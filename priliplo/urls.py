"""priliplo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path as url
from django.views.generic import TemplateView
from . import views
from client.views import ClientMainView

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.conf import settings
# from client import views
from django.contrib.auth.decorators import login_required


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView 

admin.site.site_header = 'Система управления сайтом Прилипло'
admin.site.site_title = 'Система управления сайтом Прилипло'

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path('company/', include('company.urls')),
    path('kassa/', include('kassa.urls')),
    path('page/', include('page.urls')),
    path('adminpanel/', include('adminpanel.urls')),
    path('webpush/', include('webpush.urls')),
    # path('send_push/', views.send_push),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript')),

    url(r'^login/', TemplateView.as_view(template_name="auth/login.html"), name="login"),
    url(r'^password_restore/', TemplateView.as_view(template_name="auth/password_restore.html"), name="pass_restore"),
    url(r'^sign_up/', TemplateView.as_view(template_name="auth/sign-up.html"), name="sign_up"),
    url(r'^login_in/', views.login_in, name="login_in"),
    url(r'^login_in_as_user/', views.login_in_as_user, name="login_in_as_user"),
    url(r'^register/', views.register, name="register"),
    url(r'^pwd_restore/', views.password_restore, name='password_restore'),
    url(r'^login_out/', views.log_out, name="login_out"),
    url(r'^soglasie/', login_required(views.soglasie), name='soglasie'),

    # url(r'^main/', views.mainpage, name='mainpage'),
    url(r'^campaign/(?P<pk>[0-9]+)/$', views.MainCampaignDescriptionView.as_view(), name='main_campaign_desc'),
    url(r'^companies/(?P<pk>[0-9]+)/$', views.MainCompanyDescriptionView.as_view(), name='main_company_desc'),
    url(r'^campaigns/$', views.MainCampaignListView.as_view(), name='campaigns_list'),
    url(r'^campaigns/(?P<campaign_id>\d+)/$', views.MainCampaignListView.as_view(), name='campaigns_list'),
    # url(r'^testpush/', login_required(views.testpush), name='testpush'),
    # url(r'^$', TemplateView.as_view(template_name="auth/login.html"), name="login"),
    url(r'^$', views.mainpage, name='mainpage'),
    # url('$', views.mainpage, name='mainpage'),

    # url('$',login_required(views.ClientMainView.as_view()),name='mainpage'),
    # url('$', ClientMainView.as_view(), name='mainpage'),

    path(r'api/v1/', include(('api.urls', 'api'), namespace='v1')),     
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'), 

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
