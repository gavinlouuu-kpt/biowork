"""Cloudflare Turnstile verification utilities."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import requests
from django.conf import settings

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
DEFAULT_TIMEOUT_SECS = 5


def _bool_env(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def is_enabled() -> bool:
    """Return whether Turnstile verification is enabled via settings or env."""
    enabled = getattr(settings, "TURNSTILE_ENABLED", None)
    if enabled is None:
        return _bool_env(os.getenv("TURNSTILE_ENABLED"), False)
    return bool(enabled)


def _get_secret() -> str:
    """Get the Turnstile secret key from settings or env."""
    secret = getattr(settings, "TURNSTILE_SECRET_KEY", "") or os.getenv("TURNSTILE_SECRET_KEY", "")
    return secret or ""


def verify_turnstile(token: str, ip: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify a Turnstile token with Cloudflare.

    Args:
        token: One-time token returned by the Turnstile widget (cf-turnstile-response).
        ip: Optional client IP to forward to Cloudflare for risk analysis.

    Returns:
        (success, info) where success is True when verification succeeds,
        and info includes Cloudflare response payload or local error description.
    """
    # Allow short-circuiting when feature is disabled
    if not is_enabled():
        return True, {"skipped": True}

    if not token:
        return False, {"error": "missing_token"}

    secret = _get_secret()
    if not secret:
        return False, {"error": "missing_secret"}

    data: Dict[str, Any] = {"secret": secret, "response": token}
    if ip:
        data["remoteip"] = ip

    try:
        resp = requests.post(VERIFY_URL, data=data, timeout=DEFAULT_TIMEOUT_SECS)
        info = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"status_code": resp.status_code, "text": resp.text}
        return bool(info.get("success")), info
    except Exception as exc:
        return False, {"error": "verification_exception", "detail": str(exc)}
