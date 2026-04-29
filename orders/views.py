from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from yookassa import Payment, Configuration
from uuid import uuid4
import json
import logging

from .forms import OrderForm
from .models import Order, OrderItem
from cart.views import CartMixin
from cart.models import Cart

logger = logging.getLogger(__name__)

# ЮKassa конфигурация
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class CheckoutView(CartMixin, View):

    def get(self, request):
        cart = self.get_cart(request)

        if cart.total_items == 0:
            return redirect('main:index')

        form = OrderForm(user=request.user)

        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.select_related('product'),
            'total_price': cart.subtotal,
        }

        # Если это HTMX-запрос — возвращаем только контент
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/checkout_content.html', context)
        # Обычный GET-запрос — отдаём полную страницу
        return render(request, 'orders/checkout.html', context)


    @transaction.atomic
    def post(self, request):
        cart = self.get_cart(request)

        if cart.total_items == 0:
            return redirect('main:index')

        form = OrderForm(request.POST, user=request.user)

        if not form.is_valid():
            context = {
                'form': form,
                'cart': cart,
                'cart_items': cart.items.select_related('product'),
                'total_price': cart.subtotal,
            }
            # При ошибке валидации возвращаем контент (HTMX) или полную страницу
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/checkout_content.html', context)
            return render(request, 'orders/checkout.html', context)

        # Создание заказа
        order = Order.objects.create(
            user=request.user,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            company=form.cleaned_data['company'],
            address=form.cleaned_data['address'],
            city=form.cleaned_data['city'],
            country=form.cleaned_data['country'],
            province=form.cleaned_data['province'],
            postal_code=form.cleaned_data['postal_code'],
            phone=form.cleaned_data['phone'],
            total_price=cart.subtotal,
            status='pending',
            payment_provider='yookassa',
            cart_id=cart.id
        )

        # Создаем позиции заказа
        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        payment = self.create_yookassa_payment(order, request)
        redirect_url = payment.confirmation.confirmation_url

        if request.headers.get('HX-Request'):
            response = HttpResponse(status=200)
            response['HX-Redirect'] = redirect_url
            return response
        return redirect(redirect_url)


    def create_yookassa_payment(self, order, request):

        receipt_items = []

        for item in order.items.all():
            receipt_items.append({
                "description": item.product.name,
                "quantity": str(item.quantity),
                "amount": {
                    "value": f"{item.price:.2f}",
                    "currency": "RUB"
                },
                "vat_code": 1,
                "payment_mode": "full_payment",
                "payment_subject": "commodity"
            })

        idempotence_key = str(uuid4())

        payment = Payment.create({
            "amount": {
                "value": f"{order.total_price:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(
                    f'/orders/yookassa/success/?order_id={order.id}'
                )
            },
            "capture": True,
            "description": f"Заказ №{order.id}",
            "metadata": {
                "order_id": order.id,
                "user_id": order.user.id
            },
            "receipt": {
                "customer": {
                    "email": order.email
                },
                "items": receipt_items
            }
        }, idempotence_key)

        order.yookassa_payment_id = payment.id
        order.save()

        return payment
    
class YookassaSuccessView(TemplateView):
    template_name = 'orders/yookassa_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.GET.get('order_id')
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=self.request.user)
            context['order'] = order

            # Очищаем корзину, если она ещё существует
            if order.cart_id:
                cart = Cart.objects.filter(id=order.cart_id).first()
                if cart:
                    cart.clear()
                # Обнуляем cart_id в заказе, чтобы не пытаться очистить повторно
                order.cart_id = None
                order.save(update_fields=['cart_id'])

        return context

@csrf_exempt
@require_POST
def yookassa_webhook(request):

    try:
        event_json = json.loads(request.body.decode('utf-8'))
        event_type = event_json.get('event')
        payment = event_json.get('object', {})
        metadata = payment.get('metadata', {})

        order_id = metadata.get('order_id')
        user_id = metadata.get('user_id')

        order = Order.objects.select_for_update().get(id=order_id, user_id=user_id)

        if event_type == 'payment.succeeded':
            if order.status != 'completed':
                order.status = 'completed'
                order.save()

                # очищаем корзину
                if order.cart_id:
                    cart = Cart.objects.filter(id=order.cart_id).first()
                    if cart:
                        cart.clear()
                        order.cart_id = None
                        order.save(update_fields=['cart_id'])

        elif event_type == 'payment.canceled':
            order.status = 'cancelled'
            order.save()

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(str(e))
        return HttpResponseBadRequest()