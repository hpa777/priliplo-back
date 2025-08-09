from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.PageView.as_view(), name='pagedetail'),
]
