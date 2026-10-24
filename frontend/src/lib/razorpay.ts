export interface RazorpayOrder {
  payment_id: number;
  booking_id: number;
  razorpay_order_id: string;
  amount: number;
  currency: string;
  key_id: string;
  expires_at: string;
}

export interface RazorpaySuccess {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
}

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;
  handler: (response: RazorpaySuccess) => void;
  modal?: {
    ondismiss?: () => void;
  };
  theme?: {
    color?: string;
  };
}

interface RazorpayInstance {
  open: () => void;
  on: (
    event: string,
    callback: (response: unknown) => void
  ) => void;
}

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

export function loadRazorpay(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.Razorpay) {
      resolve();
      return;
    }

    const existing = document.querySelector<HTMLScriptElement>(
      'script[src="https://checkout.razorpay.com/v1/checkout.js"]'
    );

    const script = existing ?? document.createElement("script");

    script.addEventListener(
      "load",
      () => resolve(),
      { once: true }
    );

    script.addEventListener(
      "error",
      () => reject(new Error("Unable to load Razorpay Checkout.")),
      { once: true }
    );

    if (!existing) {
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.async = true;
      document.body.appendChild(script);
    }
  });
}

export function openRazorpayCheckout(
  order: RazorpayOrder,
  onSuccess: (response: RazorpaySuccess) => void,
  onDismiss?: () => void
) {
  if (!window.Razorpay) {
    throw new Error("Razorpay Checkout is not loaded.");
  }

  let completed = false;
  let dismissed = false;

  const checkout = new window.Razorpay({
    key: order.key_id,
    amount: order.amount,
    currency: order.currency,
    name: "AeroSky",
    description: `Flight booking #${order.booking_id}`,
    order_id: order.razorpay_order_id,
    handler: (response: RazorpaySuccess) => {
      if (completed || dismissed) return;

      completed = true;
      onSuccess(response);
    },
    modal: {
      ondismiss: () => {
        if (completed || dismissed) return;

        dismissed = true;
        onDismiss?.();
      },
    },
    theme: {
      color: "#2563eb",
    },
  });

  checkout.open();
}
