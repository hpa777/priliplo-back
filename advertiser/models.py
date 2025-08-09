from django.db import models
from datetime import date
from django.utils import timezone
from datetime import datetime
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from PIL import Image, ImageOps
from sorl.thumbnail import ImageField


class Advertiser (models.Model):
    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    title = models.CharField(_("Название"), max_length=255, default='')
    logo_image= ImageField(_("Логотип"), upload_to='advertiser_logo', blank=True)
    short_description = models.CharField(_("Короткое описание"), max_length=255, default='')
    full_description = models.TextField(_("Полное описание"), default='', blank=True)
    award = models.IntegerField(_("Вознаграждение"), default=0)
    num = models.IntegerField(default=0, verbose_name=u'Порядковый номер', blank=True, db_index=True)

    class Meta:
        verbose_name = _("Рекламодатель")
        verbose_name_plural = _("Рекламодатели")
        ordering = ['-num']

    def __str__(self):
        return self.title

    def campaigns_count(self):
            return self.campaign_set.count()



class Campaign (models.Model):
    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    edited_date = models.DateTimeField(_("Дата редактирования"), auto_now=True, editable=False, null=True)

    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    title = models.CharField(_("Название"), max_length=255, default='')
    campaign_image = ImageField(_("Изображение акции"), upload_to='campaign_image', blank=True)
    short_description = models.TextField(_("Короткое описание"), default='')
    award = models.IntegerField(_("Вознаграждение"), default=0)
    end_date = models.DateTimeField(_("Дата окончания акции"))

    num = models.IntegerField(default=0, verbose_name=u'Порядковый номер', blank=True, db_index=True)

    class Meta:
        verbose_name = _("Акция")
        verbose_name_plural = _("Акции")
        ordering = ['-num']

    def __str__(self):
        return self.title

