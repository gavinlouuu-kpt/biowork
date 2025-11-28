import React from "react";
import { Button } from "../../components";

export const BillingPage = () => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const startCheckout = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/billing/checkout/session/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      if (data?.url) {
        location.href = data.url;
        return;
      }
      setError("Unable to create checkout session");
    } catch (e) {
      setError("Unable to create checkout session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6">
      <div className="flex flex-col gap-4 max-w-[640px]">
        <h1 className="text-2xl font-semibold">Billing</h1>
        <p className="text-neutral-content-subtle">
          Manage your subscription. If you don’t have an active subscription, you can upgrade below.
        </p>
        <div className="flex gap-2 items-center">
          <Button look="primary" disabled={loading} onClick={startCheckout}>
            {loading ? "Redirecting..." : "Upgrade"}
          </Button>
          {error && <span className="text-danger">{error}</span>}
        </div>
      </div>
    </main>
  );
};

BillingPage.title = "Billing";
BillingPage.path = "/billing";
BillingPage.exact = true;


