from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django_common.auth_backends import User
from django.forms import ModelForm
from company.models import Campaign, Advertiser
from datetime import datetime
from django import forms


class CrmTaskGroup(models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')

    class Meta:
        verbose_name = _("Группа задач")
        verbose_name_plural = _("Группы задач")

    def __str__(self):
        return self.title


class CrmTask(models.Model):
    STATUS_CHOICES = (
        (0, _("Активна")),
        (1, _("Завершена")),
    )
    title = models.CharField(_("Название"), max_length=255, default='')
    description = models.TextField(_("Описание"), blank=True, null=True)
    task_group = models.ForeignKey(CrmTaskGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u"Группа задач")
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u"Клиент")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u"Акция")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u"Рекламодатель")
    plane_finish_date = models.DateTimeField(_("Запланированная дата выполнения"), null=True, blank=True)
    finish_date = models.DateTimeField(_("Дата выполнения"), null=True, blank=True)
    task_status = models.IntegerField(_("Статус задачи"), choices=STATUS_CHOICES, default=0)

    class Meta:
        verbose_name = _("Задача")
        verbose_name_plural = _("Задачи")

    def __str__(self):
        return self.title


class TaskForm(forms.ModelForm):
    class Meta:
        model = CrmTask
        fields = ('title', 'description', 'task_group', 'client', 'campaign', 'advertiser', 'plane_finish_date')

class TaskGroupForm(forms.ModelForm):
    class Meta:
        model = CrmTaskGroup
        fields = ('title',)


class ProjectSettings (models.Model):
    title = models.CharField(_("Название"), max_length=255, default='')
    dogovor = models.FileField(_("Договор оферты"), upload_to='uploads/')
    soglasie = models.FileField(_("Пользовательское соглашение"), upload_to='uploads/')

    class Meta:
        verbose_name = _("Настройка")
        verbose_name_plural = _("Настройки")

    def __str__(self):
        return self.title
