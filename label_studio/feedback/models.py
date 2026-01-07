"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Feedback(models.Model):
    """User feedback submission model"""

    # User association (nullable for anonymous feedback)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions',
        help_text=_('User who submitted the feedback'),
    )

    # Organization context (optional, for organization-specific feedback)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions',
        help_text=_('Organization context for the feedback'),
    )

    # Project context (optional, for project-specific feedback)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions',
        help_text=_('Project context for the feedback'),
    )

    # Feedback content
    title = models.CharField(max_length=255, blank=True, help_text=_('Optional title for the feedback'))
    message = models.TextField(help_text=_('Feedback message'))

    # Feedback type/category
    FEEDBACK_TYPES = [
        ('bug', _('Bug Report')),
        ('feature', _('Feature Request')),
        ('improvement', _('Improvement Suggestion')),
        ('question', _('Question')),
        ('other', _('Other')),
    ]
    feedback_type = models.CharField(
        max_length=20, choices=FEEDBACK_TYPES, default='other', help_text=_('Type of feedback')
    )

    # Priority/Urgency (optional)
    PRIORITY_LEVELS = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS, default='medium', blank=True, help_text=_('Priority level')
    )

    # Status tracking
    STATUS_CHOICES = [
        ('new', _('New')),
        ('acknowledged', _('Acknowledged')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new', help_text=_('Current status of the feedback')
    )

    # Additional metadata
    user_email = models.EmailField(blank=True, help_text=_('Email if user not logged in'))
    user_name = models.CharField(max_length=255, blank=True, help_text=_('Name if user not logged in'))
    page_url = models.URLField(blank=True, help_text=_('URL where feedback was submitted from'))
    browser_info = models.CharField(max_length=255, blank=True, help_text=_('Browser information'))
    user_agent = models.TextField(blank=True, help_text=_('User agent string'))

    # Admin response
    admin_response = models.TextField(blank=True, help_text=_('Response from admin/team'))
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses',
        help_text=_('Admin user who responded'),
    )
    responded_at = models.DateTimeField(null=True, blank=True, help_text=_('When the response was made'))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['feedback_type', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
        ]

    def __str__(self):
        feedback_type_display = self.get_feedback_type_display()
        return f'Feedback #{self.id} - {feedback_type_display}'
