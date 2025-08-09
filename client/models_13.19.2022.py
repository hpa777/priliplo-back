import os
from django.db import models
from datetime import date
from django.utils import timezone
from datetime import datetime
from django.utils.translation import ugettext_lazy as _, ugettext
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from PIL import Image, ImageOps
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import re
from sorl.thumbnail import delete
from company.models import Campaign, Advertiser
from django.conf import settings
from webpush import send_user_notification


class Country(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Страна")
        verbose_name_plural = _("Страны")

    def __str__(self):
        return self.title


class City(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, verbose_name=u"Страна")

    class Meta:
        verbose_name = _("Город")
        verbose_name_plural = _("Города")

    def __str__(self):
        return self.title


class District(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, verbose_name=u"Город")

    class Meta:
        verbose_name = _("Район")
        verbose_name_plural = _("Районы")

    def __str__(self):
        return self.title


class Odometer(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Период пробегов")
        verbose_name_plural = _("Периоды пробегов")

    def __str__(self):
        return self.title


class AutoType(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Тип транспортного средства")
        verbose_name_plural = _("Типы транспортных средств")

    def __str__(self):
        return self.title


class AutoMarka(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Марка транспортного средства")
        verbose_name_plural = _("Марки транспортных средств")
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_models(self):
        return AutoModel.objects.filter(marka=self.pk).all()

class AutoModel(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')
    marka = models.ForeignKey(AutoMarka, on_delete=models.CASCADE, blank=True, verbose_name=u"Марка")

    class Meta:
        verbose_name = _("Модель транспортного средства")
        verbose_name_plural = _("Модели транспортных средств")
        ordering = ['title']

    def __str__(self):
        return self.title


# User._meta.get_field('email')._unique = False
# User._meta.get_field('email')._editable = False


class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        (0, _("Нет")),
        (1, _("Администратор")),
        (2, _("Клиент")),
        (3, _("Рекламодатель")),
        (4, _("Кассир")),
    )

    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    user_role = models.IntegerField(_("Роль пользователя"), choices=USER_TYPE_CHOICES, default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=200, blank=True, unique=True, default='', verbose_name=u'Телефон')
    # user_email = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Email')
    # last_name = models.CharField(max_length=1000, verbose_name=u'Фамилия', blank=True, default='')
    name = models.CharField(max_length=1000, verbose_name=u'Как к вам обращаться?', blank=True, default='')
    # surname_name = models.CharField(max_length=1000, verbose_name=u'Отчество', blank=True, default='')
    # automarka = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Марка автомобиля')
    # automodel = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Модель автомобиля')

    auto_marka = models.ForeignKey(AutoMarka, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Марка автомобиля")
    auto_model = models.ForeignKey(AutoModel, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Модель автомобиля")
    auto_markamodel_other = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Марка и модель автомобиля')

    autogv = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Год выпуска автомобиля')
    autonumber = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Гос номер автомобиля')

    auto_type = models.ForeignKey(AutoType, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name=u"Тип транспортного средства")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Страна")
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u"Город")
    district = models.ManyToManyField(District, blank=True, verbose_name=u"Районы присутствия")
    odometer = models.ForeignKey(Odometer, on_delete=models.CASCADE, blank=True, null=True,
                                 verbose_name=u"Пробег в месяц")
    auto_sideview = models.ImageField(upload_to='auto_sideview', verbose_name=u'Общий вид автомобиля', null=True, blank=True)
    auto_rearview = models.ImageField(upload_to='auto_rearview', verbose_name=u'Вид автомобиля сзади', null=True, blank=True)
    loaded_rsainfo_attempts = models.IntegerField(_("Количество попыток запроса информации из ГИБДД"), default=0, blank=True, null=True)

    # def save(self):
    #     super().save()
    #     try:
    #         img = Image.open(self.avatar.path)
    #         if img.height > 100 or img.width > 100:
    #             output_size = (100, 100)
    #             img.thumbnail(output_size, Image.ANTIALIAS)
    #             img=ImageOps.fit(img, (100, 100), method=3, bleed=0.0, centering=(0.5, 0.5))
    #             img.save(self.avatar.path)
    #     except:
    #         pass

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        # if self.name != '' or self.surname_name != '' or self.last_name != '':
        #     full_name = '%s %s %s' % (self.name, self.surname_name, self.last_name)
        if self.name != '':
            full_name = '%s' % (self.name)

        else:
            full_name = self.user.username

        return full_name.strip()

    def get_balance(self):
        pass

    def profile_filled(self):
        return self.phone != '' and self.name != '' and self.auto_marka is not None and self.auto_model is not None and self.autogv != '' and self.autonumber != '' and self.auto_type is not None and self.country is not None and self.city is not None and self.district is not None and self.odometer is not None


# @receiver(pre_save, sender=User)
# def email_to_username(sender, instance, *args, **kwargs):
#     instance.username = instance.email



class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_phone = models.CharField(max_length=200, blank=True, default='', verbose_name=u'Телефон')
    company_fio = models.CharField(max_length=1000, verbose_name=u'ФИО контактного лица', blank=True, default='')
    company_name = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Наименование компании')
    company_inn = models.CharField(max_length=255, blank=True, default='', verbose_name=u'ИНН компании')
    kassir_login = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Логин кассира')
    kassir_password = models.CharField(max_length=255, blank=True, default='', verbose_name=u'Пароль кассира')
    company_description = models.TextField(blank=True, default='', verbose_name=u'Описание')
    company_logo = models.ImageField(upload_to='company_logo', verbose_name=u'Логотип компании', null=True, blank=True)

    def get_full_company_fio(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if self.company_fio != '':
            full_name = '%s' % (self.company_fio)

        else:
            full_name = self.user.username

        return full_name.strip()




class PhotoAutoGeneralView(models.Model):
    file_general_view = models.ImageField(upload_to='photo_auto_general_view',
                                          verbose_name=u'Фото общего вида автомобиля', null=True, blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, verbose_name=u"Пользователь")

    class Meta:
        verbose_name = _("Фотография общего вида")
        verbose_name_plural = _("Фотографии общего вида")

    def __str__(self):
        return self.user_profile


class PhotoAutoRearView(models.Model):
    file_rear_view = models.ImageField(upload_to='photo_auto_rear_view', verbose_name=u'Фото автомобиля сзади',
                                       null=True, blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, verbose_name=u"Пользователь")

    class Meta:
        verbose_name = _("Фотография автомобиля сзади")
        verbose_name_plural = _("Фотографии автомобиля сзади")

    def __str__(self):
        return self.user_profile


class ClientBalance(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Клиент")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.SET_NULL, null=True, default=None, verbose_name=u"Рекламодатель")
    balance = models.DecimalField(_("Баланс баллов"), max_digits=7, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Баланс клиента")
        verbose_name_plural = _("Балансы клиентов")

    def __str__(self):
        return self.client.username


class ClientBalanceHistory(models.Model):
    CHANGE_TYPE_CHOICES = (
        (0, _("Прочее")),
        (1, _("Корректировка")),
        (2, _("Отрицательная корректировка")),
        (3, _("Пополнение баллов")),
        (4, _("Списание за услугу или товар")),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Клиент")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, default=None, blank=True, verbose_name=u"Акция")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.SET_NULL, null=True, default=None, verbose_name=u"Рекламодатель")

    balance_increase = models.DecimalField(_("Приход"), max_digits=7, decimal_places=2, default=0)
    balance_decrease = models.DecimalField(_("Расход"), max_digits=7, decimal_places=2, default=0)
    balance_before = models.DecimalField(_("Баллов до корректировки"), max_digits=7, decimal_places=2, default=0)
    balance_current = models.DecimalField(_("Баллов после корректировки"), max_digits=7, decimal_places=2, default=0)
    edited_date = models.DateTimeField(auto_now=True, verbose_name=u'Дата', editable=False, null=True)
    history_description = models.CharField(_("Описание"), max_length=1000, blank=True)
    change_type = models.IntegerField(_("Тип"), choices=CHANGE_TYPE_CHOICES, default=0)

    class Meta:
        verbose_name = _("Движение баллов на балансе клиента")
        verbose_name_plural = _("Движения баллов на балансе клиента")

    def __str__(self):
        return self.client.username


@receiver(post_save, sender=ClientBalanceHistory)
def post_save_handler(sender, instance, **kwargs):
    print('----------- post save callback --------------')
    print(instance.client)
    print(instance.client.clientbalance_set.filter(client=instance.client, advertiser=instance.advertiser).first())

    related_name_user = instance.client
    balance_model = related_name_user.clientbalance_set.filter(client=instance.client, advertiser=instance.advertiser).first()

    balance_model.balance += instance.balance_increase
    balance_model.balance -= instance.balance_decrease
    balance_model.save()

    current_balance = balance_model.balance

    ClientBalanceHistory.objects.filter(pk=instance.pk).update(balance_current=current_balance)


@receiver(pre_save, sender=ClientBalanceHistory)
def pre_save_handler(sender, instance, **kwargs):
    related_name_user = instance.client
    if not related_name_user.clientbalance_set.filter(client=instance.client, advertiser=instance.advertiser).first():
        client_balance = ClientBalance.objects.create(
            client=related_name_user,
            advertiser=instance.advertiser,
            balance=0.0
        )
    current_balance = related_name_user.clientbalance_set.filter(client=instance.client, advertiser=instance.advertiser).first().balance
    instance.balance_before = current_balance


class CampaignApplication(models.Model):  # заявка на участие в акции
    APPLICATION_STATUS_CHOICES = (
        (0, _("Нет")),
        (1, _("На одобрении")),
        (2, _("Одобрена")),
        (3, _("Отклонена")),
        (4, _("Отстранен от участия")),
        (5, _("На оклейке")),
        (6, _("Отказался от участия после оклейки")),
        (7, _("Баллы перечислены на счет")),
        (8, _("Отказался от участия до оклейки")),
    )

    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, null=True)

    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Клиент")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, verbose_name=u"Акция")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.SET_NULL, null=True, verbose_name=u"Рекламодатель")
    application_status = models.IntegerField(_("Статус заявки"), choices=APPLICATION_STATUS_CHOICES, default=0)
    description = models.TextField(_("Описание"), default='', blank=True)
    approve_date = models.DateField(_("Дата приема заявки"), blank=True, null=True)
    sticker_reserve_date = models.DateTimeField(_("Бронь времени на оклейку машины"), null=True, blank=True)
    admin_comment = models.TextField(_("Комментарий администратора для себя"), default='', blank=True)


    class Meta:
        verbose_name = _("Заявка в акцию")
        verbose_name_plural = _("Заявки в акции")
        ordering = ['-created_date']

    def __str__(self):
        return self.client.username + " в " + self.campaign.title + " (" + self.campaign.advertiser.company_name + ")"

    def get_photoreports(self):
        return self.photoreport_set.filter(photoreport_status=2).order_by('created_date')


class PhotoReport(models.Model):  # фотоотчет
    PHOTOREPORT_STATUS_CHOICES = (
        (0, _("Нет")),
        (1, _("На одобрении")),
        (2, _("Одобрен")),
        (3, _("Отклонен")),
    )
    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, null=True)

    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Клиент")
    odometer = models.IntegerField(_("Текущий пробег"), default=0)
    photoreport_odometer = models.ImageField(upload_to='photoreport_odometer', verbose_name=u'Фотография одометра')
    photoreport_sticker = models.ImageField(upload_to='photoreport_sticker', verbose_name=u'Фотография наклейки')
    photoreport_status = models.IntegerField(_("Статус отчета"), choices=PHOTOREPORT_STATUS_CHOICES, blank=True, default=0)
    application = models.ForeignKey(CampaignApplication, on_delete=models.SET_NULL, null=True, verbose_name=u"Заявка")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, verbose_name=u"Акция")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.SET_NULL, null=True, verbose_name=u"Рекламодатель")
    description = models.TextField(_("Описание"), default='', blank=True)

    class Meta:
        verbose_name = _("Фото отчет")
        verbose_name_plural = _("Фото отчеты")
        ordering = ['-created_date']

    def __str__(self):
        try:
            return self.client.username + " в " + self.campaign.title + " (" + self.campaign.advertiser.company_name + ")"
        except:
            return self.client.username

    def accept(self):
        # Клиентам участвующим в акции закинуть баллы на баланс
        print("client_balance_history START")
        client_balance_history = ClientBalanceHistory.objects.create(
            client=self.client,
            campaign=self.campaign,
            advertiser=self.advertiser,
            balance_increase=self.campaign.award,
            change_type=3
        )
        print("client_balance_history OK")
        self.photoreport_status = 2
        self.save()
        # if PhotoReport.objects.filter(advertiser=self.advertiser, photoreport_status=2).count() >= 6:
        if PhotoReport.objects.filter(application=self.application, photoreport_status=2).count() > 6:
            campaign = CampaignApplication.objects.get(id=self.application.pk)
            campaign.application_status = 7
            campaign.save()

        send_user_notification(user=self.client, payload={"head": "Фотоотчеты", "body": "Ваш фотоотчет в сервисе priliplo.ru принят рекламодателем!"}, ttl=1000)

    def decline(self, note=''):
        self.photoreport_status = 3
        if note != '':
            self.description = note
        self.save()
        send_user_notification(user=self.client, payload={"head": "Фотоотчет отклонен", "body": "Ваш фотоотчет в сервисе priliplo.ru отклонен рекламодателем! Ознакомьтесь с недостатками и устраните их."}, ttl=1000)


class PhotoReportForm(forms.ModelForm):
    class Meta:
        model = PhotoReport
        fields = ('odometer', 'photoreport_odometer', 'photoreport_sticker', )

class UserProfileForm(forms.ModelForm):
    auto_sideview_image_remove = forms.BooleanField(required=False)
    # auto_rearview_image_remove = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = (
        'name', 'phone', 'auto_marka', 'auto_model', 'autogv', 'autonumber', 'auto_type',
        'country', 'city', 'district', 'odometer', 'auto_sideview', 'auto_markamodel_other')

        error_messages = {
            'auto_model': {
                'required': "Поле \"Модель автомобиля\" обязательно для заполнения",
            },
            'auto_sideview': {
                'required': "Поле \"Вид автомобиля сбоку\" обязательно для заполнения",
            },
            'auto_rearview': {
                'required': "Поле \"Вид автомобиля сзади\" обязательно для заполнения",
            },
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['phone'].required = True
        self.fields['auto_model'].required = True
        self.fields['autogv'].required = True
        self.fields['autonumber'].required = True
        self.fields['auto_type'].required = True
        self.fields['country'].required = True
        self.fields['city'].required = True
        self.fields['district'].required = True
        self.fields['odometer'].required = True
        self.fields['auto_sideview'].required = True
        # self.fields['auto_rearview'].required = True

    def clean_auto_marka(self):
        data = self.data.copy()
        if 'auto_model' in self.data and self.data['auto_model'] != '':
            data['auto_marka'] = AutoModel.objects.get(id=self.data['auto_model']).marka
        else:
            data['auto_marka'] = None

        self.data = data
        return self.data['auto_marka']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        # parse digits from the string
        digit_list = re.findall("\d+", phone)
        phone = ''.join(digit_list)
        return phone
    
    # def clean_auto_sideview(self):
    #     data = self.data.copy()
    #     if 'auto_sideview_image_remove' in self.data and self.data['auto_sideview_image_remove']=='1':
    #         data['auto_sideview'] = None
    #
    #     self.data = data
    #     print(self.data['auto_sideview_image_remove'])
    #     print(self.data['auto_sideview'])
    #     return self.data['auto_sideview']

    def save(self, commit=True):
        instance = super(UserProfileForm, self)
        instance.save(commit=False)
        # print(self.fields['name'])
        # print(self.cleaned_data.get('id'))
        # print(instance.pk)
        if self.cleaned_data.get('auto_sideview_image_remove'):
            try:
                # print(self.cleaned_data.get('auto_sideview'))
                # delete(instance.auto_sideview)
                # print(settings.MEDIA_ROOT)
                delete(settings.MEDIA_ROOT + "/" + str(self.cleaned_data.get('auto_sideview')))
                # os.remove(os.path.join(settings.MEDIA_ROOT, str(self.cleaned_data.get('auto_sideview'))))
            except OSError:
                pass
            # instance.auto_sideview = None
            # print("self.cleaned_data['auto_sideview'] = ", self.cleaned_data['auto_sideview'])
            # self.fields['auto_sideview']=None
            # print("self.data['auto_sideview'] = ", self.data['auto_sideview'])
            # self.cleaned_data['auto_sideview']=None
            # self.data['auto_sideview']=None
            # instance['auto_sideview'] = None

        if self.cleaned_data.get('auto_rearview_image_remove'):
            try:
                # delete(instance.auto_rearview)
                delete(settings.MEDIA_ROOT + "/" + str(self.cleaned_data.get('auto_rearview')))
            except OSError:
                pass
            # instance.auto_rearview = None

        if commit:
            instance.save()
        return instance
#
# class CompanyProfileForm(forms.ModelForm):
#     image_remove = forms.BooleanField(required=False)
#
#     class Meta:
#         model = CompanyProfile
#         fields = ('company_fio', 'company_phone', 'company_name', 'company_inn', 'company_description', 'company_logo', 'kassir_login', 'kassir_password', 'image_remove')
#
#     def __init__(self, *args, **kwargs):
#         super(CompanyProfileForm, self).__init__(*args, **kwargs)
#         self.fields['company_fio'].required = True
#         self.fields['company_phone'].required = True
#         self.fields['company_name'].required = True
#         self.fields['company_inn'].required = True
#         self.fields['company_description'].required = True
#         self.fields['kassir_login'].required = True
#         self.fields['kassir_password'].required = True
#
#     def save(self, commit=True):
#         instance = super(CompanyProfileForm, self).save(commit=False)
#         print("1")
#         print(self.cleaned_data)
#         if self.cleaned_data.get('image_remove'):
#             print("2")
#             # print(instance.company_logo)
#             try:
#                 # if os.path.isfile(instance.company_logo.path):
#                 delete(instance.company_logo)
#                 # os.unlink(instance.company_logo.path)
#             except OSError:
#                 pass
#             instance.company_logo = None
#         if commit:
#             instance.save()
#         return instance
