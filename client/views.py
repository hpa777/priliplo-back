from django.views import generic
from django.views.generic import View
from django.shortcuts import render
from .models import UserProfile, UserProfileForm, AutoType, Country, City, District, Odometer, CampaignApplication, \
    AutoMarka, AutoModel, PhotoReportForm, PhotoReport, ClientBalanceHistory
from company.models import Advertiser, Campaign
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.utils.timezone import get_current_timezone
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.db.models import Q, F
from webpush import send_user_notification
from django.utils.timezone import make_aware, is_naive
from django.http import JsonResponse
import requests
from .gosnomer import normalize
import time
import json

def check_for_need_photoreport(context, accepted_application):
    #
    #
    #

    # try:
    #     period_start_date_tmp = timedelta(days=14)
    #     edit_date_start_date_TMP = accepted_application.approve_date + period_start_date_tmp
    #     print('edit_date_start_date= ', edit_date_start_date_TMP)
    #     print('edit_date_start_date.date()= ', edit_date_start_date_TMP.date())
    #     print('edit_date_end_date= ', edit_date_start_date_TMP)
    # except:
    #     print("===ERROR Date convert===")

    #
    #
    #


    # application_date = accepted_application.edited_date
    application_date = accepted_application.approve_date
    # print ("-----------------------")
    # print(application_date)
    # print(accepted_application.edited_date.date())
    # print(accepted_application.approve_date.date())
    # print (application_date)
    context['photoreport_start_date'] = application_date.strftime("%Y-%m-%d")
    # print (context['photoreport_start_date'])
    today = datetime.now(tz=get_current_timezone())
    # print(today.date())
    # context['days_from_accept'] = (today.date() - application_date.date()).days
    context['days_from_accept'] = (today.date() - application_date).days
    # print(context['days_from_accept'])

    start_date = 0
    end_date = 0
    current_period = 0

    if context['days_from_accept'] >= 14 and context['days_from_accept'] < 28:
        start_date = 14
        end_date = 28
        current_period = 2
    elif context['days_from_accept'] >= 28 and context['days_from_accept'] < 42:
        start_date = 28
        end_date = 42
        current_period = 3
    elif context['days_from_accept'] >= 42 and context['days_from_accept'] < 56:
        start_date = 42
        end_date = 56
        current_period = 4
    elif context['days_from_accept'] >= 56 and context['days_from_accept'] < 70:
        start_date = 56
        end_date = 70
        current_period = 5
    elif context['days_from_accept'] >= 70 and context['days_from_accept'] < 84:
        start_date = 70
        end_date = 84
        current_period = 6
    elif context['days_from_accept'] >= 84 and context['days_from_accept'] < 98:
        start_date = 84
        end_date = 98
        current_period = 7

    # print('start_date= ', start_date)
    # print('end_date= ', end_date)
    # print('current_period= ', current_period)

    if start_date != 0 and end_date != 0:
        period_start_date = timedelta(days=start_date)
        period_end_date = timedelta(days=end_date)
        edit_date_start_date = application_date + period_start_date
        edit_date_end_date = application_date + period_end_date
        context['current_period'] = current_period
        # edit_date_start_date = datetime.now(tz=get_current_timezone()) - period_14_days
        # today_minus_some_days = application_date - period_14_days

        # print('edit_date_start_date= ', edit_date_start_date)
        # try:
        #     print (get_current_timezone())
        #     print (is_naive(edit_date_start_date))
        #     print('edit_date_start_date make_aware= ', make_aware(edit_date_start_date, get_current_timezone()))
        # except:
        #     print('===Timezone error===')
        #
        # print('edit_date_end_date= ', edit_date_end_date)

        # photoreports = PhotoReport.objects.filter(Q(photoreport_status=1) | Q(photoreport_status=2)).filter(Q(edited_date__gte=edit_date_start_date) | Q(edited_date__lt=edit_date_end_date)).filter(application=acсepted_application).first()
        # photoreports = PhotoReport.objects.filter(Q(photoreport_status=1) | Q(photoreport_status=2)).filter(edited_date__gte=edit_date_start_date.date()).filter(edited_date__lt=edit_date_end_date.date()).filter(application=accepted_application).first()
        photoreports = PhotoReport.objects.filter(Q(photoreport_status=1) | Q(photoreport_status=2)).filter(edited_date__gte=edit_date_start_date).filter(edited_date__lt=edit_date_end_date).filter(application=accepted_application).first()

        # print ('photoreports= ', photoreports)
        if photoreports:
            need_photoreport = False
        else:
            need_photoreport = True
    else:
        need_photoreport = False

    return need_photoreport


