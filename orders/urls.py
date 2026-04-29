from django.urls import path
from . import views
from .views import CheckoutView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('yookassa/success/', views.YookassaSuccessView.as_view(), name='yookassa_success'),
]