from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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



@api_view(['GET'])
@permission_classes([AllowAny])
def dictionary_view(request, locale, context):    

    qs = Dictionary.objects.filter(
        locale=locale,
        context=context
    ).values('key', 'value')

    return Response({
        item['key']: item['value']
        for item in qs
    })    