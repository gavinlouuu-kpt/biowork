"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from organizations.models import Organization, OrganizationMember

logger = logging.getLogger(__name__)


class DummyGetSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user and user.is_authenticated:
            if user.active_organization is None:
                # Create individual organization for user without one (legacy users)
                org = Organization.create_organization(created_by=user, title=f"{user.email}'s Organization")
                user.active_organization = org
                user.save(update_fields=['active_organization'])
            elif user.active_organization_id == 1:
                # Check if user should be migrated out of organization 1
                member = OrganizationMember.objects.filter(user=user, organization_id=1).first()
                org1 = Organization.objects.get(id=1)
                if member and not member.joined_via_invitation and org1.created_by != user:
                    # User is in org 1 but didn't create it and wasn't invited - give them their own org
                    org = Organization.create_organization(created_by=user, title=f"{user.email}'s Organization")
                    user.active_organization = org
                    user.save(update_fields=['active_organization'])
                    # Remove from organization 1
                    member.delete()
        
        if user and user.is_authenticated and user.active_organization:
            request.session['organization_pk'] = user.active_organization.id
        
        response = self.get_response(request)
        return response
