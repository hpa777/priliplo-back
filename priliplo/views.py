from datetime import date, datetime
from django.views import generic
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random, string

from company.models import Advertiser, Campaign, BusinessType
from page.models import Page
from .settings import EMAIL_ADMINISTRATOR
from .forms import UserRegistrationForm
from client.models import UserProfile, CampaignApplication, PhotoReport
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
import json
from django.db.models import F, Q
from django.utils import timezone

# FOR WEB_PUSH
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from webpush import send_user_notification
import json


#
# def login_in(request):
#     username = request.POST['username']
#     try:
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         login(request, user)
#
#         return HttpResponseRedirect('/client')
#     except:
#         return render(request, 'login.html', {'err': 1, 'username': username})
#
#
# def password_restore(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         if (User.objects.filter(email=email).count() > 0):
#
#             user = User.objects.filter(email=email).first()
#
#             rid = ''
#             for x in range(8):
#                 rid += random.choice(('!@#$%^&*()_-+=' if 0 else '') + string.ascii_letters + string.digits)
#             user.set_password(str(rid))
#             user.save()
#             send_message = '<h2>Ваши данные для сайта Прилипло</h2>'
#             send_message = send_message + '<b>Логин:</b> ' + user.username + '<br><br>'
#             send_message = send_message + '<b>Пароль:</b> ' + str(rid) + '<br><br>'
#
#             send_mail('Восстановление пароля в сервисе Прилипло', send_message, settings.EMAIL_HOST_USER, [email], html_message=send_message)
#
#             return render(request, 'login.html', {'err': 2, 'username': ''})
#
#         else:
#             return render(request, 'login.html', {'err': 3, 'username': ''})
#
#
# def log_out(request):
#     logout(request)
#     return HttpResponseRedirect('/login')
#

def login_in_as_user(request):
    return False
    # user = User.objects.get(username='s.conovalowa@mail.ru')
    # user = User.objects.get(username='scherbinin.alexander2016@yandex.ru')
    user = User.objects.get(username='ramzaev-denis@mail.ru')
    # user = User.objects.get(username='khalin@bk.ru')

    # new_created_date = datetime(year=2021, month=10, day=17)
    # instance = CampaignApplication.objects.filter(id=25).update(edited_date=new_created_date)
    # instance = PhotoReport.objects.filter(id=28).update(created_date=new_created_date)
    # instance = PhotoReport.objects.filter(id=28).update(edited_date=new_created_date)

    login(request, user)
    return HttpResponseRedirect('/client')


def login_in(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        # username = "".join( x for x in username if (x.isalnum() or x in "._@"))

        try:
            user_get = User.objects.get(email=username)
            auth_user = user_get.username
        except:
            try:
                username = "".join(x for x in username if x.isalnum())
                user_get = UserProfile.objects.get(phone=username)
                auth_user = user_get.user.username
            except:
                try:
                    user_get = User.objects.get(username=username)
                    auth_user = user_get.username
                except:
                    auth_user = ""

        user = authenticate(username=auth_user, password=password)
        login(request, user)

        # if request.user.has_perm('superuser'):
        #     return HttpResponseRedirect('/admin_users/')

        user_role = UserProfile.objects.get(user=user).user_role

        if user_role == 1:
            return HttpResponseRedirect('/adminpanel')
        elif user_role == 2:
            return HttpResponseRedirect('/client')
        elif user_role == 3:
            return HttpResponseRedirect('/company')
        elif user_role == 4:
            return HttpResponseRedirect('/kassa')
        else:
            return HttpResponseRedirect('/admin')

    except:
        return render(request, 'auth/login.html', {'err': 1, 'username': username})


def log_out(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        # print(user_form.data['phone'])
        if user_form.is_valid():
            # print(user_form)
            # print(user_form.data)
            # print(user_form.cleaned_data.get("email"))
            # print(user_form.cleaned_data.get("phone"))

            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            # username=new_user.username
            email = new_user.email
            new_user.username = email
            new_user.save()

            own_user = User.objects.filter(email=email).first()

            if user_form.cleaned_data.get("account_type") == 'client':
                user_role = 2
            else:
                user_role = 3
                company = Advertiser.objects.create(
                    owner_user=own_user,
                    company_phone=user_form.cleaned_data.get("phone"),
                    company_fio=user_form.cleaned_data.get("name"),
                    company_name=user_form.cleaned_data.get("company_name"))
                company.save()

            profile = UserProfile.objects.create(
                user=own_user,
                name=user_form.cleaned_data.get("name"),
                phone=user_form.cleaned_data.get("phone"),
                user_role=user_role)
            profile.save()

            login(request, new_user)

            # send_message = '<h2>В сервисе Прилипло зарегистрирован новый пользователь</h2>'
            # send_message = send_message + '<b>Логин:</b> ' + new_user.username + '<br><br>'

            # send_mail('В сервисе Прилипло новый пользователь ', send_message, settings.EMAIL_HOST_USER, [EMAIL_ADMINISTRATOR],
            #           html_message=send_message)

            messages.success(request, 'Вы успешно зарегистрировались')
            if user_role == 2:
                return HttpResponseRedirect('/client/')
            else:
                return HttpResponseRedirect('/company/')
        else:
            messages.error(request, user_form.errors)
            return render(request, 'auth/sign-up.html', {'form': user_form})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'auth/sign-up.html', {'form': user_form})


def password_restore(request):
    if request.method == 'POST':
        email = request.POST['email']
        if (User.objects.filter(email=email).count() > 0):

            user = User.objects.filter(email=email).first()

            rid = ''
            for x in range(8):
                rid += random.choice(('!@#$%^&*()_-+=' if 0 else '') + string.ascii_letters + string.digits)
            user.set_password(str(rid))
            user.save()
            send_message = '<h2>Ваши данные в сервисе Прилипло были изменены</h2>'
            send_message = send_message + '<b>Логин:</b> ' + user.username + '<br><br>'
            send_message = send_message + '<b>Пароль:</b> ' + str(rid) + '<br><br>'

            send_mail('Восстановление пароля в сервисе Прилипло ', send_message, settings.EMAIL_HOST_USER, [email],
                      html_message=send_message)

            messages.success(request, 'Пароль отправлен на указанный email')
            return HttpResponseRedirect('/login/')
            # return render(request, 'auth/login.html', {'err': 2, 'username': ''})

        else:
            messages.error(request, 'Email не найден')
            return render(request, 'auth/password_restore.html', {'email': email})


def soglasie(request):
    return render(request, 'soglasie.html', {'username': request.user.id})


def testpush(request):
    # webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    # vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    # user = request.user
    user = User.objects.get(username='client@priliplo.ru')
    payload = {"head": "Тестовое сообщение", "body": "Вы получили сообщение случайно."}
    send_user_notification(user=user, payload=payload, ttl=1000)

    # return render(request, 'testpush.html', {user: user, 'vapid_key': vapid_key})
    return render(request, 'testpush.html')


# web push отправление
@require_POST
@csrf_exempt
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)
        print(body)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {"head": data['head'], "body": data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})

    ###  Открытая часть сайта


