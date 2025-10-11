from django.contrib import admin
from .models import Content


class ContentAdmin(admin.ModelAdmin):
    """
    Admin interface for Content model
    """
    list_display = ['title', 'training', 'content_type', 'order', 'is_active', 'created_by', 'created_at']
    list_filter = ['content_type', 'is_active', 'training', 'created_by', 'created_at']
    search_fields = ['title', 'description', 'training__name']
    readonly_fields = ['created_by', 'created_at', 'updated_at']

    # Exclude created_by from the form
    exclude = ['created_by']

    fieldsets = (
        ('Content Information', {
            'fields': ('training', 'title', 'description', 'content_type', 'order')
        }),
        ('Content Data', {
            'fields': ('file', 'url', 'text_content')
        }),
        ('Status & Meta', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by to the current user when creating
        """
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Only register Content model here
admin.site.register(Content, ContentAdmin)
