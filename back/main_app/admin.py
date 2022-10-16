from django.contrib import admin
from main_app.models import Frame, Rock


class FrameAdmin(admin.ModelAdmin):
    list_display = ('fullness', 'timestamp')


class RockAdmin(admin.ModelAdmin):
    list_display = ('frame', 'max_size')


admin.site.register(Frame, FrameAdmin)
admin.site.register(Rock, RockAdmin)