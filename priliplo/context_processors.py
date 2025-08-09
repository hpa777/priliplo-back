from client.models import UserProfile, CompanyProfile
from adminpanel.models import ProjectSettings
from company.models import Advertiser
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings


def user_profile(request):
    usr_profile = UserProfile.objects.filter(user=request.user.id).first()
    documents_settings = ProjectSettings.objects.first()
    full_balance = 0

    if usr_profile:
        for balance_set in usr_profile.user.clientbalance_set.all():
            full_balance = full_balance + balance_set.balance

        # return {"user_profile": usr_profile, "full_balance": int(full_balance), "withdrawals_code": (hash("dsfsdfdfgdfggfgbgfbfgbf1g") % 10**4)}
        balance_str = str("%d-%s-saltsalt" % (int(full_balance), str(date.today().strftime("%d/%m/%Y"))))
        return {"documents_settings": documents_settings, "user_profile": usr_profile, "full_balance": int(full_balance), "withdrawals_code": (hash(balance_str)) % 10**4}
    else:
        return {"documents_settings": documents_settings, "user_profile": usr_profile}


def company_profile(request):
    documents_settings = ProjectSettings.objects.first()
    return {"documents_settings": documents_settings, "company_profile": Advertiser.objects.filter(owner_user=request.user.id).first()}


def kassir_profile(request):
    return {"kassir_profile": Advertiser.objects.filter(kassir_user=request.user.id).first()}

def vapid_key(request):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    return {"vapid_key": webpush_settings.get('VAPID_PUBLIC_KEY')}
