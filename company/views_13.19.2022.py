from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.shortcuts import render
from django.contrib import messages
from sorl.thumbnail import delete
from datetime import datetime, timedelta
from client.models import CampaignApplication, PhotoReport, CompanyProfile, UserProfile, ClientBalanceHistory
from company.models import Advertiser, Campaign, CampaignForm, CompanyProfileForm, Order, Billing_history, \
    AdvertiserSettings, BusinessType, CampaignBalanceHistory
from robokassa.forms import RobokassaForm


class AdvertiserMainView(generic.TemplateView):
    template_name = 'company/advertiser_main.html'

    def get_context_data(self, **kwargs):
        context = super(AdvertiserMainView, self).get_context_data(**kwargs)
        context['user_status'] = 2  # TODO убрать после добавления авторизации
        context['title_1'] = "Сводка"

        try:
            context['advertiser'] = Advertiser.objects.get(owner_user=self.request.user)
            context['campaigns'] = Campaign.objects.filter(advertiser=context['advertiser'])

            try:
                context['declined_applications'] = Campaign.objects.filter(advertiser=context['advertiser'], application_status=3).all()
            except:
                context['declined_applications'] = {}

            context['title_2'] = context['advertiser'].company_name
        except:
            context['advertiser'] = {}
            context['campaigns'] = {}

            # context['active_applications'] = {}
            context['title_2'] = ""

        return context



class AdvertiserListCampaigns(generic.TemplateView):
    template_name = 'company/campaigns_list.html'

    def get_context_data(self, **kwargs):
        context = super(AdvertiserListCampaigns, self).get_context_data(**kwargs)
        context['user_status'] = 2  # TODO убрать после добавления авторизации
        context['title_1'] = "Сводка"

        try:
            context['advertiser'] = Advertiser.objects.get(owner_user=self.request.user)
            context['campaigns'] = Campaign.objects.filter(advertiser=context['advertiser'])

            try:
                context['declined_applications'] = Campaign.objects.filter(advertiser=context['advertiser'], application_status=3).all()
            except:
                context['declined_applications'] = {}

            context['title_2'] = context['advertiser'].company_name
        except:
            context['advertiser'] = {}
            context['campaigns'] = {}

            # context['active_applications'] = {}
            context['title_2'] = ""

        return context


class CampaignDescriptionView(generic.DetailView):
    template_name = 'company/campaign_desc.html'
    model = Campaign

    # def get_object(self):
    #     advertiser = Advertiser.objects.get(owner_user=self.request.user)
    #     campaign = get_object_or_404(Campaign, pk=self.kwargs['pk'], advertiser=advertiser)
    #     return campaign

    def get_queryset(self):
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return Campaign.objects.filter(advertiser=advertiser)

    def get_context_data(self, **kwargs):
        context = super(CampaignDescriptionView, self).get_context_data(**kwargs)
        context['title_1'] = "Подробности акции"
        context['title_2'] = context['object'].title
        context['breadcrumbs'] = [
            {'url': '/company/', 'text': 'Список акций'}
        ]

        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        context['active_applications'] = CampaignApplication.objects.filter(campaign=context['object']).filter(advertiser=advertiser).filter(application_status=2).all()
        context['request_applications'] = CampaignApplication.objects.filter(campaign=context['object']).filter(advertiser=advertiser).filter(application_status=1).all()
        context['sticker_applications'] = CampaignApplication.objects.filter(campaign=context['object']).filter(advertiser=advertiser).filter(application_status=5).all()  # на оклейке
        context['finished_applications'] = CampaignApplication.objects.filter(campaign=context['object']).filter(advertiser=advertiser).filter(application_status=7).all()  # получившие баллы

        return context


class ClientPhotoReportView(generic.ListView):
    template_name = 'company/client_photoreports.html'
    model = PhotoReport

    def get_queryset(self):
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return PhotoReport.objects.filter(advertiser=advertiser, photoreport_status=1)

    def get_context_data(self, **kwargs):
        context = super(ClientPhotoReportView, self).get_context_data(**kwargs)
        context['title_1'] = "Отчеты клиентов"
        context['title_2'] = "Отчеты клиентов"

        return context


class ClientRequestsView(generic.ListView):
    template_name = 'company/client_requests.html'
    model = CampaignApplication

    def get_queryset(self):
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return CampaignApplication.objects.filter(advertiser=advertiser, application_status=1)

    def get_context_data(self, **kwargs):
        context = super(ClientRequestsView, self).get_context_data(**kwargs)
        context['title_1'] = "Запросы на участие в акциях"
        context['title_2'] = "Запросы на участие в акциях"

        return context


