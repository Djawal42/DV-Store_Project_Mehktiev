from django.shortcuts import get_object_or_404              # Классовое представление 
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Category, Product, Brand
from django.db.models import Q

# Главная страничка
class IndexView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        context['products'] = Product.objects.order_by('-created_at')[:8]   # SQL-запрос  LIMIT 8
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)
    
# Каталог
class CatalogView(TemplateView):
    template_name = 'main/base.html'

    # Вместо If Else (Компактнее, удобнее)
    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'brand': lambda queryset, value: queryset.filter(brand__slug=value),
        'condition': lambda queryset, value: queryset.filter(condition=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        'min_battery': lambda queryset, value: queryset.filter(battery_health__gte=value),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        brands = Brand.objects.all()

        # 1 JOIN-запрос вместо множества SQL запросов
        products = Product.objects.select_related(
            'category', 'brand'
        ).order_by('-created_at')

        current_category = None

        # Фильтр по категории
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        # Поиск
        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query)
            )

        # Универсальные фильтры
        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''

        filter_params['q'] = query or ''

        available_colors = Product.objects.values_list(
            'color', flat=True
        ).distinct().order_by('color')

        available_brands = Brand.objects.filter(
            products__isnull=False
        ).distinct().order_by('name')

        context.update({
            'categories': categories,
            'brands': brands,
            'products': products,
            'current_category': current_category,
            'current_category_slug': current_category.slug if current_category else None,
            'filter_params': filter_params,
            'search_query': query or '',
            'available_colors': available_colors,
            'available_brands': available_brands,
        })

        # Отделяем поиск от каталога
        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True
        
        return context
    

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            if context.get('show_search'):
                return TemplateResponse(request, 'main/search_input.html', context)
            elif context.get('reset_search'):
                return TemplateResponse(request, 'main/search_button.html', {})
            template = 'main/filter_modal.html' if request.GET.get('show_filters') == 'true' else 'main/catalog.html'
            return TemplateResponse(request, template, context)
        return TemplateResponse(request, self.template_name, context)
    
class ReturnPolicyView(TemplateView):
    template_name = 'orders/return_policy.html'

# Детальная страница товара
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        # Если HTMX — возвращаем только content
        if request.headers.get('HX-Request'):
            return TemplateResponse(
                request,
                'main/product_detail_content.html',
                context
            )

        # Если обычный переход — возвращаем полный layout
        return TemplateResponse(
            request,
            self.template_name,
            context
        )