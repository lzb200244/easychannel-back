from django.contrib import admin

from apps.chat.models import *


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass


@admin.register(RecordFileInfo)
class RecordFileInfoAdmin(admin.ModelAdmin):
    pass




@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass
