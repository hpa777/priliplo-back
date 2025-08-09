from company.models import Campaign
from django import forms


class CampaignApproveForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('campaign_image',)
