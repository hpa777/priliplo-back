from . import views
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import include
from django.urls import re_path as url
from django.views.generic import TemplateView
from priliplo.decorators import user_is_company

urlpatterns = [
    url(r'^robokassa/', include('robokassa.urls')),
    url(r'^campaign_desc/(?P<pk>[0-9]+)/$', login_required(user_is_company(views.CampaignDescriptionView.as_view())), name='campaign_desc'),
    url(r'^create_campaign/', login_required(user_is_company(views.CreateCampaignView.as_view())), name='create_campaign'),
    url(r'^edit_campaign/(?P<pk>[0-9]+)/$', login_required(user_is_company(views.EditCampaignView.as_view())), name='edit_campaign'),
    url(r'^remove_campaign/(?P<pk>[0-9]+)/$', login_required(user_is_company(views.remove_campaign)), name='remove_campaign'),
    url(r'^archive_campaign/(?P<pk>[0-9]+)/$', login_required(user_is_company(views.archive_campaign)), name='archive_campaign'),
    url(r'^application_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', login_required(user_is_company(views.application_action)), name='application_action'),
    url(r'^photoreport_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', login_required(user_is_company(views.photoreport_action)), name='photoreport_action'),
    url(r'^save_campaign_data/', login_required(user_is_company(views.save_campaign_data)), name='save_campaign_data'),
    url(r'^user_data/', login_required(user_is_company(views.UserData.as_view())), name='user_data'),
    url(r'^save_user_data/', login_required(user_is_company(views.save_user_data)), name='save_user_data'),
    url(r'^client_photoreports', login_required(user_is_company(views.ClientPhotoReportView.as_view())), name='client_photoreports'),
    url(r'^client_requests', login_required(user_is_company(views.ClientRequestsView.as_view())), name='client_requests'),
    url(r'^list_campaigns/', login_required(user_is_company(views.AdvertiserListCampaigns.as_view())), name='list_campaigns'),
    url(r'^balance_history/', login_required(user_is_company(views.BalanceHistoryView.as_view())), name='balance_history'),
    url(r'^bonus_changes/', login_required(user_is_company(views.BonusChangesView.as_view())), name='bonus_changes'),
    url(r'^select_payment/', login_required(user_is_company(views.SelectPaymentView.as_view())), name='select_payment'),
    url(r'^pay_with_robokassa/', login_required(user_is_company(views.pay_with_robokassa)), name='pay_with_robokassa'),

    # url(r'^temp_create_campaign/', TemplateView.as_view(template_name="company/create_campaign_temp.html"), name="create_campaign_temp"),
    url(r'^create_campaign_wizard/', login_required(user_is_company(views.CreateCampaignViewWizard.as_view())), name='create_campaign_wizard'),

    url(r'^$', login_required(user_is_company(views.AdvertiserMainView.as_view())), name='companymainpage'),
]

app_name = 'company'