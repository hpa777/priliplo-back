from rest_framework import serializers
from company.models import Advertiser, Campaign, BusinessType
from page.models import Slider, Slide

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = '__all__'


class CustomFileRelatedField(serializers.RelatedField):
    def to_representation(self, value):       
        return value.file.url

class SlideSerializer(serializers.ModelSerializer):
    img = CustomFileRelatedField(read_only=True)
    img_tablet = CustomFileRelatedField(read_only=True)
    img_mob = CustomFileRelatedField(read_only=True)
    icon = CustomFileRelatedField(read_only=True)   
    class Meta:
        model = Slide
        fields = '__all__'

class SliderWithSlidesSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True, source='slide_set')
    class Meta:
        model = Slider        
        fields = ['id', 'title', 'slug', 'slides']