class BalanceHistoryView(generic.ListView):
    template_name = 'company/balance_history.html'
    model = Billing_history

    def get_queryset(self):
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return Billing_history.objects.filter(advertiser=advertiser)

    def get_context_data(self, **kwargs):
        context = super(BalanceHistoryView, self).get_context_data(**kwargs)
        context['title_1'] = "История изменений баланса"
        context['title_2'] = "История изменений баланса"

        return context


class CreateCampaignView(generic.TemplateView):
    template_name = 'company/create_campaign.html'

    def get_context_data(self, **kwargs):
        context = super(CreateCampaignView, self).get_context_data(**kwargs)
        context['form_type'] = "create"
        context['title_1'] = "Создать акцию"
        context['title_2'] = "Создать акцию"

        advertiser_settings = AdvertiserSettings.objects.first()
        context['advertiser_settings'] = advertiser_settings

        # context['title_2'] = context['object'].title

        return context


class CreateCampaignViewWizard(generic.TemplateView):
    template_name = 'company/create_campaign_wizard.html'

    def get_context_data(self, **kwargs):
        context = super(CreateCampaignViewWizard, self).get_context_data(**kwargs)
        context['form_type'] = "create"
        context['title_1'] = "Создать акцию"
        context['title_2'] = "Создать акцию"

        advertiser_settings = AdvertiserSettings.objects.first()
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        context['advertiser_settings'] = advertiser_settings
        context['advertiser'] = advertiser

    # context['title_2'] = context['object'].title

        return context


class EditCampaignView(generic.DetailView):
    model = Campaign
    template_name = 'company/create_campaign.html'

    def get_context_data(self, **kwargs):
        context = super(EditCampaignView, self).get_context_data(**kwargs)
        context['form_type'] = "edit"
        context['title_1'] = "Редактировать акцию"
        context['title_2'] = context['object'].title
        context['obj_id'] = context['object'].pk
        context['form'] = {}
        context['form']['data'] = context['object']

        return context


def application_action(request, pk, action):
    try:
        inst = CampaignApplication.objects.get(id=pk)
        if inst.campaign.advertiser.owner_user.pk == request.user.pk:
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
                return HttpResponseRedirect('/company/campaign_desc/'+str(inst.campaign.pk)+'/')
            else:
                return HttpResponse("Действие не возможно")
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
        return HttpResponse(u'Ошибка выполнения')


def photoreport_action(request, pk, action):
    try:
        inst = PhotoReport.objects.get(id=pk)
        if inst.advertiser.owner_user.pk == request.user.pk:
            if action == "2":
                # inst.photoreport_status = 2
                # inst.save()
                inst.accept()
                messages.success(request, 'Отчет одобрен.')
                return HttpResponse('ok')
            elif action == "3":
                decline_note = request.POST.get('decline_note', False)
                inst.decline(decline_note)
                # inst.description = decline_note
                # inst.photoreport_status = 3
                # inst.save()
                messages.error(request, 'Отчет отклонен')
                return HttpResponseRedirect('/company/client_photoreports/')
            else:
                return HttpResponse("Действие не возможно")
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
        return HttpResponse(u'Ошибка выполнения')


