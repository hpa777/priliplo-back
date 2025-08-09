from django.views import generic
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import render
from advertiser.models import Advertiser, Campaign


class AdvertiserMainView(generic.TemplateView):
    template_name = 'advertiser_main.html'

    def get_context_data(self, **kwargs):
        context = super(AdvertiserMainView, self).get_context_data(**kwargs)
        context['user_status'] = 2  # TODO убрать после добавления авторизации
        context['title_1'] = "Сводка"
        context['title_2'] = ""
        context['campaigns'] = Campaign.objects.filter(advertiser=1)

        return context


class CampaignDescriptionView(generic.TemplateView):
    # template_name = 'client_main.html'
    def get_context_data(self, **kwargs):
        context = super(CampaignDescriptionView, self).get_context_data(**kwargs)
        context['user_status'] = 2  # TODO убрать после добавления авторизации
        pass

        return context
