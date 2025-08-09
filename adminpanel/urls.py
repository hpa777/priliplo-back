from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required, permission_required
from priliplo.decorators import user_is_admin


urlpatterns = [
    # url(r'^advertiser_desc/(?P<pk>[0-9]+)/$', login_required(views.ClientAdvDescriptionView.as_view()), name='advertiser_desc'),
    # url(r'^photoreport/$', login_required(views.ClientPhotoReportView.as_view()), name='photoreport'),
    # url(r'^save_photoreport/', login_required(views.save_photoreport), name='save_photoreport'),
    # url(r'^user_data/', login_required(views.UserData.as_view()), name='user_data'),
    # url(r'^save_user_data/', login_required(views.save_user_data), name='save_user_data'),
    # url(r'^request_to_campaign/(?P<pk>[0-9]+)/$', login_required(views.request_application_to_campaign), name='request_application_to_campaign'),
    # url(r'^remove_application_from_campaign/(?P<pk>[0-9]+)/$', login_required(views.remove_application_from_campaign), name='remove_application_from_campaign'),
    url(r'^advertisers_list', user_is_admin(login_required(views.AdvertisersListView.as_view())), name='advertisers_list'),
    url(r'^advertiser_desc/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.AdminAdvDescriptionView.as_view())), name='advertiser_desc'),
    url(r'^advertiser_remove/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.advertiser_remove)), name='advertiser_remove'),


    url(r'^client_photoreports', user_is_admin(login_required(views.ClientPhotoReportView.as_view())), name='admin_client_photoreports'),
    url(r'^photoreport_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', user_is_admin(login_required(views.photoreport_action)), name='photoreport_action'),
    url(r'^client_requests/(?P<app_type>[0-9]+)/', user_is_admin(login_required(views.ClientRequestsView.as_view())), name='client_requests'),
    url(r'^client_desc/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.AdminClientDescriptionView.as_view())), name='client_desc'),
    url(r'^all_clients/', user_is_admin(login_required(views.AllClientsView.as_view())), name='all_clients'),
    url(r'^admin_photoreport/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.AdminPhotoReportView.as_view())), name='admin_photoreport'),
    url(r'^save_photoreport/', user_is_admin(login_required(views.save_photoreport)), name='save_photoreport'),
    url(r'^application_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', user_is_admin(login_required(views.application_action)), name='application_action'),
    url(r'^save_stiker_reserve_date/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.save_stiker_reserve_date)), name='save_stiker_reserve_date'),
    url(r'^sticker_requests', user_is_admin(login_required(views.StickerRequestsView.as_view())), name='sticker_requests'),
    url(r'^campaign_requests', user_is_admin(login_required(views.CampaignRequestsView.as_view())), name='campaign_requests'),
    url(r'^campaign_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', user_is_admin(login_required(views.campaign_action)), name='campaign_action'),
    url(r'^application_campaign_action/(?P<pk>[0-9]+)/(?P<action>[0-9]+)/$', user_is_admin(login_required(views.application_campaign_action)), name='application_campaign_action'),

    url(r'^todo_list', user_is_admin(login_required(views.TodoListView.as_view())), name='todo_list'),
    url(r'^create_task/', user_is_admin(login_required(views.CreateTodoTaskView.as_view())), name='create_task'),
    url(r'^edit_task/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.EditTodoTaskView.as_view())), name='edit_task'),
    url(r'^view_task/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.ShowTodoTaskView.as_view())), name='view_task'),
    url(r'^remove_task/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.remove_task)), name='remove_task'),
    url(r'^change_task_status/(?P<pk>[0-9]+)/(?P<status>[0-9]+)/$', user_is_admin(login_required(views.change_task_status)), name='change_task_status'),
    url(r'^save_task_data/', user_is_admin(login_required(views.save_task_data)), name='save_task_data'),
    url(r'^login_in_as_user/(?P<user_id>[0-9]+)/$', user_is_admin(login_required(views.login_in_as_user)), name='login_in_as_user'),
    #####

    url(r'^todo_group_list', user_is_admin(login_required(views.TodoGroupListView.as_view())), name='todo_group_list'),
    url(r'^create_task_group/', user_is_admin(login_required(views.CreateTodoTaskGroupView.as_view())), name='create_task_group'),
    url(r'^edit_task_group/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.EditTodoTaskGroupView.as_view())), name='edit_task_group'),
    url(r'^remove_task_group/(?P<pk>[0-9]+)/$', user_is_admin(login_required(views.remove_task_group)), name='remove_task_group'),
    url(r'^save_task_group_data/', user_is_admin(login_required(views.save_task_group_data)), name='save_task_group_data'),
    url(r'^todo_auto_search/', user_is_admin(login_required(views.todo_auto_search)), name='todo_auto_search'),

    url(r'^$', user_is_admin(login_required(views.AdminMainView.as_view())), name='adminmainpage'),
]
app_name = 'adminpanel'