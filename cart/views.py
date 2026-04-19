from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.db import transaction
from main.models import Product
from .models import Cart, CartItem


class CartMixin:
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart


class CartModalView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal.html', context)


class AddToCartView(CartMixin, View):
    @transaction.atomic
    def post(self, request, slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)

        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({'error': ''}, status=400)

        if product.stock < quantity:
            return JsonResponse({
                'error': f'В наличии только {product.stock} шт!'
            }, status=400)

        existing_item = cart.items.filter(product=product).first()

        if existing_item:
            total_quantity = existing_item.quantity + quantity
            if total_quantity > product.stock:
                return JsonResponse({
                    'error': f"В наличии только {product.stock - existing_item.quantity} шт!"
                }, status=400)
            existing_item.quantity = total_quantity
            existing_item.save()
            cart_item = existing_item
        else:
            cart_item = cart.add_product(product, quantity)

        if request.headers.get('HX-Request'):
            return redirect('cart:cart_modal')

        return JsonResponse({
            'success': True,
            'total_items': cart.total_items,
            'message': f"{product.name} в корзине!",
            'cart_item_id': cart_item.id
        })


class UpdateCartItemView(CartMixin, View):
    @transaction.atomic
    def post(self, request, item_id):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = int(request.POST.get('quantity', 1))

        if quantity < 0:
            return JsonResponse({'error': 'Неверное количество'}, status=400)

        if quantity == 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'error': f'К сожалению, доступно не более {cart_item.product.stock} штук'
                }, status=400)

            cart_item.quantity = quantity
            cart_item.save()

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').order_by('-added_at')
        }

        return TemplateResponse(request, 'cart/cart_modal.html', context)


class RemoveCartItemView(CartMixin, View):
    def post(self, request, item_id):
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()

            context = {
                'cart': cart,
                'cart_items': cart.items.select_related('product').order_by('-added_at')
            }

            return TemplateResponse(request, 'cart/cart_modal.html', context)

        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Товар не найден'}, status=400)


class CartCountView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal)
        })


class ClearCartView(CartMixin, View):
    def post(self, request):
        cart = self.get_cart(request)
        cart.clear()

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_empty.html', {
                'cart': cart
            })

        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена'
        })


class CartSummaryView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_summary.html', context)