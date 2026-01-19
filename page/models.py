from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User
from company.models import Advertiser
from django.urls import resolve, reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.html import mark_safe
from django.conf import settings
from cabinet.fields import CabinetForeignKey, ForeignKeyRawIdWidget
from cabinet.models import File


class BasePage(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания', editable=False)
    edited_date = models.DateTimeField(auto_now=True, verbose_name=u'Дата редактирования', editable=False, null=True)

    class Meta:
        abstract = True


class Page(BasePage):
    """
    A page in the page tree. This is the base class that custom content types
    need to subclass.
    """

    PAGE_TYPE_CHOICES = (
        (0, _("Страница")),
        (1, _("Ссылка")),
    )

    in_menus = models.BooleanField(_("Опубликовать"), blank=True, default=True)
    title = models.CharField(_("Заголовок"), max_length=1000, default='')
    meta_description = models.CharField(_("Description"), max_length=1000, blank=True)
    meta_keywords = models.CharField(_("Keywords"), max_length=1000, blank=True)
    menu_title = models.CharField(_("Название в меню"), max_length=255, null=True, blank=True, help_text=_("Оставьте пустым для использования названия страницы"))
    slug = models.SlugField(_("Имя для url"), unique=True, blank=True, help_text=_("Только английские буквы, цифры и знаки минус и подчеркивание. <br><a id='set_main_page'>Главная страница</a>"))
    login_required = models.BooleanField(_("Требуется логин"), default=False,
                                         help_text=_("Если выбрано, то только залогиненный пользователь может просматривать страницу"))
    content = RichTextUploadingField("Текст", blank=True)
    page_type = models.IntegerField(_("Тип страницы"), choices=PAGE_TYPE_CHOICES, default=0)
    redirect_url = models.CharField(_("URL для редиректа"), max_length=1000, default='', blank=True)


    class Meta:
        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        URL for a page - for ``Link`` page types, simply return its
        slug since these don't have an actual URL pattern. Also handle
        the special case of the homepage being a page object.
        """
        slug = self.slug
        if self.page_type == 1:
            return self.redirect_url
        elif slug == "main":
            return reverse("index")
        else:
            return reverse("pagedetail", kwargs={"slug": slug})


class Slider(models.Model):
    title = models.CharField(_("Название"), max_length=512, blank=False)
    slug = models.SlugField(_("Код"), blank=False, unique=True)
    page = models.ForeignKey(Page, on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        verbose_name = _("Слайдер")
        verbose_name_plural = _("Слайдеры")

    def __str__(self):
        return self.title
    
class Slide(models.Model):
    slider = models.ForeignKey(Slider, on_delete=models.DO_NOTHING)
    title = models.CharField(_("Заголовок"), max_length=128, blank=False)
    text = models.TextField(_("Текст"), max_length=512, blank=True)
    btn_text = models.CharField(_("Текст кнопки"), blank=True, max_length=128)
    btn_url = models.CharField(_("URL кнопки"), max_length=512, blank=True)    
    
    img = CabinetForeignKey(verbose_name=_("Картинка"), 
                            related_name='slide_img_ref',
                            on_delete=models.SET_NULL, 
                            null=True, 
                            blank=False)

    
    img_mob = CabinetForeignKey(verbose_name=_("Картинка для мобильных"),
                                related_name='slide_img_mobile_ref',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True
                                )
    
    img_tablet = CabinetForeignKey(verbose_name=_("Картинка для планшетов"),
                                   related_name='slide_img_tablet_ref',
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)    

    icon = CabinetForeignKey(verbose_name=_("Иконка"),
                             related_name='slide_icon_ref',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    rank = models.IntegerField(_('Сортировка'), default=0)

    class Meta:
        verbose_name = _("Слайд")
        verbose_name_plural = _("Слайды")

    def __str__(self):
        return self.title
    def img_tag(self):                
        return mark_safe('<img src="%s%s" height="100" />' % (settings.MEDIA_URL, self.img.file))
    
class Faq(models.Model):

    QUSTION_TYPE_CHOICES = (
        (0, _("Авто-владельцу")),
        (1, _("Бизнесу")),
    )
    type = models.IntegerField(_("Тип вопроса"), choices=QUSTION_TYPE_CHOICES, default=0, blank=False)
    rank = models.IntegerField(_('Сортировка'), default=0)
    question = models.TextField(_("Вопрос"), max_length=1000, blank=False)
    answer = RichTextUploadingField("Ответ", blank=False)

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("FAQ")

    def __str__(self):
        return self.question
    
class Dictionary(models.Model):
    """Модель для хранения локализованных словарей."""
    LOCALE_CHOICES = (
        ('en', _('en')),
        ('ru', _('ru')),
    )

    CONTEXET_CHOICES = (
        ('vrn', _('Воронеж')),        
    )

    locale = models.CharField(_("Локаль (язык)"), choices=LOCALE_CHOICES, max_length=10, default='ru', db_index=True)
    context = models.CharField(_("Контекст"), choices=CONTEXET_CHOICES, max_length=10, default='vrn', blank=True, db_index=True)    
    key = models.CharField(_("Ключ"), max_length=512)
    value = models.TextField(_("Значение"))

    class Meta:
        verbose_name = _("Словарь")
        verbose_name_plural = _("Словари")
        unique_together = [['locale', 'context', 'key']]

    def __str__(self):
        value = self.value[:50] + '...' if len(self.value) > 50 else self.value
        return f"{self.key} ({self.locale}): {value}"