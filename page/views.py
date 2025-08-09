from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.views.generic import View

from company.models import BusinessType
from .models import Page
import requests
from django.conf import settings


class PageView(generic.DetailView):
    model = Page
    template_name = 'frontend/mainpage/page.html'

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)

        context = get_frontend_data(context)

        context['slug'] = self.kwargs['slug']
        context['title_1'] = context['object'].title

        return context


def get_frontend_data(context):
    context['menu_categories'] = BusinessType.objects.filter(parent_business_type=None)
    return context