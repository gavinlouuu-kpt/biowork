"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
# Generated manually for feedback module

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '__first__'),
        ('organizations', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Optional title for the feedback', max_length=255)),
                ('message', models.TextField(help_text='Feedback message')),
                (
                    'feedback_type',
                    models.CharField(
                        choices=[
                            ('bug', 'Bug Report'),
                            ('feature', 'Feature Request'),
                            ('improvement', 'Improvement Suggestion'),
                            ('question', 'Question'),
                            ('other', 'Other'),
                        ],
                        default='other',
                        help_text='Type of feedback',
                        max_length=20,
                    ),
                ),
                (
                    'priority',
                    models.CharField(
                        blank=True,
                        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
                        default='medium',
                        help_text='Priority level',
                        max_length=20,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('new', 'New'),
                            ('acknowledged', 'Acknowledged'),
                            ('in_progress', 'In Progress'),
                            ('resolved', 'Resolved'),
                            ('closed', 'Closed'),
                        ],
                        default='new',
                        help_text='Current status of the feedback',
                        max_length=20,
                    ),
                ),
                ('user_email', models.EmailField(blank=True, help_text='Email if user not logged in', max_length=254)),
                ('user_name', models.CharField(blank=True, help_text='Name if user not logged in', max_length=255)),
                ('page_url', models.URLField(blank=True, help_text='URL where feedback was submitted from')),
                ('browser_info', models.CharField(blank=True, help_text='Browser information', max_length=255)),
                ('user_agent', models.TextField(blank=True, help_text='User agent string')),
                ('admin_response', models.TextField(blank=True, help_text='Response from admin/team')),
                ('responded_at', models.DateTimeField(blank=True, help_text='When the response was made', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'organization',
                    models.ForeignKey(
                        blank=True,
                        help_text='Organization context for the feedback',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='feedback_submissions',
                        to='organizations.organization',
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        blank=True,
                        help_text='Project context for the feedback',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='feedback_submissions',
                        to='projects.project',
                    ),
                ),
                (
                    'responded_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='Admin user who responded',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='feedback_responses',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        blank=True,
                        help_text='User who submitted the feedback',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='feedback_submissions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedback',
                'db_table': 'feedback',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['user', '-created_at'], name='feedback_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['status', '-created_at'], name='feedback_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['feedback_type', '-created_at'], name='feedback_type_created_idx'),
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['organization', '-created_at'], name='feedback_org_created_idx'),
        ),
    ]
