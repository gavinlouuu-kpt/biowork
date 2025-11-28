# Billing: django-allauth + dj-stripe + Stripe Checkout

This project uses:
- django-allauth: account flows (email login, signup, password)
- dj-stripe: Stripe objects sync + webhook ingestion
- Stripe Checkout: subscription purchase flow

## Environment Variables

Backend (see docker-compose):
- STRIPE_PUBLISHABLE_KEY=pk_test_xxx
- STRIPE_SECRET_KEY=sk_test_xxx
- STRIPE_WEBHOOK_SECRET=whsec_xxx
- STRIPE_PRICE_ID_MONTHLY=price_xxx

## URLs

- Accounts (allauth): /accounts/
- dj-stripe webhook + admin: /stripe/
- Create Checkout Session: POST /api/billing/checkout/session/

## Flow

1) User clicks "Upgrade" in the UI.
2) Frontend calls POST /api/billing/checkout/session/.
3) Server ensures a Stripe Customer linked to the user, creates Checkout Session for STRIPE_PRICE_ID_MONTHLY and returns a URL.
4) User completes the payment on Stripe.
5) Stripe sends webhooks → dj-stripe ingests.
6) Signal handler updates user.is_premium based on Subscription status (active|trialing → true; others → false).

## Local Testing

1) Create test Product + Price in Stripe Dashboard; copy the price id to STRIPE_PRICE_ID_MONTHLY.
2) Run server.
3) Forward webhooks using Stripe CLI:

```bash
stripe login
stripe listen --forward-to localhost:8080/stripe/webhook/ --events checkout.session.completed,customer.subscription.updated,customer.subscription.deleted
```

4) From the app UI, click Upgrade; complete test payment with 4242 4242 4242 4242.
5) Verify in Django shell:

```bash
poetry run python label_studio/manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.first().is_premium)"
```

## Notes

- Customer.subscriber is mapped to users.User via DJSTRIPE_SUBSCRIBER_MODEL.
- We set DJSTRIPE_FOREIGN_KEY_TO_FIELD=id for new installs.
- Success/cancel URL uses FRONTEND_HOSTNAME or HOSTNAME; adjust as needed.


