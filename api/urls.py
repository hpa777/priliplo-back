from django.urls import include, path  
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from .views import *

router = routers.DefaultRouter()
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [  
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sliders/<slug:slug>/slides/', SliderSlidesAPIView.as_view(), name='slider-slides'),  # GET all slides for a slider by slug
    path('sliders/<slug:slug>/', SliderWithSlidesAPIView.as_view(), name='slider-with-slides'), # GET slider details with associated slides
    path('faq/', FaqViewSet.as_view(), name='faq'),    
    path('dictionary/<slug:locale>/<slug:context>/', dictionary_view, name='dictionary')      
]