class ClientMainView(generic.TemplateView):
    template_name = 'client/client_main.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ClientMainView, self).get_context_data(*args, **kwargs)
        try:
            context['advertisers_list'] = self.kwargs['advertisers_list']
        except:
            context['advertisers_list'] = False

        context['title_1'] = "Сводка"
        # context['title_2'] = "#ID-" + str(self.request.user.id)
        context['title_2'] = "Полезная информация"
        # context['advertisers_list'] = False
        context['advertisers'] = Advertiser.objects.all()
        context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=1) | Q(application_status=2) | Q(application_status=3) | Q(application_status=5)).first()
        context['acсepted_application'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=2)).first()
        # context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(~Q(application_status=0)).first()
        # print(context['active_applications'])

        if context['active_applications']:
            context['photoreports'] = context['active_applications'].get_photoreports()

        if context['acсepted_application']:
            context['need_photoreport'] = check_for_need_photoreport(context, context['acсepted_application'])

        return context


#
# class AdvertisersView(generic.TemplateView):
#     template_name = 'client/client_main.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(ClientMainView, self).get_context_data(**kwargs)
#         context['title_1'] = "Сводка"
#         context['title_2'] = "Список рекламодателей"
#         context['advertisers_list'] = True
#         context['advertisers'] = Advertiser.objects.all()
#         context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=1) | Q(application_status=2)).first()
#         context['acсepted_application'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=2)).first()
#
#         if context['acсepted_application']:
#             context['need_photoreport'] = check_for_need_photoreport(context, context['acсepted_application'])
#
#         return context


class ClientAdvDescriptionView(generic.DetailView):
    # class ClientAdvDescriptionView(generic.TemplateView):
    template_name = 'client/advertiser_desc.html'
    model = Advertiser

    def get_context_data(self, **kwargs):
        context = super(ClientAdvDescriptionView, self).get_context_data(**kwargs)
        # context['others_news']=News.get_news_block(2)
        context['campaigns'] = Campaign.objects.filter(advertiser=context['object']).filter(campaign_status=2)
        context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=1) | Q(application_status=2) | Q(application_status=5)).first()

        for campaign in context['campaigns']:
            campaign.applications_count = campaign.quota - CampaignApplication.objects.filter(campaign=campaign).filter(
                Q(application_status=1) | Q(application_status=2) | Q(application_status=5) | Q(application_status=7)).count()

        # context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(~Q(application_status=0)).first()
        context['title_1'] = "Подробная информация о рекламодателе"
        context['breadcrumbs'] = [
            {'url': '/client/', 'text': 'Рекламодатели'}
        ]
        context['title_2'] = context['object'].company_name
        return context


class ClientPhotoReportsHistoryView(generic.ListView):
    template_name = 'client/photoreports_history.html'
    model = PhotoReport

    def get_queryset(self):
        # advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return PhotoReport.objects.filter(client=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ClientPhotoReportsHistoryView, self).get_context_data(**kwargs)
        context['title_1'] = "Архив фотоотчетов"
        context['title_2'] = "Список отчетов"

        return context


