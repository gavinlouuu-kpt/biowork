from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import stripe
from djstripe import models as djstripe_models


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        price_id = settings.STRIPE_PRICE_ID_MONTHLY
        if not price_id:
            return Response({"detail": "Stripe price id not configured"}, status=500)

        # Ensure Stripe API key
        if not settings.STRIPE_SECRET_KEY:
            return Response({"detail": "Stripe secret key not configured"}, status=500)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Ensure a Stripe Customer associated to our user (subscriber)
        customer, _ = djstripe_models.Customer.get_or_create(subscriber=user)

        # Compute return URLs
        base_url = settings.FRONTEND_HOSTNAME or settings.HOSTNAME or ""
        if not base_url:
            # Fallback to relative root if host is unset
            base_url = ""

        success_url = f"{base_url}/?billing=success"
        cancel_url = f"{base_url}/?billing=cancel"

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer.id,
            line_items=[{"price": price_id, "quantity": 1}],
            client_reference_id=str(user.id),
            success_url=success_url,
            cancel_url=cancel_url,
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
        )

        return Response({"url": session.get("url")})


