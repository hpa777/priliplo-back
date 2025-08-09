from django.contrib import admin

from company.models import Advertiser, Campaign, Order, Billing_history, AdvertiserSettings, BusinessType, CampaignBalanceHistory

admin.site.register(Advertiser)
admin.site.register(Campaign)
admin.site.register(Order)


class Billing_historyAdmin(admin.ModelAdmin):
    list_display = ('advertiser','balance_increase', 'balance_decrease', 'balance_before', 'balance_current', 'change_type', 'history_description', 'edited_date')
    list_display_links = None
    list_filter = ['advertiser', 'change_type']
    search_fields = ['advertiser__company_name']
    readonly_fields = ["balance_before", "balance_current"]
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        # extra_context['show_save'] = False
        return super(Billing_historyAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

admin.site.register(Billing_history, Billing_historyAdmin)


class CampaignBalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('advertiser','campaign','balance_increase', 'balance_decrease', 'balance_before', 'balance_current', 'change_type', 'history_description', 'edited_date')
    list_display_links = None
    list_filter = ['advertiser', 'campaign', 'change_type']
    search_fields = ['advertiser__company_name']
    readonly_fields = ["balance_before", "balance_current"]
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        # extra_context['show_save'] = False
        return super(CampaignBalanceHistoryAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

admin.site.register(CampaignBalanceHistory, CampaignBalanceHistoryAdmin)


class AdvertiserSettingsAdmin(admin.ModelAdmin):
    # list_display_links = None
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(AdvertiserSettings, AdvertiserSettingsAdmin)


class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ('title','parent_business_type')

admin.site.register(BusinessType, BusinessTypeAdmin)