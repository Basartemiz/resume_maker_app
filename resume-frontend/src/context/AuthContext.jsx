import React, { createContext, useContext, useState, useEffect } from 'react';
import { isAuthenticated, clearTokens, getAccessToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    if (isAuthenticated()) {
      setUser({ authenticated: true });
    }
    setLoading(false);
  }, []);

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  const loginSuccess = () => {
    setUser({ authenticated: true });
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout, loginSuccess, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
