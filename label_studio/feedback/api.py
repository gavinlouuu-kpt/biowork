"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import django_filters
from core.permissions import ViewClassPermission, all_permissions
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback
from .serializers import (
    FeedbackCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackListSerializer,
    FeedbackUpdateSerializer,
)


class FeedbackFilterSet(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Feedback.STATUS_CHOICES)
    feedback_type = django_filters.ChoiceFilter(choices=Feedback.FEEDBACK_TYPES)
    priority = django_filters.ChoiceFilter(choices=Feedback.PRIORITY_LEVELS)
    project = django_filters.NumberFilter(field_name='project_id')

    class Meta:
        model = Feedback
        fields = ['status', 'feedback_type', 'priority', 'project']


class IsOwnerOrStaffOrReadOnly:
    """Permission class that allows users to view their own feedback, staff to view all"""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # Allow anyone to submit feedback
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Allow viewing (filtered in queryset)
        # For updates/deletes, require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff can do anything
        if request.user.is_staff:
            return True
        # Users can view their own feedback
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return obj.user == request.user
        # Only staff can update/delete
        return False


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_sdk_group_name='feedback',
        x_fern_sdk_method_name='create',
        x_fern_audiences=['public'],
        operation_summary='Submit feedback',
        operation_description='Submit feedback about the application. Can be submitted anonymously or by authenticated users.',
        request_body=FeedbackCreateSerializer,
        responses={
            201: openapi.Response(
                description='Feedback created successfully',
                schema=FeedbackDetailSerializer,
            ),
            400: 'Bad request',
        },
    ),
)
@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_sdk_group_name='feedback',
        x_fern_sdk_method_name='list',
        x_fern_audiences=['public'],
        operation_summary='List feedback',
        operation_description='List feedback submissions. Users can see their own feedback, staff can see all feedback.',
        manual_parameters=[
            openapi.Parameter(
                name='status',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description='Filter by status',
                enum=[choice[0] for choice in Feedback.STATUS_CHOICES],
            ),
            openapi.Parameter(
                name='feedback_type',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description='Filter by feedback type',
                enum=[choice[0] for choice in Feedback.FEEDBACK_TYPES],
            ),
            openapi.Parameter(
                name='priority',
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
                description='Filter by priority',
                enum=[choice[0] for choice in Feedback.PRIORITY_LEVELS],
            ),
            openapi.Parameter(
                name='project',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
                description='Filter by project ID',
            ),
        ],
    ),
)
class FeedbackListCreateAPI(generics.ListCreateAPIView):
    """API endpoint for listing and creating feedback"""

    queryset = Feedback.objects.all()
    permission_classes = [AllowAny]  # Allow anonymous submissions
    filter_backends = [DjangoFilterBackend]
    filterset_class = FeedbackFilterSet

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FeedbackCreateSerializer
        return FeedbackListSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Feedback.objects.all()

        # If user is staff, show all feedback
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset

        # If user is authenticated but not staff, show only their feedback
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)

        # Anonymous users cannot list feedback
        return queryset.none()

    def perform_create(self, serializer):
        """Create feedback with user and metadata"""
        request = self.request

        # Set user if authenticated
        if request.user.is_authenticated:
            serializer.save(user=request.user)

            # Set organization if user has active organization
            if hasattr(request.user, 'active_organization') and request.user.active_organization:
                serializer.save(organization=request.user.active_organization)
        else:
            serializer.save()

        # Capture additional metadata
        feedback = serializer.instance
        if not feedback.page_url and request.META.get('HTTP_REFERER'):
            feedback.page_url = request.META.get('HTTP_REFERER')
        if not feedback.user_agent and request.META.get('HTTP_USER_AGENT'):
            feedback.user_agent = request.META.get('HTTP_USER_AGENT')
            # Extract browser info
            user_agent = feedback.user_agent
            if 'Chrome' in user_agent:
                feedback.browser_info = 'Chrome'
            elif 'Firefox' in user_agent:
                feedback.browser_info = 'Firefox'
            elif 'Safari' in user_agent:
                feedback.browser_info = 'Safari'
            elif 'Edge' in user_agent:
                feedback.browser_info = 'Edge'
            else:
                feedback.browser_info = 'Other'
        feedback.save()


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_sdk_group_name='feedback',
        x_fern_sdk_method_name='get',
        x_fern_audiences=['public'],
        operation_summary='Get feedback details',
        operation_description='Get detailed information about a specific feedback submission.',
    ),
)
@method_decorator(
    name='patch',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_sdk_group_name='feedback',
        x_fern_sdk_method_name='update',
        x_fern_audiences=['internal'],
        operation_summary='Update feedback',
        operation_description='Update feedback status and admin response. Staff only.',
        request_body=FeedbackUpdateSerializer,
    ),
)
@method_decorator(
    name='put',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_audiences=['internal'],
        operation_summary='Update feedback (full)',
        request_body=FeedbackUpdateSerializer,
    ),
)
class FeedbackDetailAPI(generics.RetrieveUpdateAPIView):
    """API endpoint for retrieving and updating feedback"""

    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return FeedbackUpdateSerializer
        return FeedbackDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Feedback.objects.all()

        # Staff can see all feedback
        if self.request.user.is_staff:
            return queryset

        # Regular users can only see their own feedback
        return queryset.filter(user=self.request.user)

    def get_object(self):
        """Get feedback object with permission check"""
        obj = super().get_object()

        # Staff can access any feedback
        if self.request.user.is_staff:
            return obj

        # Users can only access their own feedback
        if obj.user != self.request.user:
            raise PermissionDenied('You do not have permission to access this feedback.')

        return obj

    def update(self, request, *args, **kwargs):
        """Update feedback - staff only"""
        if not request.user.is_staff:
            raise PermissionDenied('Only staff members can update feedback.')

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full detail view
        detail_serializer = FeedbackDetailSerializer(instance)
        return Response(detail_serializer.data)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=['Feedback'],
        x_fern_sdk_group_name='feedback',
        x_fern_sdk_method_name='list_current_user',
        x_fern_audiences=['public'],
        operation_summary='Get current user feedback',
        operation_description='Get all feedback submissions for the current authenticated user.',
    ),
)
class CurrentUserFeedbackAPI(generics.ListAPIView):
    """API endpoint for listing current user's feedback"""

    serializer_class = FeedbackListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FeedbackFilterSet

    def get_queryset(self):
        """Return only current user's feedback"""
        return Feedback.objects.filter(user=self.request.user)
