from django.db import models
from django.utils.text import slugify

# Импорт валидаторов для  battery_health
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
    
class Product(models.Model):

    # Выбор состояния товара
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('excellent', 'Отличное'),
        ('good', 'Хорошее'),
        ('fair', 'Удовлетворительное'),
        ('poor', 'Сильно изношено'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Производитель"
    )

    # Основные меняющиеся параметры
    color = models.CharField(max_length=100, verbose_name="Цвет")
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good',
        verbose_name="Состояние"
    )

    # Складской учёт
    price = models.DecimalField(max_digits=10, decimal_places=2,
        verbose_name="Цена")
    stock = models.PositiveIntegerField(default=1,
        verbose_name="В наличии")

    # Техническая инфа
    storage = models.CharField(max_length=50, blank=True,
        verbose_name="Память")  # 128GB, 256GB
    ram = models.CharField(max_length=50, blank=True,
        verbose_name="ОЗУ")      # 8GB, 16GB
    battery_health = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Укажите состояние аккумулятора...",
        verbose_name="Здоровье аккумулятора",
        validators=[
        MinValueValidator(0),
        MaxValueValidator(100),
    ],
    )   

    description = models.TextField(blank=True, verbose_name="Описание")
    main_image = models.ImageField(upload_to='products/main/', verbose_name="Фото")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.condition})"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at'] 

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/extra/')

    def __str__(self):
        return f"Image for {self.product.name}"