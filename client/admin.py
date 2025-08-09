from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from django.db.models import F, Value, BooleanField, CharField

from .models import UserProfile, Country, City, District, Odometer, AutoType, CampaignApplication, AutoModel, AutoMarka, PhotoReport, CompanyProfile, ClientBalance, ClientBalanceHistory
from company.models import Advertiser
from django.contrib import admin
from django.contrib.auth import admin as upstream
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext, ugettext_lazy as _

admin.site.register(Country)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Odometer)
admin.site.register(AutoType)
admin.site.register(AutoMarka)
admin.site.register(AutoModel)
# admin.site.register(PhotoReport)
admin.site.register(ClientBalance)


class CampaignApplicationAdmin(admin.ModelAdmin):
    list_display = ('client', 'advertiser', 'campaign', 'application_status', 'created_date', 'edited_date')


admin.site.register(CampaignApplication, CampaignApplicationAdmin)
# admin.site.register(ClientBalanceHistory)

class ClientBalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('client', 'advertiser', 'balance_increase', 'balance_decrease', 'balance_before', 'balance_current', 'change_type', 'history_description', 'edited_date')
    list_display_links = None
    search_fields = ['advertiser__username', 'client']
    readonly_fields = ["balance_before", "balance_current"]
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super(ClientBalanceHistoryAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


admin.site.register(ClientBalanceHistory, ClientBalanceHistoryAdmin)


class UserAdmin(upstream.UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    form = UserChangeForm
    add_form = UserCreationForm


try:
    admin.site.unregister(User)
except:
    pass

admin.site.register(User, UserAdmin)

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class CompanyProfileInline(admin.StackedInline):
    model = Advertiser
    fk_name = "owner_user"


class PhotoReportAdmin(admin.ModelAdmin):
    list_display = ['client', 'created_date', 'edited_date', 'photoreport_status', 'advertiser', 'campaign']


admin.site.register(PhotoReport, PhotoReportAdmin)


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, CompanyProfileInline]
    list_display = ['username', 'get_fio', 'get_company_fio', 'get_role', 'get_phone', 'date_joined']

    # list_filter = ['username']
    # def get_balance(self, obj):
    #     return UserProfile.objects.get(user=obj).in_index
    #
    # get_balance.admin_order_field = 'userprofile__in_index'
    #
    # get_balance.short_description = 'Показывать'
    # get_balance.boolean = True

    def get_fio(self, obj):
        return UserProfile.objects.get(user=obj).name
        # return UserProfile.objects.get(user=obj).last_name+" "+UserProfile.objects.get(user=obj).name+" "+UserProfile.objects.get(user=obj).surname_name

    def get_company_fio(self, obj):
        return Advertiser.objects.get(owner_user=obj).company_fio

    def get_role(self, obj):
        return UserProfile.objects.get(user=obj).get_user_role_display()
        # UserProfile.objects.get(user=obj)._meta.get_field('user_role').choices

    def get_phone(self, obj):
        return UserProfile.objects.get(user=obj).phone

    #
    # get_fio.admin_order_field = 'userprofile__last_name'
    #
    # get_fio.short_description = 'ФИО'


admin.site.register(User, UserProfileAdmin)
