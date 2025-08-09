from .models import Campaign
from django import forms

class CreateCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        # fields = ('title', 'campaign_image', 'short_description', 'award', 'end_date', 'quota')
        fields = ('title', 'logo_image', 'short_description', 'award', 'end_date', 'quota')

    # def clean_visible(self):
    #     data = self.data.copy()
    #     data['in_index'] = False
    #     self.data = data