class ClientPhotoReportView(generic.TemplateView):
    template_name = 'client/photoreport.html'

    # model = News
    def get_context_data(self, **kwargs):
        context = super(ClientPhotoReportView, self).get_context_data(**kwargs)
        # context['others_news']=News.get_news_block(2)
        context['title_1'] = "Фотоотчет"
        context['title_2'] = "Фотоотчет"

        active_application = CampaignApplication.objects.filter(client=self.request.user).filter(application_status=2)
        context['active_application_count'] = active_application.count()
        context['active_application'] = active_application.first()
        context['acсepted_application'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=2)).first()
        if context['acсepted_application']:
            context['need_photoreport'] = check_for_need_photoreport(context, context['acсepted_application'])
        else:
            context['need_photoreport'] = False

        if context['active_application_count'] > 0:
            context['photo_report'] = PhotoReport.objects.filter(client=self.request.user).filter(application=context['active_application']).filter(
                Q(photoreport_status=1) | Q(photoreport_status=3)).first()
            if context['photo_report']:
                if context['photo_report'].photoreport_status == 1 or context['photo_report'].photoreport_status == 3:
                    context['form'] = {}
                    context['form']['data'] = context['photo_report']

                    context['form_type'] = "edit"
                    context['title_2'] = "Редактирование отчета"
                    context['form_title_2'] = "Редактирование отчета от " + context['photo_report'].created_date.strftime("%d.%m.%Y")
            else:
                context['title_2'] = "Создание фотоотчета"
                context['form_type'] = "create"

        return context


class UserData(generic.TemplateView):
    template_name = 'client/user_data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_profile'] = UserProfile.objects.filter(user=self.request.user).first()
        context['user'] = self.request.user
        context['auto_types'] = AutoType.objects.all
        context['countries'] = Country.objects.all
        context['cities'] = City.objects.all
        context['districts'] = District.objects.all
        context['odometers'] = Odometer.objects.all
        context['auto_marka'] = AutoMarka.objects.all
        context['auto_model'] = AutoModel.objects.all

        context['form'] = UserProfileForm()
        context['main_name'] = 'Данные пользователя'
        context['title_1'] = "Профиль"
        context['title_2'] = "Профиль"

        return context


class BonusChangesView(generic.ListView):
    template_name = 'client/bonus_changes_history.html'
    model = ClientBalanceHistory

    def get_queryset(self):
        # client = Advertiser.objects.get(owner_user=self.request.user)
        client = UserProfile.objects.filter(user=self.request.user.id).first().user
        return ClientBalanceHistory.objects.filter(client=client)

    def get_context_data(self, **kwargs):
        context = super(BonusChangesView, self).get_context_data(**kwargs)
        context['title_1'] = "История изменений баллов"
        context['title_2'] = "История изменений баллов"

        context['yesterday'] = datetime.today() - timedelta(days=1)

        return context


def save_user_data(request):
    if request.method == 'POST':
        inst = UserProfile.objects.filter(user=request.user.id).first()
        form = UserProfileForm(request.POST, request.FILES, instance=inst)

        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Данные профиля сохранены')
            return HttpResponseRedirect('/client/')
        else:
            messages.error(request, form.errors)
            return HttpResponseRedirect('/client/user_data/')
    else:
        form = UserProfileForm()
        messages.error(request, "Ошибка GET запроса 0050")
        return HttpResponseRedirect('/client/user_data/')


def request_application_to_campaign(request, pk):
    user_model = request.user
    profile = UserProfile.objects.filter(user=user_model.id).first()
    campaign_model = Campaign.objects.get(pk=pk)
    if profile.profile_filled() and (campaign_model.get_applications_quota() > 0):
        today = datetime.now(tz=get_current_timezone())
        if today <= campaign_model.end_date:
            application = CampaignApplication(client=user_model, campaign=campaign_model, advertiser=campaign_model.advertiser, application_status=1)
            application.save()

            messages.success(request, 'Заявка на участие в акции отправлена рекламодателю. Ожидайте одобрения.')
        else:
            messages.error(request, 'Прием заявок в акцию окончен')
    else:
        messages.error(request, 'Чтобы присоединиться к акции нужно рассказать побольше о себе и своем автомобиле. Сделайте это в разделе Профиль и возвращайтесь, когда все будет готово.')

    return HttpResponseRedirect('/client/')