def mainpage(request):
    pageobjects = {}
    pageobjects['advertisers'] = Advertiser.objects.all()
    pageobjects['campaigns'] = Campaign.objects.filter(campaign_status=2)[:6]
    pageobjects['about_text'] = Page.objects.filter(slug="main").first()
    for campaign in pageobjects['campaigns']:
        campaign.award *= 6

    context = get_frontend_data({})

    return render(request, 'frontend/mainpage/mainpage.html', {'username': request.user.id, 'pageobjects': pageobjects, 'mainpage': True, 'menu_categories': context['menu_categories']})


class MainCampaignDescriptionView(generic.DetailView):
    # class ClientAdvDescriptionView(generic.TemplateView):
    template_name = 'frontend/mainpage/campaign.html'
    model = Campaign

    def get_context_data(self, **kwargs):
        context = super(MainCampaignDescriptionView, self).get_context_data(**kwargs)
        # context['campaigns'] = Campaign.objects.filter(campaign_status=2)

        context = get_frontend_data(context)

        context['applications_count'] = context['object'].quota - CampaignApplication.objects.filter(
            campaign=context['object']).filter(
            Q(application_status=1) | Q(application_status=2) | Q(application_status=5) | Q(
                application_status=7)).count()

        # context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(~Q(application_status=0)).first()
        context['award'] = context['object'].award * 6
        context['title_1'] = context['object'].title
        context['breadcrumbs'] = [
            {'url': '/campaigns', 'text': 'Акции'}
        ]
        context['title_2'] = context['object'].advertiser.company_name
        return context


class MainCompanyDescriptionView(generic.DetailView):
    # class ClientAdvDescriptionView(generic.TemplateView):
    template_name = 'frontend/mainpage/company.html'
    model = Advertiser

    def get_context_data(self, **kwargs):
        context = super(MainCompanyDescriptionView, self).get_context_data(**kwargs)

        context = get_frontend_data(context)
        context['pageobjects'] = {}
        context['pageobjects']['campaigns'] = Campaign.objects.filter(advertiser=context['object']).filter(
            campaign_status=2)
        # context['active_applications'] = CampaignApplication.objects.filter(client=self.request.user).filter(Q(application_status=1) | Q(application_status=2) | Q(application_status=5)).first()

        for campaign in context['pageobjects']['campaigns']:
            campaign.award *= 6

        context['title_1'] = context['object'].company_name
        context['title_2'] = "О компании"

        # context['title_2'] = context['object'].advertiser.company_name
        return context


class MainCampaignListView(generic.ListView):
    # class ClientAdvDescriptionView(generic.TemplateView):
    template_name = 'frontend/mainpage/campaigns.html'
    model = Campaign

    def get_context_data(self, **kwargs):
        context = super(MainCampaignListView, self).get_context_data(**kwargs)

        context = get_frontend_data(context)
        context['pageobjects'] = {}

        campaign_id = self.kwargs.get('campaign_id', 0)

        if campaign_id == 0:
            context['pageobjects']['campaigns'] = Campaign.objects.filter(campaign_status=2)
            context['title_1'] = "Все рекламные акции Прилипло"
            context['title_2'] = "Акции"
        else:
            context['pageobjects']['campaigns'] = Campaign.objects.filter(campaign_status=2).filter(advertiser__in=Advertiser.objects.filter(business_type=campaign_id))
            context['title_2'] = BusinessType.objects.get(pk=campaign_id)
            context['title_1'] = context['title_2'].underscored_name
            context['breadcrumbs'] = [
                {'url': '/campaigns', 'text': 'Акции'}
            ]

        for campaign in context['pageobjects']['campaigns']:
            campaign.award *= 6

        context['pageobjects']['advertisers'] = Advertiser.objects.all()

        return context


def get_frontend_data(context):
    context['menu_categories'] = BusinessType.objects.filter(parent_business_type=None)
    return context
