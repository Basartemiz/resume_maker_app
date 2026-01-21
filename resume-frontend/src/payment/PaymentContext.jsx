import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { getPaymentConfig } from './paymentApi';

const PaymentContext = createContext(null);

export function PaymentProvider({ children }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [onPaymentSuccess, setOnPaymentSuccess] = useState(null);
  const [stripePromise, setStripePromise] = useState(null);

  useEffect(() => {
    async function loadStripeConfig() {
      try {
        const config = await getPaymentConfig();
        if (config?.publishable_key) {
          setStripePromise(loadStripe(config.publishable_key));
        }
      } catch (err) {
        console.error('Failed to load Stripe config:', err);
      }
    }
    loadStripeConfig();
  }, []);

  const openPaymentModal = useCallback((successCallback) => {
    setOnPaymentSuccess(() => successCallback);
    setIsModalOpen(true);
  }, []);

  const closePaymentModal = useCallback(() => {
    setIsModalOpen(false);
    setOnPaymentSuccess(null);
  }, []);

  const handlePaymentComplete = useCallback((paymentId) => {
    if (onPaymentSuccess) {
      onPaymentSuccess(paymentId);
    }
    closePaymentModal();
  }, [onPaymentSuccess, closePaymentModal]);

  return (
    <PaymentContext.Provider value={{
      isModalOpen,
      openPaymentModal,
      closePaymentModal,
      handlePaymentComplete,
      stripePromise
    }}>
      {children}
    </PaymentContext.Provider>
  );
}

export function usePayment() {
  const context = useContext(PaymentContext);
  if (!context) {
    throw new Error('usePayment must be used within PaymentProvider');
  }
  return context;
}
