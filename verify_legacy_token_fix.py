#!/usr/bin/env python3
"""
Verification script for ML Backend Authentication Fix

This script verifies that new organizations are created with legacy tokens enabled by default.
Run this after deploying the fix to confirm it's working.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'label_studio'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.label_studio')
django.setup()

from organizations.functions import create_organization
from users.models import User
from jwt_auth.models import JWTSettings


def verify_new_org_defaults():
    """Verify that new organizations get legacy tokens enabled by default."""
    print("=" * 60)
    print("ML Backend Authentication Fix Verification")
    print("=" * 60)
    
    # Create test user
    print("\n1. Creating test user...")
    test_email = 'verify_test@example.com'
    
    # Clean up if exists
    User.objects.filter(email=test_email).delete()
    
    test_user = User.objects.create(
        email=test_email,
        username='verify_test'
    )
    print(f"   ✓ Created user: {test_user.email}")
    
    # Create organization
    print("\n2. Creating organization...")
    org = create_organization(
        title="Verification Test Organization",
        created_by=test_user
    )
    print(f"   ✓ Created organization: {org.title} (ID: {org.id})")
    
    # Check JWT settings
    print("\n3. Checking JWT settings...")
    jwt_settings = org.jwt
    
    print(f"   Organization ID: {org.id}")
    print(f"   api_tokens_enabled: {jwt_settings.api_tokens_enabled}")
    print(f"   legacy_api_tokens_enabled: {jwt_settings.legacy_api_tokens_enabled}")
    
    # Verify
    success = True
    if not jwt_settings.legacy_api_tokens_enabled:
        print("\n   ✗ FAILED: legacy_api_tokens_enabled is False!")
        success = False
    else:
        print("\n   ✓ PASSED: legacy_api_tokens_enabled is True!")
    
    # Cleanup
    print("\n4. Cleaning up test data...")
    org.delete()
    test_user.delete()
    print("   ✓ Test data cleaned up")
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✓ VERIFICATION PASSED")
        print("\nNew organizations will have legacy tokens enabled by default.")
        print("ML backends will work without manual configuration.")
    else:
        print("✗ VERIFICATION FAILED")
        print("\nThe fix was not applied correctly.")
        print("Check label_studio/organizations/functions.py")
    print("=" * 60)
    
    return success


def check_existing_orgs():
    """Check how many existing organizations have legacy tokens disabled."""
    print("\n" + "=" * 60)
    print("Existing Organizations Status")
    print("=" * 60)
    
    total = JWTSettings.objects.count()
    enabled = JWTSettings.objects.filter(legacy_api_tokens_enabled=True).count()
    disabled = total - enabled
    
    print(f"\nTotal organizations: {total}")
    print(f"  With legacy tokens enabled: {enabled}")
    print(f"  With legacy tokens disabled: {disabled}")
    
    if disabled > 0:
        print(f"\n⚠️  {disabled} organization(s) have legacy tokens disabled.")
        print("   ML backends will not work for these organizations.")
        print("\n   To fix all existing organizations, run:")
        print("   python3 manage.py shell")
        print("   >>> from jwt_auth.models import JWTSettings")
        print("   >>> JWTSettings.objects.update(legacy_api_tokens_enabled=True)")
    else:
        print("\n✓ All organizations have legacy tokens enabled!")
    
    print("=" * 60)


if __name__ == '__main__':
    try:
        # Verify new org defaults
        success = verify_new_org_defaults()
        
        # Check existing orgs
        check_existing_orgs()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

