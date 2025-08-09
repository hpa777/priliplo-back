from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^campaign_desc/(?P<pk>[0-9]+)/$', views.CampaignDescriptionView.as_view(), name='campaign_desc'),
    # url(r'^photoreport/$', views.AdvertiserPhotoReportView.as_view(), name='advertiser_photoreports'),
    url(r'^$', views.AdvertiserMainView.as_view(), name='companymainpage'),
]

app_name = 'advertiser'