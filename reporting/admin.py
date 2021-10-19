from django.contrib import admin
from .models import Representative, Committee, Meeting, Report

admin.site.register(Representative)
admin.site.register(Committee)
admin.site.register(Meeting)
admin.site.register(Report)