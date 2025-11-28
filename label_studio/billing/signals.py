from django.db.models.signals import post_save
from django.dispatch import receiver
from djstripe.models import Subscription


@receiver(post_save, sender=Subscription)
def update_user_premium_from_subscription(sender, instance: Subscription, **kwargs):
    """
    Toggle user.is_premium based on Stripe Subscription status.
    """
    customer = instance.customer
    if not customer:
        return
    user = getattr(customer, "subscriber", None)
    if not user:
        return

    # Active states: trialing or active
    active = instance.status in {"active", "trialing"}
    if user.is_premium != active:
        user.is_premium = active
        user.save(update_fields=["is_premium"])