def remove_application_from_campaign(request, pk):
    user_model = request.user

    try:
        inst = CampaignApplication.objects.get(id=pk)
        if inst.client.pk == user_model.pk:
            inst.application_status = 6
            inst.save()
            messages.success(request, 'Вы отказались от участия в акции')
        else:
            messages.error(request, 'Вы не участвуете в этой акции')
    except:
        messages.error(request, 'Ошибка')

    return HttpResponseRedirect('/client/')


def save_photoreport(request):
    if request.method == 'POST':
        pk = request.POST.get('id', False)

        if pk == False:
            form = PhotoReportForm(request.POST, request.FILES)

            if form.is_valid():
                try:
                    # select last active campaign!
                    active_application = CampaignApplication.objects.filter(client=request.user).filter(application_status=2).first()

                    if active_application:
                        need_photoreport = check_for_need_photoreport({}, active_application)
                        if need_photoreport:
                            campaign = active_application.campaign
                            advertiser = campaign.advertiser

                            form_obj = form.save(commit=False)
                            form_obj.client = request.user
                            form_obj.application = active_application
                            form_obj.campaign = campaign
                            form_obj.advertiser = advertiser
                            form_obj.photoreport_status = 1
                            form_obj.save()

                            send_user_notification(user=advertiser.owner_user, payload={"head": "Фотоотчеты", "body": "Вам отправили фотоотчет в сервисе priliplo.ru!"}, ttl=1000)

                            messages.success(request, 'Фотоотчет сохранен. Ожидайте его подтверждения рекламодателем.')
                            return HttpResponseRedirect('/client/photoreport/')
                        else:
                            messages.error(request, "Ошибка расчета времени фотоотчета. Сообщите администратору об ошибке.")
                            return render(request, 'client/photoreport.html', {'form': form})
                    else:
                        messages.error(request, "Вы не участвуете ни в одной акции")
                        return render(request, 'client/photoreport.html', {'form': form})
                except:
                    messages.error(request, "Ошибка создания фотоотчета 0055")
                    # return render(request, 'client/photoreport.html', {'form': form})
                    return HttpResponseRedirect('/client/photoreport/')
            else:
                messages.error(request, form.errors)
                return HttpResponseRedirect('/client/photoreport/')
                # return render(request, 'client/photoreport.html', {'form': form})

        else:
            try:
                active_application = CampaignApplication.objects.filter(client=request.user).filter(application_status=2).first()
                if active_application:
                    campaign = active_application.campaign
                    advertiser = campaign.advertiser

                    photo_report = PhotoReport.objects.filter(client=request.user).filter(application=active_application).first()
                    if photo_report:
                        form = PhotoReportForm(request.POST, request.FILES, instance=photo_report)

                        form.fields['photoreport_odometer'].required = False
                        form.fields['photoreport_sticker'].required = False

                        if form.is_valid():

                            if not "photoreport_odometer" in form.data:
                                form.data.photoreport_odometer = photo_report.photoreport_odometer
                            if not "photoreport_sticker" in form.data:
                                form.data.photoreport_sticker = photo_report.photoreport_sticker

                            form_obj = form.save(commit=False)
                            form_obj.photoreport_status = 1
                            form_obj.save()

                            messages.success(request, 'Фотоотчет сохранен. Ожидайте его подтверждения рекламодателем.')
                            return HttpResponseRedirect('/client/photoreport/')
                        else:
                            messages.error(request, form.errors)
                            return HttpResponseRedirect('/client/photoreport/')
                            # return render(request, 'client/photoreport.html', {'form': form, 'form_type': "edit"})
                else:
                    messages.success(request, 'Вы не участвуете ни в одной акции')
                    return HttpResponseRedirect('/client/photoreport/')

            except:
                messages.error(request, "Ошибка редактирования акции 0051")
                return HttpResponseRedirect('/client/photoreport/')


