from django.db import models
from django.utils.text import slugify

# Создаю категории для группировки товаров

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Product(models.Model):

    # Выбор состояния товара
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('excellent', 'Отличное'),
        ('good', 'Хорошее'),
        ('fair', 'Удовлетворительное'),
        ('poor', 'Сильно изношено'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )

    # Основные меняющиеся параметры
    color = models.CharField(max_length=100)
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good'
    )

    # Складской учёт
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)

    # Техническая инфа
    storage = models.CharField(max_length=50, blank=True)  # 128GB, 256GB
    ram = models.CharField(max_length=50, blank=True)      # 8GB, 16GB
    battery_health = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Ввелите состояние аккумулятора в %"
    )

    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products/main/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.condition})"

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/extra/')

    def __str__(self):
        return f"Image for {self.product.name}"