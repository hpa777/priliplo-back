from django.contrib import admin
from .models import Page, Slider, Slide
from django import forms
from django.utils.translation import ugettext_lazy as _


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {
            'fields': ('in_menus', 'title', 'menu_title', 'slug', 'meta_description', 'meta_keywords', 'login_required', 'content')
        }),
        (_('Расширенные настройки'), {
            'classes': ('collapse grp-collapse grp-closed',),
            'fields': ('page_type', 'redirect_url'),
        }),
    )

admin.site.register(Page, PageAdmin)



admin.site.register(Slider)

class SlideAdmin(admin.ModelAdmin):
    list_display = ('slider', 'title', 'img_tag')
    list_filter = ('slider',)
    raw_id_fields = ('img', 'img_mob', 'img_tablet', 'icon')
    ordering =('slider', 'rank',)

admin.site.register(Slide, SlideAdmin)