def translate_to_ru(x):
    dic = {'ь':'', 'ъ':'', 'а':'a', 'б':'b','в':'b',
           'г':'g', 'д':'d', 'е':'e', 'ё':'e','ж':'z',
           'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l',
           'м':'m', 'н':'h', 'о':'o', 'р':'p', 'рр':'r',
           'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h',
           'ц':'ts', 'ч':'ch', 'ш':'sh', 'щ':'sch', 'ы':'yi',
           'э':'e', 'ю':'yu', 'я':'ya'}

    t = ''
    for i in x:
        t+=dic.get(i.lower(), i.lower()).upper() if i.isupper() else dic.get(i, i)
    return t



class upload_auto_data(View):
    def post(self, request):
        license = request.POST.get('license')

        token = "d8eea67c134669d4d720b95f7c79432d"
        url_rsa = "https://api-cloud.ru/api/converter.php"
        url_gibdd = "https://api-cloud.ru/api/gibdd.php"
        # data_rsa = {
        #     "token": token,
        #     "type": "osago",
        #     "regNumber": "E332PT190",
        #     "cache": "1"
        # }
        params_rsa = dict(
            token=token,
            type="search",
            # regNumber="е332рт190",
            string=normalize(license),
            #cache="1"
        )
        # params_gibdd = dict(
        #     token=token,
        #     type="gibdd",
        #     vin="X96ERB6X4B0008543",
        # )
        # out_rsa = json.loads("{'status': 200, 'count': 1, 'rez': [{'numberID': '1', 'seria': 'ААВ', 'nomer': '3024662873', 'orgosago': 'АО \"СОГАЗ\"', 'status': 'Действует', 'term': 'Период использования ТС активен на запрашиваемую дату', 'brandmodel': 'ГАЗ Прочие (категория «B»)', 'regnum': 'в456оа36', 'vin': 'X96ERB6X4B0008543', 'kuzovNumber': None, 'power': '143.00', 'maxMassa': None, 'sledToRegorTo': 'Нет', 'trailer': 'Нет', 'cel': 'Прочее', 'ogran': 'Не ограничен список лиц, допущенных к управлению', 'insured': 'ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325', 'owner': 'ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325', 'kbm': '0.64', 'region': 'Воронежская обл, г Воронеж', 'strahsum': '2846.79 руб.', 'dateactual': '24.08.2022'}], 'inquiry': {'price': 0.5, 'speed': 6, 'attempts': 1}, 'cache': {'actual': '24.08.2022 14:15:40', 'start': {'timestamp': 1661318787, 'date': '24.08.2022 08:26:27'}, 'stop': {'timestamp': 1661361987, 'date': '24.08.2022 20:26:27'}}}")
        # js = "{'status': 200, 'count': 1, 'rez': [{'numberID': '1', 'seria': 'ААВ', 'nomer': '3024662873', 'orgosago': 'АО \"СОГАЗ\"', 'status': 'Действует', 'term': 'Период использования ТС активен на запрашиваемую дату', 'brandmodel': 'ГАЗ Прочие (категория «B»)', 'regnum': 'в456оа36', 'vin': 'X96ERB6X4B0008543', 'kuzovNumber': None, 'power': '143.00', 'maxMassa': None, 'sledToRegorTo': 'Нет', 'trailer': 'Нет', 'cel': 'Прочее', 'ogran': 'Не ограничен список лиц, допущенных к управлению', 'insured': 'ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325', 'owner': 'ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325', 'kbm': '0.64', 'region': 'Воронежская обл, г Воронеж', 'strahsum': '2846.79 руб.', 'dateactual': '24.08.2022'}], 'inquiry': {'price': 0.5, 'speed': 6, 'attempts': 1}, 'cache': {'actual': '24.08.2022 14:15:40', 'start': {'timestamp': 1661318787, 'date': '24.08.2022 08:26:27'}, 'stop': {'timestamp': 1661361987, 'date': '24.08.2022 20:26:27'}}}"
        js = '''{
   "status":200,
   "count":1,
   "rez":[
      {
         "numberID":"1",
         "seria":"ААВ",
         "nomer":"3024662873",
         "orgosago":"АО СОГАЗ",
         "status":"Действует",
         "term":"Период использования ТС активен на запрашиваемую дату",
         "brandmodel":"ГАЗ Прочие (категория «B»)",
         "regnum":"в456оа36",
         "vin":"X96ERB6X4B0008543",
         "kuzovNumber":"None",
         "power":"143.00",
         "maxMassa":"None",
         "sledToRegorTo":"Нет",
         "trailer":"Нет",
         "cel":"Прочее",
         "ogran":"Не ограничен список лиц, допущенных к управлению",
         "insured":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325",
         "owner":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325",
         "kbm":"0.64",
         "region":"Воронежская обл, г Воронеж",
         "strahsum":"2846.79 руб.",
         "dateactual":"24.08.2022"
      }
   ],
   "inquiry":{
      "price":0.5,
      "speed":6,
      "attempts":1
   },
   "cache":{
      "actual":"24.08.2022 14:15:40",
      "start":{
         "timestamp":1661318787,
         "date":"24.08.2022 08:26:27"
      },
      "stop":{
         "timestamp":1661361987,
         "date":"24.08.2022 20:26:27"
      }
   }
}'''

        js_gibdd = '''{
   "status":200,
   "found":true,
   "utilicazia":0,
   "utilicaziainfo":"",
   "vehicle":{
      "vin":"X96ERB6X4B0008543",
      "bodyNumber":"JR4100B0008622",
      "engineNumber":"275800042",
      "model":"ВОЛГА SIВЕR ",
      "color":"ЧЕРНЫЙ",
      "year":"2010",
      "engineVolume":"2429.0",
      "powerHp":"143.0",
      "powerKwt":"105.2",
      "category":"В",
      "type":"23",
      "typeinfo":"Легковые автомобили седан"
   },
   "vehiclePassport":{
      "number":"52НВ256950",
      "issue":"ГОУВПО ПГПУ ИМ.С.М.КИРОВА"
   },
   "ownershipPeriod":[
      {
         "lastOperation":"11",
         "lastOperationInfo":"первичная регистрация",
         "simplePersonType":"Legal",
         "simplePersonTypeInfo":"Юридическое лицо",
         "from":"23.12.2010",
         "to":"27.12.2011",
         "period":"1 год 0 месяцев 3 дня"
      },
      {
         "lastOperation":"04",
         "lastOperationInfo":"изменение данных о собственнике (владельце)",
         "simplePersonType":"Legal",
         "simplePersonTypeInfo":"Юридическое лицо",
         "from":"27.12.2011",
         "to":"23.04.2021",
         "period":"9 лет 4 месяца 0 дней"
      },
      {
         "lastOperation":"03",
         "lastOperationInfo":"Изменение собственника (владельца) в результате совершения сделки, вступления в наследство, слияние и разделение капитала у юридического лица, переход права по договору лизинга, судебные решения и др.",
         "simplePersonType":"Legal",
         "simplePersonTypeInfo":"Юридическое лицо",
         "from":"23.04.2021",
         "to":"null",
         "period":"1 год 4 месяца 3 дня"
      }
   ],
   "inquiry":{
      "price":0.5,
      "speed":2,
      "attempts":1
   }
}'''
        usr_profile = UserProfile.objects.filter(user=self.request.user.id).first()

        if usr_profile.loaded_rsainfo_attempts < 1:

            js_gibdd_json = json.loads(js_gibdd)
            try:
                response_rsa = requests.get(url_rsa, params=params_rsa, timeout=60)
                out_rsa = response_rsa.json()
                usr_profile.rsa_info = out_rsa  # сохранить json в базу
                # out_rsa = json.loads(js)
                # print (out_rsa)
            except:
                response = {
                    'status': 'error',
                    'normalize_license': normalize(license),
                    'out': "Ошибка получения информации ГИБДД об автомобиле 001"
                }
                return JsonResponse(response)

            try:
                # print(out_rsa["status"])
                if out_rsa["status"] == 200:                    
                    if out_rsa["partner"]["found"] == True:
                        # Получение информации из гибдд
                        params_gibdd = dict(
                            token=token,
                            type="gibdd",
                            # vin="X96ERB6X4B0008543",
                            vin=out_rsa["partner"]["result"]["vin"],
                        )
                        response_gibdd = requests.get(url_gibdd, params=params_gibdd, timeout=60)
                        # print (response_gibdd.json())
                        js_gibdd_json = response_gibdd.json()
                        usr_profile.gibdd_info = js_gibdd_json  # сохранить json в базу
                        # js_gibdd_json = json.loads(js_gibdd)


                        try:
                            if js_gibdd_json["vehicle"]["category"] == "В":
                                category = "1"
                            elif js_gibdd_json["vehicle"]["category"] == "В":
                                category = "2"
                            else:
                                category = "3"

                            #if "Воронеж" in out_rsa["rez"][0]["region"]:
                            #    city = 1
                            #else:
                            #    city = 1


                            # print(usr_profile)
                            usr_profile.loaded_rsainfo_attempts += 1
                            usr_profile.save()
                            # usr_profile.update(loaded_rsainfo_attempts=F('loaded_rsainfo_attempts') + 1)

                            out_gibdd = {
                                "model":js_gibdd_json["vehicle"]["model"],
                                "year":js_gibdd_json["vehicle"]["year"],
                                "category":category,
                            #    "city":city,
                            }
                            response = {
                                'status': 'ok',
                                'normalize_license': normalize(license),
                                'out': out_gibdd
                            }
                        except:
                            response = {
                                'status': 'error',
                                'normalize_license': normalize(license),
                                'out': "Ошибка получения информации ГИБДД об автомобиле 003"
                            }
                            return JsonResponse(response)








                        # return JsonResponse(response)
                    else:
                        response = {
                            'status': 'error',
                            'normalize_license': normalize(license),
                            'out': "Информация не найдена"
                        }
                else:
                    response = {
                        'status': 'error',
                        'normalize_license': normalize(license),
                        'out': out_rsa.error
                    }
                    return JsonResponse(response)
            except:
                response = {
                    'status': 'error',
                    'normalize_license': normalize(license),
                    'out': "Ошибка получения информации ГИБДД об автомобиле 002"
                }
                return JsonResponse(response)

        else:
            response = {
                'status': 'error',
                'normalize_license': normalize(license),
                'out': "Превышено количество попыток запроса данных об автомобиле"
            }
            return JsonResponse(response)
        # response_gibdd = requests.get(url_gibdd, params=params_gibdd)
        # print (response_gibdd.json())
        #
        # r = requests.get(url_gibdd, params=params_gibdd)
        # print (r.json())
        # {"status":200,"count":1,"rez":[{"numberID":"1","seria":"ААВ","nomer":"3024662873","orgosago":"АО \"СОГАЗ\"","status":"Действует","term":"Период использования ТС активен на запрашиваемую дату","brandmodel":"ГАЗ Прочие (категория «B»)","regnum":"в456оа36","vin":"X96ERB6X4B0008543","kuzovNumber":null,"power":"143.00","maxMassa":null,"sledToRegorTo":"Нет","trailer":"Нет","cel":"Прочее","ogran":"Не ограничен список лиц, допущенных к управлению","insured":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325","owner":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325","kbm":"0.64","region":"Воронежская обл, г Воронеж","strahsum":"2846.79 руб.","dateactual":"19.08.2022"}],"inquiry":{"price":0.5,"speed":10,"attempts":1},"cache":{"actual":"19.08.2022 17:34:40","start":{"timestamp":1660898420,"date":"19.08.2022 11:40:20"},"stop":{"timestamp":1660941620,"date":"19.08.2022 23:40:20"}}}
        # {'status': 200, 'found': True, 'utilicazia': 0, 'utilicaziainfo': '', 'vehicle': {'vin': 'X96ERB6X4B0008543', 'bodyNumber': 'JR4100B0008622', 'engineNumber': '275800042', 'model': 'ВОЛГА SIВЕR ', 'color': 'ЧЕРНЫЙ', 'year': '2010', 'engineVolume': '2429.0', 'powerHp': '143.0', 'powerKwt': '105.2', 'category': 'В', 'type': '23', 'typeinfo': 'Легковые автомобили седан'}, 'vehiclePassport': {'number': '52НВ256950', 'issue': 'ГОУВПО ПГПУ ИМ.С.М.КИРОВА'}, 'ownershipPeriod': [{'lastOperation': '11', 'lastOperationInfo': 'первичная регистрация', 'simplePersonType': 'Legal', 'simplePersonTypeInfo': 'Юридическое лицо', 'from': '23.12.2010', 'to': '27.12.2011', 'period': '1 год 0 месяцев 3 дня'}, {'lastOperation': '04', 'lastOperationInfo': 'изменение данных о собственнике (владельце)', 'simplePersonType': 'Legal', 'simplePersonTypeInfo': 'Юридическое лицо', 'from': '27.12.2011', 'to': '23.04.2021', 'period': '9 лет 4 месяца 0 дней'}, {'lastOperation': '03', 'lastOperationInfo': 'Изменение собственника (владельца) в результате совершения сделки, вступления в наследство, слияние и разделение капитала у юридического лица, переход права по договору лизинга, судебные решения и др.', 'simplePersonType': 'Legal', 'simplePersonTypeInfo': 'Юридическое лицо', 'from': '23.04.2021', 'to': 'null', 'period': '1 год 4 месяца 2 дня'}], 'inquiry': {'price': 0.5, 'speed': 2, 'attempts': 1}}
        # response = {
        #     'status': 'ok',
        #     'normalize_license': normalize(license),
        #     'out': r.text
        #     # 'out': {"status":200,"count":1,"rez":[{"numberID":"1","seria":"ААВ","nomer":"3024662873","orgosago":"АО \"СОГАЗ\"","status":"Действует","term":"Период использования ТС активен на запрашиваемую дату","brandmodel":"ГАЗ Прочие (категория «B»)","regnum":"в456оа36","vin":"X96ERB6X4B0008543","kuzovNumber":null,"power":"143.00","maxMassa":null,"sledToRegorTo":"Нет","trailer":"Нет","cel":"Прочее","ogran":"Не ограничен список лиц, допущенных к управлению","insured":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325","owner":"ФЕДЕРАЛЬНОЕГОСУДАРСТВЕННОЕБЮДЖЕТНОЕОБРАЗОВАТЕЛЬНОЕУЧРЕЖДЕНИЕВЫСШЕГООБРАЗОВАНИЯВОРОНЕЖСКИИГОСУДАРСТВЕННЫИЛЕСОТЕХНИЧЕСКИИУНИВЕРСИТЕТИМЕНИГФМОРОЗОВА, ИНН 3666012325","kbm":"0.64","region":"Воронежская обл, г Воронеж","strahsum":"2846.79 руб.","dateactual":"19.08.2022"}],"inquiry":{"price":0.5,"speed":10,"attempts":1},"cache":{"actual":"19.08.2022 17:34:40","start":{"timestamp":1660898420,"date":"19.08.2022 11:40:20"},"stop":{"timestamp":1660941620,"date":"19.08.2022 23:40:20"}}}
        # }
        # time.sleep(3)
        return JsonResponse(response)