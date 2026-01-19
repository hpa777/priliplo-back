from rest_framework import viewsets, permissions, generics
from company.models import Advertiser, Campaign, BusinessType
from .serializers import *
from django.http import Http404
from page.models import Dictionary

class CampaignViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]    
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    

class FaqViewSet(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FaqSerializer
    queryset = Faq.objects.all().order_by('rank')

class SliderSlidesAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SlideSerializer    
    def get_queryset(self):
        """
        Возвращает список слайдов для слайдера с указанным slug.
        """
        slug = self.kwargs['slug']
        try:
            slider = Slider.objects.get(slug=slug)
        except Slider.DoesNotExist:
           raise Http404

        return Slide.objects.filter(slider=slider).order_by('rank')
    

class SliderWithSlidesAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]    
    serializer_class = SliderWithSlidesSerializer
    queryset = Slider.objects.all()
    lookup_field = 'slug' # Use slug instead of pk
    lookup_url_kwarg = 'slug'


class DictionaryViewSet(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]    
    serializer_class = DictionarySerializer
    def get_queryset(self):
        locale = self.kwargs['locale']
        context = self.kwargs['context']
        return Dictionary.objects.filter(locale=locale, context=context)
    