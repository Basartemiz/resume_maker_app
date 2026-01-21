import React, { useState, useEffect } from 'react';
import { Elements } from '@stripe/react-stripe-js';
import { usePayment } from './PaymentContext';
import PaymentForm from './PaymentForm';
import { createPaymentIntent } from './paymentApi';
import './payment.css';

export default function PaymentModal() {
  const { isModalOpen, closePaymentModal, handlePaymentComplete, stripePromise } = usePayment();
  const [clientSecret, setClientSecret] = useState(null);
  const [paymentId, setPaymentId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isModalOpen && !clientSecret) {
      setLoading(true);
      setError(null);
      createPaymentIntent()
        .then((data) => {
          setClientSecret(data.client_secret);
          setPaymentId(data.payment_id);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, [isModalOpen]);

  useEffect(() => {
    if (!isModalOpen) {
      setClientSecret(null);
      setPaymentId(null);
      setError(null);
    }
  }, [isModalOpen]);

  if (!isModalOpen) return null;

  const appearance = {
    theme: 'stripe',
    variables: {
      colorPrimary: '#0570de',
    },
  };

  const options = {
    clientSecret,
    appearance,
  };

  return (
    <div className="payment-modal-overlay" onClick={closePaymentModal}>
      <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
        <button className="payment-modal-close" onClick={closePaymentModal}>
          &times;
        </button>

        <div className="payment-modal-header">
          <h2>Download Resume PDF</h2>
          <p className="payment-price">$1.00</p>
        </div>

        <div className="payment-modal-body">
          {loading && (
            <div className="payment-loading">
              <p>Loading payment form...</p>
            </div>
          )}

          {error && (
            <div className="payment-error-box">
              <p>{error}</p>
              <button onClick={() => {
                setError(null);
                setLoading(true);
                createPaymentIntent()
                  .then((data) => {
                    setClientSecret(data.client_secret);
                    setPaymentId(data.payment_id);
                    setLoading(false);
                  })
                  .catch((err) => {
                    setError(err.message);
                    setLoading(false);
                  });
              }}>Try Again</button>
            </div>
          )}

          {!loading && !error && clientSecret && stripePromise && (
            <Elements stripe={stripePromise} options={options}>
              <PaymentForm
                paymentId={paymentId}
                onSuccess={handlePaymentComplete}
                onError={setError}
              />
            </Elements>
          )}
        </div>

        <div className="payment-modal-footer">
          <p>Secure payment powered by Stripe</p>
          <p className="payment-methods">
            Accepts credit cards, Apple Pay, and Google Pay
          </p>
        </div>
      </div>
    </div>
  );
}
