import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import { AdminPermission } from '../../types';
import LoadingSpinner from '../LoadingSpinner';

interface AdminRouteProps {
  children: React.ReactNode;
  requiredPermission?: AdminPermission;
}

/**
 * Admin Route Guard Component
 *
 * Protects admin routes and checks permissions.
 * Redirects unauthorized users to login or home page.
 */
const AdminRoute: React.FC<AdminRouteProps> = ({ children, requiredPermission }) => {
  const { user, isLoading } = useAuthContext();
  const { hasPermission, canAccessAdminPanel } = usePermissions();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Not authorized to access admin panel
  if (!canAccessAdminPanel()) {
    return <Navigate to="/" replace />;
  }

  // Check specific permission if required
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">
            You do not have permission to access this page.
          </p>
          <a
            href="/admin"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Back to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default AdminRoute;
