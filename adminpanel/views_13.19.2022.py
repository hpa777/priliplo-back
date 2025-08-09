from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from datetime import datetime
from django.contrib import messages

from adminpanel.forms import CampaignApproveForm
from client.models import CampaignApplication, PhotoReport, PhotoReportForm, UserProfile
from company.models import Advertiser, Campaign, AdvertiserSettings, CampaignBalanceHistory
from webpush import send_user_notification


class AdminMainView(generic.TemplateView):
    template_name = 'adminpanel/admin_main.html'

    def get_context_data(self, **kwargs):
        context = super(AdminMainView, self).get_context_data(**kwargs)
        context['title_1'] = "Сводка"
        context['title_2'] = "Сводка"

        try:
            context['sticker_applications'] = CampaignApplication.objects.filter(application_status=5).all()  # на оклейке
            context['campaign_requests'] = Campaign.objects.filter(campaign_status=1).all()  # акции на модерации
            context['active_campaigns'] = Campaign.objects.filter(campaign_status=2).all()  # Активные акции
            context['reports_not_completed'] = PhotoReport.objects.filter(photoreport_status=1).all()  # Не обработанных отчетов
            context['advertisers'] = Advertiser.objects.all()  # Рекламодателей
            context['carowners'] = UserProfile.objects.filter(user_role=2).all()  # Автомобилистов
            context['kassirs'] = UserProfile.objects.filter(user_role=4).all()  # Кассиров
            context['users'] = UserProfile.objects.all()  # Пользователей
        except:
            context['sticker_applications'] = {}
            context['campaign_requests'] = {}
            context['active_campaigns'] = {}
            context['reports_not_completed'] = {}
            context['advertisers'] = {}
            context['carowners'] = {}
            context['kassirs'] = {}
            context['users'] = {}
            context['title_2'] = ""

        return context


class ClientRequestsView(generic.ListView):
    template_name = 'adminpanel/client_requests.html'
    model = CampaignApplication

    def get_queryset(self):
        app_type = self.kwargs.get('app_type')
        return CampaignApplication.objects.filter(application_status=app_type)

    def get_context_data(self, **kwargs):
        context = super(ClientRequestsView, self).get_context_data(**kwargs)
        app_type = self.kwargs.get('app_type')
        if app_type == "1":
            context['title_1'] = "Запросы на участие в акциях"
        elif app_type == "2":
            context['title_1'] = "Одобренные участники акций"

        context['title_2'] = "Запросы"
        context['app_type'] = app_type

        return context


class ClientPhotoReportView(generic.ListView):
    template_name = 'adminpanel/client_photoreports.html'
    model = PhotoReport

    def get_queryset(self):
        return PhotoReport.objects.filter(photoreport_status=1)

    def get_context_data(self, **kwargs):
        context = super(ClientPhotoReportView, self).get_context_data(**kwargs)
        context['title_1'] = "Ожидающие одобрения отчеты клиентов "
        context['title_2'] = "Фотоотчеты"

        return context


class AdvertisersListView(generic.ListView):
    template_name = 'adminpanel/advertisers_list.html'
    model = Advertiser

    # def get_queryset(self):
    #     return Advertiser.objects.filter(photoreport_status=1)

    def get_context_data(self, **kwargs):
        context = super(AdvertisersListView, self).get_context_data(**kwargs)
        context['title_1'] = "Рекламодатели в системе"
        context['title_2'] = "Рекламодатели"

        return context


class AdminAdvDescriptionView(generic.DetailView):
    template_name = 'adminpanel/advertiser_desc.html'
    model = Advertiser

    def get_context_data(self, **kwargs):
        context = super(AdminAdvDescriptionView, self).get_context_data(**kwargs)
        # context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=1) | Q(application_status=2) | Q(application_status=5)).first()
        context['title_1'] = "Подробная информация о рекламодателе"
        context['breadcrumbs'] = [
            {'url': '/adminpanel/advertisers_list', 'text': 'Рекламодатели'}
        ]
        context['title_2'] = Advertiser.objects.get(pk=context['object'].pk)
        return context


class StickerRequestsView(generic.ListView):
    template_name = 'adminpanel/sticker_requests.html'
    model = CampaignApplication

    def get_queryset(self):
        return CampaignApplication.objects.filter(application_status=5)

    def get_context_data(self, **kwargs):
        context = super(StickerRequestsView, self).get_context_data(**kwargs)
        context['title_1'] = "Запросы на оклейку автомобиля"
        context['title_2'] = "Запросы на оклейку"

        return context


