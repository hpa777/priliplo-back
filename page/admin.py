from django.contrib import admin
from .models import Page
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



