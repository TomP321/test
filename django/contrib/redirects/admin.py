from django.contrib import admin
from django.contrib.redirects.models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('redirect_type', 'old_path', 'new_path')
    list_filter = ('redirect_type', 'site',)
    search_fields = ('old_path', 'new_path')
    radio_fields = {'site': admin.VERTICAL}
