from django.contrib import admin

from apps.chat.models import *


@admin.register(GroupRecords)
class RecordAdmin(admin.ModelAdmin):
    pass







@admin.register(GroupRoom)
class RoomAdmin(admin.ModelAdmin):
    pass
