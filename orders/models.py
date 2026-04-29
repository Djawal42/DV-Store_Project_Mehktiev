from django.db import models
from django.conf import settings
from main.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='orders',
    verbose_name="Пользователь"
    )

    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    email = models.EmailField(max_length=254, verbose_name="Email")
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Компания")
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name="Регион")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Почтовый индекс")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    special_instructions = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    payment_provider = models.CharField(max_length=20, null=True, blank=True, verbose_name="Способ оплаты")
    yookassa_payment_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID платежа ЮKassa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    cart_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID корзины")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, 
        verbose_name="Цена"
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    

    def get_total_price(self):
        return self.price * self.quantity
    