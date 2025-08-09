import decimal

from django.db import models
from datetime import date

from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
import re
from PIL import Image, ImageOps
from sorl.thumbnail import ImageField, delete
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class BusinessType(models.Model):
    parent_business_type = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name=u"Родительская категория")
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Вид деятельности")
        verbose_name_plural = _("Виды деятельности")
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_children(self):
        return BusinessType.objects.filter(parent_business_type=self.pk).order_by('title')

    def underscored_name(self):
        str_arr = self.title.split(" - ")
        return str_arr[1]

    def campaigns_count (self):
        return Campaign.objects.filter(campaign_status=2).filter(advertiser__in=Advertiser.objects.filter(business_type=self.pk)).count()

class Advertiser (models.Model):
    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    owner_user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u'Владелец', blank=False, null=True, related_name='owner_user')
    # title = models.CharField(_("Название"), max_length=255, default='', blank=True)
    # logo_image= ImageField(_("Логотип"), upload_to='advertiser_logo', blank=True)
    short_description = models.CharField(_("Короткое описание"), max_length=255, default='', blank=True)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Вид деятельности")
    # full_description = models.TextField(_("Полное описание"), default='', blank=True)

    company_phone = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Телефон')
    company_fio = models.CharField(max_length=1000, verbose_name=u'ФИО контактного лица', blank=True, default='')
    company_name = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Наименование компании')
    company_legal_name = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Юридическое лицо')
    company_inn = models.CharField(max_length=255, blank=True, default='', verbose_name=u'ИНН компании')
    kassir_login = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Логин кассира')
    kassir_password = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Пароль кассира')
    kassir_user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u'Пользователь кассир', default=None, blank=True, null=True, related_name='kassir_user_field')
    company_description = models.TextField(blank=True, default='', verbose_name=u'Описание')
    company_logo = models.ImageField(upload_to='company_logo', verbose_name=u'Логотип компании', null=True, blank=True)
    balance = models.DecimalField(_("Баланс"), max_digits=15, decimal_places=2, default=0)

    num = models.IntegerField(default=0, verbose_name=u'Порядковый номер', blank=True, db_index=True)

    class Meta:
        verbose_name = _("Рекламодатель")
        verbose_name_plural = _("Рекламодатели")
        ordering = ['num']

    def __str__(self):
        return self.company_name

    def get_full_company_fio(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if self.company_fio != '':
            full_name = '%s' % (self.company_fio)

        else:
            full_name = self.owner_user.username

        return full_name.strip()

    def campaigns_count(self):
            return self.campaign_set.filter(campaign_status=2).count()

    def profile_filled(self):
        return self.company_fio != '' and self.company_phone != '' and self.company_name != '' and self.company_legal_name != '' and self.company_inn != '' and self.company_description != '' 


class AdvertiserSettings (models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')
    sticking_cost = models.DecimalField(_("Стоимость оклейки"), max_digits=15, decimal_places=2, default=0)
    period_cost = models.DecimalField(_("Стоимость периода"), max_digits=15, decimal_places=2, default=0)
    logo_cost = models.DecimalField(_("Стоимость подготовки логотипа"), max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Настройка")
        verbose_name_plural = _("Настройки")

    def __str__(self):
        return self.title


class Campaign (models.Model):
    CAMPAIGN_STATUS_CHOICES = (
        (0, _("Нет")),
        (1, _("На одобрении")),
        (2, _("Активна")),
        (3, _("Отклонена")),
        (4, _("Завершена")),
        (5, _("Удалена")),
    )

    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    campaign_status = models.IntegerField(_("Статус акции"), choices=CAMPAIGN_STATUS_CHOICES, default=0)
    admin_comment = models.TextField(_("Комментарий администратора"), default='', blank=True)
    title = models.CharField(_("Название"), max_length=255, default='')
    logo_image = ImageField(_("Логотип акции"), upload_to='logo_campaign_image', blank=True)
    campaign_image = ImageField(_("Изображение акции"), upload_to='campaign_image', blank=True)
    short_description = models.TextField(_("Короткое описание"), default='')
    sticker_text = models.TextField(_("Текст наклейки"), default='')
    award = models.IntegerField(_("Вознаграждение"), default=0)
    quota = models.IntegerField(_("Квота участников"), default=1)
    end_date = models.DateTimeField(_("Дата окончания акции"))
    approve_date = models.DateField(_("Дата одобрения акции"), default=None, blank=True, null=True)
    campaign_balance = models.DecimalField(_("Баланс акции"), max_digits=15, decimal_places=2, default=0)

    num = models.IntegerField(default=0, verbose_name=u'Порядковый номер', blank=True, db_index=True)

    class Meta:
        verbose_name = _("Акция")
        verbose_name_plural = _("Акции")
        ordering = ['-num']

    def __str__(self):
        return self.title

    def all_applications_count(self):
        return self.campaignapplication_set.count()

    def active_applications_count(self):
        return self.campaignapplication_set.filter(application_status=2).count()

    def request_applications_count(self):
        return self.campaignapplication_set.filter(application_status=1).count()

    def sticker_applications_count(self):
        return self.campaignapplication_set.filter(application_status=5).count()

    def finished_applications_count(self):
        return self.campaignapplication_set.filter(application_status=7).count()

    def get_active_applications(self):
        return self.objects.filter(application_status=2)

    def get_applications_quota(self):
        return self.quota - self.campaignapplication_set.filter(Q(application_status=1) | Q(application_status=2) | Q(application_status=5) | Q(application_status=7)).count()


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        # fields = ('title', 'short_description', 'award', 'quota', 'end_date', 'campaign_image')
        fields = ('title', 'short_description', 'award', 'quota', 'end_date', 'logo_image', 'sticker_text')


class CampaignBalanceHistory (models.Model):
    CHANGE_TYPE_CHOICES = (
        (0, _("Прочее")),
        (1, _("Корректировка")),
        (2, _("Отрицательная корректировка")),
        (3, _("Пополнение при создании акции")),
        (4, _("Возврат не использованных средств на баланс рекламодателя")),
        (5, _("Ежемесячное списание за пройденный период")),
    )

    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name=u"Акция")
    balance_increase = models.DecimalField(_("Приход"), max_digits=9, decimal_places=2, default=0)
    balance_decrease = models.DecimalField(_("Расход"), max_digits=9, decimal_places=2, default=0)
    balance_before = models.DecimalField(_("Баланс до корректировки"), max_digits=9, decimal_places=2, default=0)
    balance_current = models.DecimalField(_("Баланс после корректировки"), max_digits=9, decimal_places=2, default=0)
    edited_date = models.DateTimeField(auto_now=True, verbose_name=u'Дата', editable=False, null=True)
    history_description = models.CharField(_("Описание"), max_length=1000, blank=True)
    change_type = models.IntegerField(_("Тип"), choices=CHANGE_TYPE_CHOICES, default=0)

    def __str__(self):
        return u"%s [%s]" % (self.advertiser, self.get_change_type_display())

    class Meta:
        verbose_name = _("История баланса акции")
        verbose_name_plural = _("Изменения баланса акции")
        ordering = ['-edited_date']

@receiver(post_save, sender=CampaignBalanceHistory)
def post_save_handler_campaign_balance(sender, instance, **kwargs):
    related_name_campaign = instance.campaign
    related_name_campaign.campaign_balance += decimal.Decimal(instance.balance_increase)
    related_name_campaign.campaign_balance -= decimal.Decimal(instance.balance_decrease)
    related_name_campaign.save()

    current_balance = related_name_campaign.campaign_balance
    CampaignBalanceHistory.objects.filter(pk=instance.pk).update(balance_current=current_balance)

@receiver(pre_save, sender=CampaignBalanceHistory)
def pre_save_handler_campaign_balance(sender, instance, **kwargs):
    related_name_campaign = instance.campaign
    current_balance = related_name_campaign.campaign_balance
    instance.balance_before = current_balance


class CompanyProfileForm(forms.ModelForm):
    image_remove = forms.BooleanField(required=False)

    class Meta:
        model = Advertiser
        fields = ('company_fio', 'company_phone', 'company_name', 'company_legal_name', 'company_inn', 'company_description', 'company_logo', 'kassir_login', 'kassir_password', 'image_remove', 'business_type')

    def __init__(self, *args, **kwargs):
        super(CompanyProfileForm, self).__init__(*args, **kwargs)
        self.fields['company_fio'].required = True
        self.fields['company_phone'].required = True
        self.fields['company_name'].required = True
        self.fields['company_legal_name'].required = True
        self.fields['company_inn'].required = True
        self.fields['company_description'].required = True
        # self.fields['short_description'].required = True
        self.fields['business_type'].required = True
        self.fields['kassir_login'].required = True
        self.fields['kassir_password'].required = True

    def clean_company_phone(self):
        phone = self.cleaned_data.get("company_phone")
        # parse digits from the string
        digit_list = re.findall("\d+", phone)
        phone = ''.join(digit_list)
        return phone

    def save(self, commit=True):
        instance = super(CompanyProfileForm, self).save(commit=False)
        if self.cleaned_data.get('image_remove'):
            try:
                # if os.path.isfile(instance.company_logo.path):
                delete(instance.company_logo)
                # os.unlink(instance.company_logo.path)
            except OSError:
                pass
            instance.company_logo = None
        if commit:
            instance.save()
        return instance


class Order (models.Model):
    PAYMENT_METHOD_CHOICES = (
        (0, _("Нет")),
        (1, _("Robokassa")),
    )
    ORDER_STATUS_CHOICES = (
        (0, _("Нет")),
        (1, _("Новый")),
        (2, _("Оплачен")),
        (3, _("Отказ")),
        (4, _("Ошибка")),
    )

    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    payment_method = models.IntegerField(_("Способ оплаты"), choices=PAYMENT_METHOD_CHOICES, blank=True, default=0)
    order_status = models.IntegerField(_("Статус счета"), choices=ORDER_STATUS_CHOICES, blank=True, default=0)
    summ = models.DecimalField(_("Сумма"), max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Пополнение баланса")
        verbose_name_plural = _("Пополнение баланса")
        ordering = ['-edited_date']


class Billing_history (models.Model):
    CHANGE_TYPE_CHOICES = (
        (0, _("Прочее")),
        (1, _("Корректировка")),
        (2, _("Отрицательная корректировка")),
        (3, _("Пополнение баланса")),
        (4, _("Списание за создание акции")),
        (5, _("Возврат не использованных средств")),
    )

    # user = models.ForeignKey(User, default=2, on_delete=models.CASCADE)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    balance_increase = models.DecimalField(_("Приход"), max_digits=9, decimal_places=2, default=0)
    balance_decrease = models.DecimalField(_("Расход"), max_digits=9, decimal_places=2, default=0)
    balance_before = models.DecimalField(_("Баланс до корректировки"), max_digits=9, decimal_places=2, default=0)
    balance_current = models.DecimalField(_("Баланс после корректировки"), max_digits=9, decimal_places=2, default=0)
    edited_date = models.DateTimeField(auto_now=True, verbose_name=u'Дата', editable=False, null=True)
    history_description = models.CharField(_("Описание"), max_length=1000, blank=True)
    change_type = models.IntegerField(_("Тип"), choices=CHANGE_TYPE_CHOICES, default=0)

    def __str__(self):
        # return self.get_change_type_display()
        return u"%s [%s]" % (self.advertiser, self.get_change_type_display())

    class Meta:
        verbose_name = _("История баланса компаний")
        verbose_name_plural = _("Изменения баланса компаний")
        ordering = ['-edited_date']

@receiver(post_save, sender=Billing_history)
def post_save_handler(sender, instance, **kwargs):
    # print('----------- post save callback --------------')
    # print(instance.advertiser)
    # print(instance.advertiser.balance)

    related_name_user = instance.advertiser

    related_name_user.balance += decimal.Decimal(instance.balance_increase)
    related_name_user.balance -= decimal.Decimal(instance.balance_decrease)
    related_name_user.save()

    current_balance = related_name_user.balance

    Billing_history.objects.filter(pk=instance.pk).update(balance_current=current_balance)
    # instance.current_balance = current_balance
    # instance.save()

@receiver(pre_save, sender=Billing_history)
def pre_save_handler(sender, instance, **kwargs):
    related_name_user = instance.advertiser
    current_balance = related_name_user.balance
    instance.balance_before = current_balance
