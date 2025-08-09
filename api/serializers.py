from rest_framework import serializers
from company.models import Advertiser, Campaign, BusinessType

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'