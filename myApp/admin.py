from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.db import models
from .models import User, TrainRoute, Station, Ticket, UserTicket, ActiveMembership

# Get the custom User model
User = get_user_model()

# Monkey-patch the LogEntry model to use the custom User model
LogEntry.user.field.remote_field.model = User

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('created_at',)

class StationInline(admin.TabularInline):
    model = Station
    extra = 1 

@admin.register(TrainRoute)
class TrainRouteAdmin(admin.ModelAdmin):
    inlines = [StationInline]
    list_display = ('train_line', 'distance', 'price')
    search_fields = ('train_line',)

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'route')
    list_filter = ('route',)
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_type', 'route')
    list_filter = ('ticket_type', 'route')
    search_fields = ('route__train_line',)

@admin.register(UserTicket)
class UserTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket', 'confirmed', 'payment_type')
    list_filter = ('confirmed', 'payment_type')
    search_fields = ('user__email', 'payment_info')
    raw_id_fields = ('user', 'ticket')

@admin.register(ActiveMembership)
class ActiveMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_ticket_type', 'start_date', 'end_date', 'is_active', 'days_remaining')
    list_filter = ('user_ticket__ticket__ticket_type', 'start_date')
    search_fields = ('user__email',)
    raw_id_fields = ('user', 'user_ticket')
    readonly_fields = ('is_active', 'days_remaining')
    
    def get_ticket_type(self, obj):
        return obj.user_ticket.ticket.ticket_type
    get_ticket_type.short_description = 'Ticket Type'
    get_ticket_type.admin_order_field = 'user_ticket__ticket__ticket_type'