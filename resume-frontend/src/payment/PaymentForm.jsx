import React, { useState } from 'react';
import {
  PaymentElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';

export default function PaymentForm({ paymentId, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: window.location.href,
      },
      redirect: 'if_required',
    });

    if (error) {
      setErrorMessage(error.message);
      setIsProcessing(false);
      if (onError) onError(error.message);
    } else if (paymentIntent && paymentIntent.status === 'succeeded') {
      setIsProcessing(false);
      if (onSuccess) onSuccess(paymentId);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <PaymentElement />
      {errorMessage && (
        <div className="payment-error">
          {errorMessage}
        </div>
      )}
      <button
        type="submit"
        disabled={!stripe || isProcessing}
        className="payment-submit-btn"
      >
        {isProcessing ? 'Processing...' : 'Pay $1.00'}
      </button>
    </form>
  );
}
