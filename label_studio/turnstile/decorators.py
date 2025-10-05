"""Cloudflare Turnstile enforcement decorator for POST form/API endpoints."""

from __future__ import annotations

from functools import wraps
from typing import Optional

from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin  # not used here, kept for future extension

from .utils import is_enabled, verify_turnstile


HEADER_OVERRIDE = "HTTP_X_CF_TURNSTILE_RESPONSE"


def _client_ip(request) -> Optional[str]:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def require_turnstile(view_func):
    """
    Decorator that enforces Cloudflare Turnstile verification for POST requests
    when TURNSTILE_ENABLED is true. No-ops for non-POST requests.

    Usage:
        @require_turnstile
        def user_login(request):
            ...

    Behavior:
        - If TURNSTILE_ENABLED is False: passes through.
        - On POST:
          * Reads token from form field 'cf-turnstile-response' (Turnstile default) or 'cf_turnstile_response'
            or header 'X-CF-Turnstile-Response'
          * Verifies token using Cloudflare siteverify
          * On failure: returns 400/403, preventing further processing
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_enabled() or request.method != "POST":
            return view_func(request, *args, **kwargs)

        token = (
            request.POST.get("cf-turnstile-response")  # default hidden field name inserted by Turnstile
            or request.POST.get("cf_turnstile_response")  # alternate name if manually wired
            or request.META.get(HEADER_OVERRIDE)  # header override
        )

        if not token:
            return HttpResponseBadRequest("Turnstile token missing")

        ok, info = verify_turnstile(token, _client_ip(request))
        if not ok:
            return HttpResponseForbidden("Turnstile verification failed")

        return view_func(request, *args, **kwargs)

    return _wrapped
