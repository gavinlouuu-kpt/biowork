from core.utils.common import temporary_disconnect_all_signals
from django.conf import settings
from django.db import transaction
from organizations.models import Organization, OrganizationMember
from projects.models import Project


def create_organization(title, created_by, legacy_api_tokens_enabled=True, **kwargs):
    from core.feature_flags import flag_set

    JWT_ACCESS_TOKEN_ENABLED = flag_set('fflag__feature_develop__prompts__dia_1829_jwt_token_auth')

    with transaction.atomic():
        org = Organization.objects.create(title=title, created_by=created_by, **kwargs)
        OrganizationMember.objects.create(user=created_by, organization=org)
        if JWT_ACCESS_TOKEN_ENABLED:
            # set auth tokens to new system for new users, unless specified otherwise
            org.jwt.api_tokens_enabled = True
            # Enable legacy tokens by default for ML backend compatibility
            # Can be overridden via explicit parameter or environment variable
            org.jwt.legacy_api_tokens_enabled = (
                legacy_api_tokens_enabled if kwargs.get('force_legacy_setting') else
                (legacy_api_tokens_enabled or settings.LABEL_STUDIO_ENABLE_LEGACY_API_TOKEN)
            )
            org.jwt.save()
        return org


def destroy_organization(org):
    with temporary_disconnect_all_signals():
        Project.objects.filter(organization=org).delete()
        if hasattr(org, 'saml'):
            org.saml.delete()
        org.delete()
