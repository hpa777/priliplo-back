from django import template

from adminpanel.models import CrmTask
from client.models import CampaignApplication, PhotoReport
from company.models import Advertiser, Campaign
from datetime import datetime, date, timedelta
from django.utils.timezone import get_current_timezone

register = template.Library()


@register.inclusion_tag('client/badge.html')
def show_badge():
    # advertisers = Advertiser.objects.all()
    advertisers = Campaign.objects.filter(campaign_status=2).values('advertiser').distinct()
    return {'numbers': advertisers.count()}

@register.inclusion_tag('adminpanel/badge.html')
def show_badge_sticker_requests():
    num = CampaignApplication.objects.filter(application_status=5)
    return {'numbers': num.count()}

@register.inclusion_tag('adminpanel/badge.html')
def show_badge_campaign_requests():
    num = Campaign.objects.filter(campaign_status=1)
    return {'numbers': num.count()}

@register.inclusion_tag('adminpanel/badge.html')
def show_badge_client_requests_1():
    num = CampaignApplication.objects.filter(application_status=1)
    return {'numbers': num.count()}

@register.inclusion_tag('adminpanel/badge.html')
def show_badge_admin_client_photoreports():
    num = PhotoReport.objects.filter(photoreport_status=1)
    return {'numbers': num.count()}

@register.inclusion_tag('adminpanel/badge.html')
def show_badge_admin_tasks():
    today = datetime.now(tz=get_current_timezone()) - timedelta(days=1)
    num = CrmTask.objects.filter(plane_finish_date__lte=today)
    return {'numbers': num.count()}
