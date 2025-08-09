from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required, permission_required
from priliplo.decorators import user_is_client


urlpatterns = [
    # url(r'^news_detail/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # url(r'^news_list/(?P<slug>[\w-]+)$', views.ListView.as_view(), name='list_all'),
    # url(r'^getoldnews/?$', views.LoadOldNews.as_view(), name='oldnews'),
    url(r'^advertiser_desc/(?P<pk>[0-9]+)/$',  login_required(user_is_client(views.ClientAdvDescriptionView.as_view())), name='advertiser_desc'),
    url(r'^photoreport/$',  login_required(user_is_client(views.ClientPhotoReportView.as_view())), name='photoreport'),
    url(r'^photoreports_history/$',  login_required(user_is_client(views.ClientPhotoReportsHistoryView.as_view())), name='photoreports_history'),
    url(r'^save_photoreport/',  login_required(user_is_client(views.save_photoreport)), name='save_photoreport'),
    url(r'^upload_auto_data/',  login_required(user_is_client(views.upload_auto_data.as_view())), name='upload_auto_data'),

    url(r'^user_data/',  login_required(user_is_client(views.UserData.as_view())), name='user_data'),
    url(r'^save_user_data/',  login_required(user_is_client(views.save_user_data)), name='save_user_data'),
    url(r'^request_to_campaign/(?P<pk>[0-9]+)/$',  login_required(user_is_client(views.request_application_to_campaign)), name='request_application_to_campaign'),
    url(r'^remove_application_from_campaign/(?P<pk>[0-9]+)/$',  login_required(user_is_client(views.remove_application_from_campaign)), name='remove_application_from_campaign'),
    url(r'^bonus_changes/',  login_required(user_is_client(views.BonusChangesView.as_view())), name='bonus_changes'),
    url(r'^advertisers/$',  login_required(user_is_client(views.ClientMainView.as_view()), {'advertisers_list': True}), name='advertisers'),

    url(r'^$', login_required(user_is_client(views.ClientMainView.as_view())), name='clientmainpage'),
]

app_name = 'client'