'use client';

import { useState, useEffect, useCallback } from 'react';
import { checkAdminAuth, adminLogin, adminLogout, AdminAPIError } from '@/lib/adminApi';

interface AdminAuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: string | null;
  error: string | null;
}

export function useAdminAuth() {
  const [state, setState] = useState<AdminAuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null,
  });

  const checkAuth = useCallback(async () => {
    try {
      const result = await checkAdminAuth();
      setState({
        isAuthenticated: result.authenticated,
        isLoading: false,
        user: result.user || null,
        error: null,
      });
    } catch (error) {
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: error instanceof Error ? error.message : 'Authentication check failed',
      });
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const result = await adminLogin(username, password);
      if (result.success) {
        setState({
          isAuthenticated: true,
          isLoading: false,
          user: result.user || username,
          error: null,
        });
        return true;
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Login failed',
        }));
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof AdminAPIError 
        ? 'Invalid credentials' 
        : 'Login failed. Please try again.';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      return false;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await adminLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: null,
      });
    }
  }, []);

  return {
    ...state,
    login,
    logout,
    checkAuth,
  };
}
