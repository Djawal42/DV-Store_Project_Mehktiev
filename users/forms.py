from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Эл. почта'}))
    first_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Фамилия'}))
    last_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Имя'}))
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Подтвердите пароль'})
    )


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
    

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user
    

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Электронная почта", widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Эл. почта'}))
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Пароль'})
    )

     
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный пароль или электронная почта.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт неактивен.')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', "Введите корректный номер.")],
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Номер телефона'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Фамилия'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Эл. почта'})
    )


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company', 
                  'address1', 'address2', 'city', 'country',
                  'province', 'postal_code', 'phone')
        widgets = {
            'company': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Компания'}),
            'address1': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Адресс 1'}),
            'address2': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Адресс 2'}),
            'city': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Город'}),
            'country': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Страна'}),
            'province': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Округ'}),
            'postal_code': forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'Индекс'}),
        }
        
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Эта почта уже используется.')
        return email
    

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email
        for field in ['company', 'address1', 'address2', 'city', 'country',
                      'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data