from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required, permission_required
from priliplo.decorators import user_is_kassir
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # url(r'^advertiser_desc/(?P<pk>[0-9]+)/$', login_required(views.ClientAdvDescriptionView.as_view()), name='advertiser_desc'),
    # url(r'^photoreport/$', login_required(views.ClientPhotoReportView.as_view()), name='photoreport'),
    # url(r'^save_photoreport/', login_required(views.save_photoreport), name='save_photoreport'),
    # url(r'^user_data/', login_required(views.UserData.as_view()), name='user_data'),
    # url(r'^save_user_data/', login_required(views.save_user_data), name='save_user_data'),
    # url(r'^request_to_campaign/(?P<pk>[0-9]+)/$', login_required(views.request_application_to_campaign), name='request_application_to_campaign'),
    # url(r'^remove_application_from_campaign/(?P<pk>[0-9]+)/$', login_required(views.remove_application_from_campaign), name='remove_application_from_campaign'),
    url(r'^step1/', csrf_exempt(login_required(user_is_kassir(views.step1))), name='step1'),
    url(r'^step2/', csrf_exempt(login_required(user_is_kassir(views.step2))), name='step2'),
    url(r'^step3/', csrf_exempt(login_required(user_is_kassir(views.step3))), name='step3'),
    url(r'^bonus_changes/', login_required(user_is_kassir(views.BonusChangesView.as_view())), name='bonus_changes'),
    url(r'^$', login_required(user_is_kassir(views.KassaMainView.as_view())), name='kassamainpage'),
]

app_name = 'kassa'