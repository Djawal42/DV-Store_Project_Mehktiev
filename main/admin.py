from django.contrib import admin
from .models import Category, Brand, Product, ProductImage

admin.site.site_header = "D&V STORE"
admin.site.site_title = "D&V STORE Администрирование"
admin.site.index_title = "Панель управления"


# Встроенные дополнительные изображения
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Админка товара
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'category',
        'condition',
        'price',
        'stock',
        'created_at',
    )

    list_filter = (
        'brand',
        'category',
        'condition',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
        'brand__name',
    )

    prepopulated_fields = {'slug': ('name',)}

    inlines = [ProductImageInline]

    readonly_fields = ('created_at', 'updated_at')


# Категории
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


# Бренды
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}