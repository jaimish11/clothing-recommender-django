from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from recommender.models import Item

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    search_fields = ['id']
