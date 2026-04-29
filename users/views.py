from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser
from main.models import Product, Category
from django.views.generic import TemplateView, DetailView
from orders.models import Order

class OrderHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'users/partials/order_history.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        return context

    def get(self, request, *args, **kwargs):
        if not request.headers.get('HX-Request'):
            return redirect('users:profile')
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, self.template_name, context)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'users/partials/order_detail.html'
    pk_url_kwarg = 'order_id'
    login_url = '/users/login/'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        if not request.headers.get('HX-Request'):
            return redirect('users:profile')
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, self.template_name, context)
        
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}

    # Если HTMX — возвращаем только контент
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'users/register_content.html', context)

    # Если обычный запрос — полный layout
    return render(request, 'users/register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:index')
    else:
        form = CustomUserLoginForm()

    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'users/login_content.html', {'form': form})

    return render(request, 'users/login.html', {'form': form})
    

@login_required(login_url='/users/login')
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    recommended_products = Product.objects.all().order_by('id')[:3]
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()

    context = {
        'form': form,
        'user': request.user,
        'recommended_products': recommended_products,
        'latest_order': latest_order,
        'categories': Category.objects.all(),
    }

    # Проверяем HTMX
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'users/profile_content.html', context)

    return TemplateResponse(request, 'users/profile.html', context)


@login_required(login_url='/users/login')
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html', {'user': user})


@login_required(login_url='/users/login')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/partials/edit_account_details.html',
                            {'user': request.user, 'form': form})


@login_required(login_url='/users/login')
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form': form})
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('user:profile')})
    return redirect('users:profile')


def logout_view(request):
    if request.method == 'POST' or request.headers.get('HX-Request'):
        auth_logout(request)
        response = HttpResponse(status=200)
        response['HX-Redirect'] = reverse('users:login')
        # Очищаем сессию полностью
        request.session.flush()
        return response

    auth_logout(request)
    request.session.flush()
    return redirect('main:index')