def save_campaign_data(request):
    if request.method == 'POST':

        pk=request.POST.get('id')

        if pk is None:
            form = CampaignForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    advertiser = Advertiser.objects.get(owner_user=request.user)

                    # if id:
                    #     campaign = get_object_or_404(Campaign, pk=id)
                    #     if campaign.advertiser != advertiser:
                    #         return HttpResponseForbidden()
                    # else:
                    #     campaign =

                    advertiser_settings = AdvertiserSettings.objects.first()
                    change_balance = ((advertiser_settings.period_cost * 3) + advertiser_settings.sticking_cost) * form.cleaned_data['quota'] + advertiser_settings.logo_cost

                    if advertiser.balance >= change_balance:

                        form_obj = form.save(commit=False)
                        # form_obj.advertiser = Advertiser.objects.get(owner_user=request.user)
                        form_obj.campaign_status = 1
                        form_obj.advertiser = advertiser
                        # form_obj.campaign_balance = change_balance
                        form_obj.save()

                        billing_history_object = Billing_history.objects.create(advertiser=advertiser, balance_decrease=change_balance, change_type=4)

                        campaign = Campaign.objects.filter(pk=pk).first()
                        campaign_balance_history_object = CampaignBalanceHistory.objects.create(advertiser=advertiser, campaign=form_obj, balance_increase=change_balance, change_type=3)

                        # print(advertiser_settings.sticking_cost)
                        # print(advertiser_settings.period_cost)
                        # print(change_balance)

                        messages.success(request,'Акция создана')
                        return HttpResponseRedirect('/company/list_campaigns/')
                    else:
                        messages.error(request, "На балансе не достаточно средств. Стоимость создания акции " + str(change_balance) + " руб.")
                        return render(request, 'company/create_campaign.html', {'form': form, 'form_type': "create"})
                except:
                # except Exception as e:
                    # print ('%s (%s)' % (e.message, type(e)))
                    messages.error(request, "Ошибка создания акции 0051")
                    return render(request, 'company/create_campaign.html', {'form': form, 'form_type': "create"})

            else:
                messages.error(request, form.errors)
                return render(request, 'company/create_campaign.html', {'form': form, 'form_type': "create"})

        else:
            try:
                advertiser = Advertiser.objects.get(owner_user=request.user)
                campaign = get_object_or_404(Campaign, pk=pk)


                if campaign.advertiser != advertiser:
                    return HttpResponseForbidden()
                else:
                    form = CampaignForm(request.POST, request.FILES, instance=campaign)

                    award = campaign.award
                    quota = campaign.quota
                    end_date = campaign.end_date

                    form.fields['award'].required = False
                    form.fields['quota'].required = False
                    form.fields['end_date'].required = False
                    form.fields['sticker_text'].required = False

                    if form.is_valid():
                        form_obj = form.save(commit=False)
                        form_obj.award = award
                        form_obj.quota = quota
                        form_obj.end_date = end_date
                        form_obj.advertiser = advertiser
                        form_obj.save()

                        # form.save()
                        messages.success(request, 'Акция отредактирована')
                        return HttpResponseRedirect('/company/list_campaigns/')
                    else:
                        messages.error(request, form.errors)
                        return render(request, 'company/create_campaign.html', {'form': form, 'form_type': "edit", 'obj_id': pk})
            except:
                form = CampaignForm(request.POST,request.FILES)
                messages.error(request, "Ошибка редактирования акции 0051")
                return render(request, 'company/create_campaign.html', {'form': form, 'form_type': "edit", 'obj_id': pk})


def remove_campaign(request, pk):
    try:
        advertiser = Advertiser.objects.get(owner_user=request.user)
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.advertiser == advertiser:
            if campaign.active_applications_count() == 0 and campaign.sticker_applications_count() == 0:
                campaign_balance = campaign.campaign_balance

                applications = CampaignApplication.objects.filter(campaign=campaign)
                if campaign.campaign_image:
                    delete(campaign.campaign_image)
                applications.delete() # TODO don't delete - just change status
                campaign.delete()

                new_object = Billing_history.objects.create(advertiser=advertiser, balance_increase=campaign_balance, change_type=5)

                messages.success(request, 'Акция удалена')
                return HttpResponseRedirect('/company/list_campaigns/')
            else:
                return HttpResponse(u'Эту акцию нельзя удалять так как в ней есть участники')
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
    # except Exception as e:
    #     print ('%s (%s)' % (e.message, type(e)))
        return HttpResponse(u'Ошибка выполнения')


def archive_campaign(request, pk):
    try:
        advertiser = Advertiser.objects.get(owner_user=request.user)
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.advertiser == advertiser:
            if campaign.active_applications_count() == 0 and campaign.sticker_applications_count() == 0:
                campaign_balance = campaign.campaign_balance

                applications = CampaignApplication.objects.filter(campaign=campaign)

                # if campaign.campaign_image:
                #     delete(campaign.campaign_image)
                # applications.delete() # TODO don't delete - just change status
                # campaign.delete()

                new_object = Billing_history.objects.create(advertiser=advertiser, balance_increase=campaign_balance, change_type=5)

                # campaign.campaign_balance = 0
                campaign.campaign_status = 4  # Пометка кампании как завершенной
                campaign.save()

                campaign_balance_history_object = CampaignBalanceHistory.objects.create(advertiser=advertiser, campaign=campaign, balance_decrease=campaign_balance, change_type=4)

                messages.success(request, 'Акция остановлена')
                return HttpResponseRedirect('/company/list_campaigns/')
            else:
                return HttpResponse(u'Эту акцию нельзя остановить так как в ней есть участники')
        else:
            return HttpResponse(u'Ошибка доступа')
    except:
    # except Exception as e:
    #     print ('%s (%s)' % (e.message, type(e)))
        return HttpResponse(u'Ошибка выполнения')


class UserData(generic.TemplateView):
    template_name = 'company/user_data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['business_types'] = BusinessType.objects.all

        context['form'] = CompanyProfileForm()
        context['main_name'] = 'Данные компании'
        context['title_1'] = "Профиль"
        context['title_2'] = "Профиль"

        return context


