"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from rest_framework import serializers

from .models import Feedback


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feedback submissions"""

    class Meta:
        model = Feedback
        fields = (
            'title',
            'message',
            'feedback_type',
            'priority',
            'user_email',
            'user_name',
            'page_url',
            'project',
        )
        extra_kwargs = {
            'message': {'required': True},
            'title': {'required': False, 'allow_blank': True},
            'user_email': {'required': False, 'allow_blank': True},
            'user_name': {'required': False, 'allow_blank': True},
            'page_url': {'required': False, 'allow_blank': True},
            'project': {'required': False},
        }

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Feedback message is required.')
        if len(value) > 5000:
            raise serializers.ValidationError('Feedback message cannot exceed 5000 characters.')
        return value.strip()

    def validate(self, attrs):
        # If user is not authenticated, require email or name
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            if not attrs.get('user_email') and not attrs.get('user_name'):
                raise serializers.ValidationError(
                    {'user_email': 'Email or name is required for anonymous feedback submissions.'}
                )
        return attrs


class FeedbackListSerializer(serializers.ModelSerializer):
    """Serializer for listing feedback (limited fields)"""

    user = serializers.SerializerMethodField()
    feedback_type_display = serializers.CharField(source='get_feedback_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = (
            'id',
            'title',
            'message_preview',
            'feedback_type',
            'feedback_type_display',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'user',
            'project',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'username': obj.user.username,
            }
        return None

    def get_message_preview(self, obj):
        """Return truncated message for list view"""
        if len(obj.message) > 200:
            return obj.message[:200] + '...'
        return obj.message


class FeedbackDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed feedback view"""

    user = serializers.SerializerMethodField()
    responded_by_user = serializers.SerializerMethodField()
    feedback_type_display = serializers.CharField(source='get_feedback_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Feedback
        fields = (
            'id',
            'title',
            'message',
            'feedback_type',
            'feedback_type_display',
            'priority',
            'priority_display',
            'status',
            'status_display',
            'user',
            'organization',
            'project',
            'user_email',
            'user_name',
            'page_url',
            'browser_info',
            'user_agent',
            'admin_response',
            'responded_by_user',
            'responded_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'user',
            'organization',
            'created_at',
            'updated_at',
            'user_email',
            'user_name',
            'page_url',
            'browser_info',
            'user_agent',
        )

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'username': obj.user.username,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
            }
        return None

    def get_responded_by_user(self, obj):
        if obj.responded_by:
            return {
                'id': obj.responded_by.id,
                'email': obj.responded_by.email,
                'username': obj.responded_by.username,
            }
        return None


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating feedback (staff only)"""

    class Meta:
        model = Feedback
        fields = ('status', 'admin_response', 'priority')
        extra_kwargs = {
            'status': {'required': False},
            'admin_response': {'required': False, 'allow_blank': True},
            'priority': {'required': False},
        }

    def validate(self, attrs):
        status = attrs.get('status')
        admin_response = attrs.get('admin_response')

        # If status is being changed to resolved, recommend admin_response
        if status == 'resolved' and not admin_response:
            current_status = self.instance.status if self.instance else None
            if current_status != 'resolved':
                # Don't require it, but it's recommended
                pass

        return attrs

    def update(self, instance, validated_data):
        status = validated_data.get('status')
        admin_response = validated_data.get('admin_response')

        # If status changed or admin_response added, update responded fields
        if status and status != instance.status:
            instance.status = status
        if admin_response:
            instance.admin_response = admin_response
            instance.responded_by = self.context['request'].user
            from django.utils import timezone

            instance.responded_at = timezone.now()

        if 'priority' in validated_data:
            instance.priority = validated_data['priority']

        instance.save()
        return instance
