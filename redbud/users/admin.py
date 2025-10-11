from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Training, TrainingModule


class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Role & Permissions'), {'fields': ('role', 'groups', 'user_permissions')}),
        (_('Status'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


class TrainingModuleInline(admin.TabularInline):
    model = TrainingModule
    extra = 1
    readonly_fields = ['created_by']


class TrainingAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'duration_days', 'assigned_trainer', 'is_active', 'created_by']
    list_filter = ['is_active', 'start_date', 'end_date', 'created_by']
    search_fields = ['name', 'description']
    filter_horizontal = ['employees']
    inlines = [TrainingModuleInline]
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    exclude = ['created_by']

    def save_model(self, request, obj, form, change):
        """Set created_by for Training model"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Set created_by for TrainingModule inline instances"""
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not instance.pk:  # Only set for new instances
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()


class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'training', 'order', 'duration_hours', 'created_by', 'created_at']
    list_filter = ['training', 'created_by', 'created_at']
    search_fields = ['title', 'description', 'training__name']
    readonly_fields = ['created_by', 'created_at', 'updated_at']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(TrainingModule, TrainingModuleAdmin)