def save_user_data(request):
    if request.method == 'POST':
        inst = Advertiser.objects.filter(owner_user=request.user.id).first()
        if not inst:
            inst = Advertiser(owner_user=request.user)

        form = CompanyProfileForm(request.POST, request.FILES, instance=inst)

        if form.is_valid():
            kassir_login = form.cleaned_data.get("kassir_login")
            kassir_password = form.cleaned_data.get("kassir_password")

            # form.save()
            form_obj = form.save(commit=False)

            if kassir_login != '' and kassir_password != '':
                test_exist_username = User.objects.filter(username=kassir_login)

                if not inst.kassir_user:
                    if test_exist_username.count() == 0:
                        user = User.objects.create(username=kassir_login, email=kassir_login)
                        user.set_password(kassir_password)
                        user.save()
                        profile = UserProfile.objects.create(user=User.objects.filter(username=kassir_login).first(), user_role=4, phone=kassir_login)
                        inst.kassir_user = User.objects.filter(username=kassir_login).first()
                        inst.save()
                    else:
                        form_obj.kassir_login = ""
                        form_obj.kassir_password = ""
                        messages.error(request, "Такой логин занят. Нужно выбрать другой!")
                        return HttpResponseRedirect('/company/user_data/')
                else:
                    if test_exist_username.count() == 0 or test_exist_username.first().pk == inst.kassir_user.pk:
                        user = inst.kassir_user
                        user.username = kassir_login
                        user.set_password(kassir_password)
                        user.save()
                    else:
                        form_obj.kassir_login = inst.kassir_user
                        form_obj.kassir_password = inst.kassir_password
                        messages.error(request, "Такой логин занят. Нужно выбрать другой!")
                        return HttpResponseRedirect('/company/user_data/')

            form_obj.save()

        # if "image_remove" in form.data:
            #     delete(inst.company_logo)

            messages.success(request, 'Данные профиля сохранены')
            return HttpResponseRedirect('/company/')
        else:
            messages.error(request, form.errors)
            return HttpResponseRedirect('/company/user_data/')
    else:
        form = CompanyProfileForm()
        messages.error(request, "Ошибка GET запроса 0050")
        return HttpResponseRedirect('/company/user_data/')


class BonusChangesView(generic.ListView):
    template_name = 'company/bonus_changes_history.html'
    model = ClientBalanceHistory

    def get_queryset(self):
        advertiser = Advertiser.objects.get(owner_user=self.request.user)
        return ClientBalanceHistory.objects.filter(advertiser=advertiser, change_type=4)

    def get_context_data(self, **kwargs):
        context = super(BonusChangesView, self).get_context_data(**kwargs)
        context['title_1'] = "История списаний баллов"
        context['title_2'] = "История списаний баллов"

        context['yesterday'] = datetime.today() - timedelta(days=1)

        return context


# RoboKassa
class SelectPaymentView(generic.TemplateView):
    template_name = 'company/select_payment.html'

    def get_context_data(self, **kwargs):
        context = super(SelectPaymentView, self).get_context_data(**kwargs)
        context['title_1'] = "Выбор способа оплаты"
        context['title_2'] = "Выбор способа оплаты"

        return context


def pay_with_robokassa(request):
    advertiser = Advertiser.objects.filter(owner_user=request.user.id).first()
    order = Order.objects.filter(order_status=1, advertiser=advertiser).first()

    breadcrumbs = [
        {'url': '/company/select_payment/', 'text': 'Выбор способа оплаты'}
    ]
    title_2 = "Робокасса"

    if not order:
        print("create order")

        order = Order (
            advertiser = advertiser,
            payment_method = 1,
            order_status = 1
        )
        order.save()

    form = RobokassaForm(initial={
        'InvId': order.id,
    })
    return render(request, 'company/pay_with_robokassa.html', {'form': form, 'title_2': title_2, 'breadcrumbs': breadcrumbs})


from robokassa.signals import result_received

def payment_received(sender, **kwargs):
    print("payment_received")
    order = Order.objects.get(id=kwargs['InvId'])
    # advertiser = order.advertiser
    advertiser = Advertiser.objects.get(pk=order.advertiser.pk)

    # print (kwargs['OutSum'])
    order.order_status = 2
    order.summ = kwargs['OutSum']
    order.save()

    # advertiser.update(balance=F('balance') + order.summ)
    # try:
    new_object = Billing_history.objects.create(advertiser=advertiser, balance_increase=order.summ, change_type=3)
    # except:
    #     print("Billing_history was NOT created")
    #     pass


result_received.connect(payment_received)
