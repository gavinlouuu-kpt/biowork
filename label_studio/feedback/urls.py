"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from django.urls import include, path

from . import api

app_name = 'feedback'

_api_urlpatterns = [
    path('', api.FeedbackListCreateAPI.as_view(), name='feedback-list-create'),
    path('<int:pk>/', api.FeedbackDetailAPI.as_view(), name='feedback-detail'),
    path('current-user/', api.CurrentUserFeedbackAPI.as_view(), name='current-user-feedback'),
]

urlpatterns = [
    path('api/feedback/', include((_api_urlpatterns, app_name), namespace='api')),
]
