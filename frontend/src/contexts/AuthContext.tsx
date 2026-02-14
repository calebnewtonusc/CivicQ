import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { User } from '../types';

interface AuthContextType {
  user: User | null | undefined;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  try {
    const auth = useAuth();

    const value: AuthContextType = {
      user: auth.user,
      isLoading: auth.isLoading,
      isAuthenticated: auth.isAuthenticated,
      login: (email: string, password: string) => auth.login({ email, password }),
      logout: auth.logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  } catch (error) {
    // Fallback if auth initialization fails
    console.error('Auth initialization failed:', error);
    const fallbackValue: AuthContextType = {
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: () => {},
      logout: () => {},
    };
    return <AuthContext.Provider value={fallbackValue}>{children}</AuthContext.Provider>;
  }
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};
