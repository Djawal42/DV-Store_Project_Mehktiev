from django import forms
from django.utils.html import strip_tags


    # ОБЯЗАТЕЛЬНЫЕ ПОЛЯ 
    
class OrderForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        label="Имя",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        label="Фамилия",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Фамилия'
        })
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Email',
            'readonly': 'readonly'
        })
    )

    # НЕОБЯЗАТЕЛЬНЫЕ ПОЛЯ
    
    company = forms.CharField(
        max_length=100,
        required=False,
        label="Компания",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Компания (необязательно)'
        })
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        label="Адрес",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black pr-10',
            'placeholder': 'Адрес'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        label="Город",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Город'
        })
    )
    
    country = forms.CharField(
        max_length=100,
        required=False,
        label="Страна",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Страна'
        })
    )
    
    province = forms.CharField(
        max_length=100,
        required=False,
        label="Регион",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Регион'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        label="Почтовый индекс",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black',
            'placeholder': 'Почтовый индекс'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        label="Телефон",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-black rounded-none text-black placeholder-gray-500 focus:outline-none focus:border-black pr-10',
            'placeholder': 'Телефон (необязательно)'
        })
    )


    # МЕТОДЫ

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['company'].initial = user.company
            self.fields['address'].initial = user.address
            self.fields['city'].initial = user.city
            self.fields['country'].initial = user.country
            self.fields['province'].initial = user.province
            self.fields['postal_code'].initial = user.postal_code
            self.fields['phone'].initial = user.phone


    def clean(self):
        cleaned_data = super().clean()
        for field in ['company', 'address', 'city', 'country', 
                      'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data
    