from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User

from company.models import Advertiser


class SmsCode (models.Model):
    created_date = models.DateTimeField(_("Дата создания"), auto_now_add=True, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Клиент")
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, verbose_name=u"Рекламодатель")
    balance = models.DecimalField(_("Баллов для списания"), max_digits=7, decimal_places=2, default=0)
    code = models.CharField(_("Код"), max_length=10, default="")

    class Meta:
        verbose_name = _("СМС код")
        verbose_name_plural = _("СМС коды")
        ordering = ['-created_date']

    def __str__(self):
        return self.client.username + " в " + self.advertiser.company_name + " (" + self.code + ")"
