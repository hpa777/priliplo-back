from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from company.models import Advertiser
from client.models import UserProfile, ClientBalanceHistory
from datetime import datetime, timedelta, date
import requests
import time
import random
import string

from kassa.models import SmsCode


class KassaMainView(generic.TemplateView):
    template_name = 'kassa/kassa_main.html'

    def get_context_data(self, **kwargs):
        context = super(KassaMainView, self).get_context_data(**kwargs)
        context['title_1'] = "Кабинет кассира"
        # context['title_2'] = Advertiser.objects.get(kassir_user=self.request.user)
        context['title_2'] = "Списание баллов"

        return context


@csrf_exempt
def step1(request):
    if request.method == 'POST':
        phone=request.POST.get('client_phone', False)
        if phone:
            phone = "".join(x for x in phone if x.isalnum())
            # return HttpResponse("ok")
            try:
                client = UserProfile.objects.get(phone=phone, user_role=2)
                advertiser = Advertiser.objects.get(kassir_user=request.user)
                clientbalance = client.user.clientbalance_set.filter(advertiser=advertiser).first().balance
                return JsonResponse({'status': 'ok', 'phone': phone, 'user': client.name, 'client_id': client.pk, 'user_balance': clientbalance})
            except:
                return JsonResponse({'status': 'error', 'message': 'Телефон не найден'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Необходимо заполнить заполнить поле телефон'})
            # return HttpResponse('Необходимо заполнить заполнить поле телефон')


@csrf_exempt
def step2(request):
    MAX_RETRIES = 2  # Arbitrary number of times we want to try
    if request.method == 'POST':
        balance_decrease=request.POST.get('balance_decrease', False)
        client_id=request.POST.get('client_id', False)
        if balance_decrease:
            if float(balance_decrease) > 0:
                client = UserProfile.objects.get(pk=client_id)
                advertiser = Advertiser.objects.get(kassir_user=request.user)
                clientbalance = client.user.clientbalance_set.filter(advertiser=advertiser).first().balance

                if float(clientbalance) >= float(balance_decrease):
                    # создать код подтвежения
                    full_balance = 0
                    for balance_set in client.user.clientbalance_set.all():
                        full_balance = full_balance + balance_set.balance
                    balance_str = str("%d-%s-saltsalt" % (int(full_balance), str(date.today().strftime("%d/%m/%Y"))))
                    original_sms_code = (hash(balance_str)) % 10**4

                    sms_code = SmsCode(client=client.user, advertiser=advertiser, balance=float(balance_decrease), code=original_sms_code)
                    sms_code.save()
                    return JsonResponse({'status': 'ok'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'У клиента не достаточно баллов для снятия'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Снять баллов нужно больше нуля'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Необходимо заполнить заполнить поле баланс'})


@csrf_exempt
def step2_BACKUP_SMS(request): # Раньше баллы списывались через отправку смс
    MAX_RETRIES = 2  # Arbitrary number of times we want to try
    if request.method == 'POST':
        balance_decrease=request.POST.get('balance_decrease', False)
        client_id=request.POST.get('client_id', False)
        if balance_decrease:
            if float(balance_decrease) > 0:
                client = UserProfile.objects.get(pk=client_id)
                advertiser = Advertiser.objects.get(kassir_user=request.user)
                clientbalance = client.user.clientbalance_set.filter(advertiser=advertiser).first().balance

                if float(clientbalance) >= float(balance_decrease):
                    # apiKey=823-5ZDNBHjWnyZZ&SenderId=Nevesomost&UseRecepientTimeZone=True&PhoneNumber=11&Text=Сообщение
                    attempt_num = 0  # keep track of how many times we've retried
                    char_set = string.digits
                    rnd_code = ''.join(random.sample(char_set*6, 6))
                    while attempt_num < MAX_RETRIES:
                        headers = {"Accept": "application/json", "Content-Type": "application/json"}
                        data = {
                            "apiKey": "823-5ZDNBHjWnyZZ",
                            "SenderId": "Nevesomost",
                            "UseRecepientTimeZone": "False",
                            "PhoneNumber": str(client.phone),
                            "Text": "Для списания баллов сообщите сотруднику код: " + str(rnd_code),
                        }

                        r = requests.post("https://api.aramba.ru/singleSms", headers=headers, json=data, verify=False)
                        if r.status_code == 200:
                            data = r.json()
                        # if 1:

                            sms_code = SmsCode(client=client.user, advertiser=advertiser, balance=float(balance_decrease), code=rnd_code)
                            sms_code.save()

                            return JsonResponse({'status': 'ok'})
                        else:
                            attempt_num += 1
                            # You can probably use a logger to log the error here
                            time.sleep(2)  # Wait for 5 seconds before re-trying
                    return JsonResponse({'status': 'error', 'message': 'Сервис отправки СМС не доступен. Свяжитесь со службой поддержки.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'У клиента не достаточно баллов для снятия'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Снять баллов нужно больше нуля'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Необходимо заполнить заполнить поле баланс'})


@csrf_exempt
def step3(request):
    if request.method == 'POST':
        sms_code=request.POST.get('sms_code', False)
        client_id=request.POST.get('client_id', False)

        if sms_code and client_id:
            try:
                client = UserProfile.objects.get(pk=client_id)
                advertiser = Advertiser.objects.get(kassir_user=request.user)
                clientbalance = client.user.clientbalance_set.filter(advertiser=advertiser).first().balance

                try:
                    original_sms_code = SmsCode.objects.filter(client=client.user, advertiser=advertiser, code=sms_code).first()
                    if original_sms_code.code == sms_code:
                        decrease_balance = original_sms_code.balance

                        client_balance_history = ClientBalanceHistory.objects.create(
                            client=client.user,
                            advertiser=advertiser,
                            balance_decrease=decrease_balance,
                            change_type=4
                        )

                        SmsCode.objects.filter(client=client.user, advertiser=advertiser).delete()

                        return JsonResponse({'status': 'ok'})
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Код списания не правильный'})
                except:
                    return JsonResponse({'status': 'error', 'message': 'Код списания не правильный'})
            except:
                return JsonResponse({'status': 'error', 'message': 'Ошибка приложения номер 075. Обновите страницу и попробуйте снова.'})

        else:
            return JsonResponse({'status': 'error', 'message': 'На сервере приложения произошел сбой. Обновите страницу и попробуйте снова.'})


class BonusChangesView(generic.ListView):
    template_name = 'kassa/bonus_changes_history.html'
    model = ClientBalanceHistory

    def get_queryset(self):
        advertiser = Advertiser.objects.get(kassir_user=self.request.user)
        return ClientBalanceHistory.objects.filter(advertiser=advertiser, change_type=4)

    def get_context_data(self, **kwargs):
        context = super(BonusChangesView, self).get_context_data(**kwargs)
        context['title_1'] = "История списаний баллов"
        context['title_2'] = "История списаний баллов"

        context['yesterday'] = datetime.today() - timedelta(days = 1 )

        return context
