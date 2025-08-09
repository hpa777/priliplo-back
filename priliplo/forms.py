from django.contrib.auth.models import User
from django import forms
import re
from client.models import UserProfile

User._meta.get_field('email').__dict__['_unique'] = True

class UserRegistrationForm(forms.ModelForm):
    phone = forms.CharField(max_length=200, label=u'Телефон')
    name = forms.CharField(max_length=1000, label=u'Как к вам обращаться?')
    company_name = forms.CharField(max_length=1000, label=u'Название организации')
    account_type = forms.CharField(max_length=1000, label=u'Тип аккаунта')
    password = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=u'Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_confirm']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password_confirm']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        # parse digits from the string
        digit_list = re.findall("\d+", phone)
        phone = ''.join(digit_list)

        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Такой номер телефона уже зарегистрирован")
        return phone
