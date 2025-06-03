from django.contrib import admin
from .models import Admin, Room, Booking, BookingMessage, AdminMessage
from django.contrib.auth.models import User

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_super_admin', 'created_at')
    list_filter = ('is_super_admin',)
    search_fields = ('user__username', 'phone_number')

@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'message')
    date_hierarchy = 'created_at'

    def short_message(self, obj):
        return obj.short_message
    short_message.short_description = 'Message'

admin.site.register(Room)
admin.site.register(Booking)