"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'feedback_type',
        'status',
        'priority',
        'user',
        'user_email',
        'created_at',
        'responded_at',
    )
    list_filter = (
        'status',
        'feedback_type',
        'priority',
        'created_at',
        'responded_at',
    )
    search_fields = (
        'title',
        'message',
        'user_email',
        'user_name',
        'user__email',
        'user__username',
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'user',
        'organization',
        'project',
        'user_email',
        'user_name',
        'page_url',
        'browser_info',
        'user_agent',
    )
    fieldsets = (
        (
            'Basic Information',
            {
                'fields': (
                    'id',
                    'title',
                    'message',
                    'feedback_type',
                    'priority',
                    'status',
                )
            },
        ),
        (
            'User Information',
            {
                'fields': (
                    'user',
                    'user_email',
                    'user_name',
                    'organization',
                    'project',
                )
            },
        ),
        (
            'Metadata',
            {
                'fields': (
                    'page_url',
                    'browser_info',
                    'user_agent',
                )
            },
        ),
        (
            'Admin Response',
            {
                'fields': (
                    'admin_response',
                    'responded_by',
                    'responded_at',
                )
            },
        ),
        (
            'Timestamps',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'organization', 'project', 'responded_by')

    def save_model(self, request, obj, form, change):
        """Set responded_by when admin_response is added"""
        if obj.admin_response and not obj.responded_by:
            obj.responded_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['mark_acknowledged', 'mark_in_progress', 'mark_resolved', 'mark_closed']

    def mark_acknowledged(self, request, queryset):
        """Mark selected feedback as acknowledged"""
        queryset.update(status='acknowledged')

    mark_acknowledged.short_description = 'Mark selected feedback as acknowledged'

    def mark_in_progress(self, request, queryset):
        """Mark selected feedback as in progress"""
        queryset.update(status='in_progress')

    mark_in_progress.short_description = 'Mark selected feedback as in progress'

    def mark_resolved(self, request, queryset):
        """Mark selected feedback as resolved"""
        queryset.update(status='resolved')

    mark_resolved.short_description = 'Mark selected feedback as resolved'

    def mark_closed(self, request, queryset):
        """Mark selected feedback as closed"""
        queryset.update(status='closed')

    mark_closed.short_description = 'Mark selected feedback as closed'