class AdminPhotoReportView(generic.TemplateView):
    template_name = 'adminpanel/photoreport.html'

    # model = News
    def get_context_data(self, **kwargs):
        context = super(AdminPhotoReportView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['application_id'] = pk
        context['title_1'] = "Фотоотчет"
        context['title_2'] = "Фотоотчет"

        active_application = CampaignApplication.objects.get(pk=pk)
        # context['active_application_count'] = active_application.count()
        context['active_application'] = active_application

        context['title_2'] = str(active_application.client.userprofile.get_full_name()) + " в " + active_application.campaign.title + " (" + active_application.campaign.advertiser.company_name + ")"
        context['form_type'] = "create"

        return context



def save_stiker_reserve_date(request, pk):
    if request.method == 'POST':
        reserve_date=request.POST.get('reserve_date', False)
        sticker_reserve_date = datetime.strptime(reserve_date, '%d-%m-%Y %H:%M')
        try:
            application = get_object_or_404(CampaignApplication, pk=pk)
            application.sticker_reserve_date = sticker_reserve_date
            application.save()
            return HttpResponse(sticker_reserve_date)
        except:
            return HttpResponse(u'Ошибка сохранения')


def application_action(request, pk, action):
    try:
        inst = CampaignApplication.objects.get(id=pk)
        if action == "2":
            inst.application_status = 2
            inst.approve_date = datetime.now()
            inst.save()
            messages.success(request, 'Заявка одобрена.')
            return HttpResponse('ok')
        elif action == "3":
            decline_note = request.POST.get('decline_note', False)
            inst.description = decline_note
            inst.application_status = 3
            inst.save()
            messages.error(request, 'Заявка отклонена')
            return HttpResponseRedirect('/adminpanel/sticker_requests/')
        else:
            return HttpResponse("Действие не возможно")
    except:
        return HttpResponse(u'Ошибка выполнения')


def save_photoreport(request):
    if request.method == 'POST':
        application_id=request.POST.get('application_id', False)

        form = PhotoReportForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                active_application = CampaignApplication.objects.get(pk=application_id)
                if active_application:
                    campaign = active_application.campaign
                    advertiser = campaign.advertiser
                    client = active_application.client

                    form_obj = form.save(commit=False)
                    form_obj.client = client
                    form_obj.application = active_application
                    form_obj.campaign = campaign
                    form_obj.advertiser = advertiser
                    form_obj.photoreport_status = 2
                    form_obj.save()

                    # пометка заявки как одобренной
                    active_application.application_status = 2
                    active_application.approve_date = datetime.now()
                    active_application.save()

                    advertiser_settings = AdvertiserSettings.objects.first()
                    campaign.campaign_balance = campaign.campaign_balance - advertiser_settings.sticking_cost # списать с акции стоимость оклейки
                    campaign.save()

                    messages.success(request, 'Фотоотчет сохранен.')
                    return HttpResponseRedirect('/adminpanel/sticker_requests/')
                else:
                    messages.error(request, "Заявка не существует")
                    return HttpResponseRedirect('/adminpanel/sticker_requests/')
                    # return render(request, 'adminpanel/photoreport.html', {'form': form})
            except:
                messages.error(request, "Ошибка создания фотоотчета 0045")
                return render(request, 'adminpanel/photoreport.html', {'form': form})

        else:
            messages.error(request, form.errors)
            return HttpResponseRedirect('/adminpanel/admin_photoreport/'+str(application_id)+'/')


def photoreport_action(request, pk, action):
    try:
        inst = PhotoReport.objects.get(id=pk)
        if request.user.userprofile.user_role == 1:
            if action == "2":
                inst.accept()
                messages.success(request, 'Отчет одобрен.')
                return HttpResponse('ok')
            elif action == "3":
                decline_note = request.POST.get('decline_note', False)
                inst.decline(decline_note)
                messages.error(request, 'Отчет отклонен')
                return HttpResponseRedirect('/adminpanel/client_photoreports/')
            else:
                return HttpResponse("Действие не возможно")
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
        return HttpResponse(u'Ошибка выполнения')


class CampaignRequestsView(generic.ListView):
    template_name = 'adminpanel/campaign_requests.html'
    model = Campaign

    def get_queryset(self):
        return Campaign.objects.filter(campaign_status=1)

    def get_context_data(self, **kwargs):
        context = super(CampaignRequestsView, self).get_context_data(**kwargs)
        context['title_1'] = "Запросы на модерацию акций"
        context['title_2'] = "Запросы на модерацию"

        return context


def campaign_action(request, pk, action):
    # print("1")
    if request.method == 'POST':
        # print("2")
        try:
            inst = Campaign.objects.get(id=pk)
            advertiser = inst.advertiser

            if action == "2":
                form = CampaignApproveForm(request.POST, request.FILES, instance=inst)
                if form.is_valid():
                    advertiser_settings = AdvertiserSettings.objects.first()

                    # advertiser_settings['logo_cost']

                    form_obj = form.save(commit=False)
                    form_obj.campaign_status = 2
                    form_obj.approve_date = datetime.now()
                    # form_obj.campaign_balance = inst.campaign_balance - advertiser_settings.logo_cost # списать с акции стоимость подготовки логотипа
                    form_obj.save()

                    change_balance = inst.campaign_balance - advertiser_settings.logo_cost  # списать с акции стоимость подготовки логотипа
                    campaign_balance_history_object = CampaignBalanceHistory.objects.create(advertiser=advertiser, campaign=form_obj, balance_decrease=change_balance, change_type=0)

                    # inst.campaign_status = 2
                    # inst.approve_date = datetime.now()
                    # inst.save()

                    send_user_notification(user=advertiser.owner_user, payload={"head": "Рекламная акция", "body": "Ваша заявка на создание рекламной акции в сервисе priliplo.ru ОДОБРЕНА!"}, ttl=1000)

                    messages.success(request, 'Заявка одобрена.')
                    # return HttpResponse('ok')
                    return HttpResponseRedirect('/adminpanel/campaign_requests/')
                else:
                    messages.error(request, 'Форма заполненна не полностью')
                    return HttpResponseRedirect('/adminpanel/campaign_requests/')
            elif action == "3":
                decline_note = request.POST.get('decline_note', False)
                inst.admin_comment = decline_note
                inst.campaign_status = 3
                inst.save()

                send_user_notification(user=advertiser.owner_user, payload={"head": "Рекламная акция", "body": "Ваша заявка на создание рекламной акции в сервисе priliplo.ru ОТКЛОНЕНА!"}, ttl=1000)

                messages.error(request, 'Заявка отклонена')
                return HttpResponseRedirect('/adminpanel/campaign_requests/')
            else:
                return HttpResponse("Действие не возможно")

        except:
            return HttpResponse(u'Ошибка выполнения')


class AllClientsView(generic.ListView):
    template_name = 'adminpanel/all_clients.html'
    model = UserProfile

    def get_queryset(self):
        # app_type = self.kwargs.get('app_type')
        objects = UserProfile.objects.filter(user_role=2)
        for obj in objects:
            obj.client = obj.user
            obj.applicationblank = CampaignApplication.objects.filter(client=obj.user, application_status=2).first()

        return objects

    def get_context_data(self, **kwargs):
        context = super(AllClientsView, self).get_context_data(**kwargs)
        # app_type = self.kwargs.get('app_type')
        context['title_1'] = "Автовладельцы"
        context['title_2'] = "Все пользователи"

        context['breadcrumbs'] = [
            {'url': '/adminpanel/', 'text': 'Сводка'}
        ]

        return context


def application_campaign_action(request, pk, action):
    try:
        inst = CampaignApplication.objects.get(id=pk)
        if request.user.userprofile.user_role == 1:
            if action == "2":
                inst.application_status = 5
                inst.save()
                messages.success(request, 'Заявка одобрена. Пользователь отправлен на оклейку автомобиля.')
                return HttpResponse('ok')
            elif action == "3":
                decline_note = request.POST.get('decline_note', False)
                inst.description = decline_note
                inst.application_status = 3
                inst.save()
                messages.error(request, 'Заявка отклонена')
                return HttpResponseRedirect('/adminpanel/client_requests/1/')
            else:
                return HttpResponse("Действие не возможно")
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
        return HttpResponse(u'Ошибка выполнения')