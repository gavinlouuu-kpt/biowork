from django.urls import re_path
from .views import CreateCheckoutSessionView

urlpatterns = [
    re_path(r"^api/billing/checkout/session/$", CreateCheckoutSessionView.as_view(), name="billing-checkout-session"),
]


