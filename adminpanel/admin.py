from django.contrib import admin

from adminpanel.models import CrmTask, CrmTaskGroup, ProjectSettings

admin.site.register(CrmTask)
admin.site.register(CrmTaskGroup)
admin.site.register(ProjectSettings)
