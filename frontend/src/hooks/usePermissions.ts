import { useAuthContext } from '../contexts/AuthContext';
import { AdminPermission, UserRole } from '../types';

/**
 * RBAC Permissions Hook
 *
 * Defines role-based access control for admin features.
 * Returns permission checking functions.
 */

const ROLE_PERMISSIONS: Record<UserRole, AdminPermission[]> = {
  [UserRole.ADMIN]: [
    AdminPermission.VIEW_DASHBOARD,
    AdminPermission.MODERATE_QUESTIONS,
    AdminPermission.MODERATE_CONTENT,
    AdminPermission.MANAGE_USERS,
    AdminPermission.VIEW_ANALYTICS,
    AdminPermission.MANAGE_CITY_CONFIG,
    AdminPermission.VIEW_AUDIT_LOG,
    AdminPermission.MANAGE_ELECTIONS,
    AdminPermission.BULK_OPERATIONS,
  ],
  [UserRole.CITY_STAFF]: [
    AdminPermission.VIEW_DASHBOARD,
    AdminPermission.MODERATE_QUESTIONS,
    AdminPermission.MODERATE_CONTENT,
    AdminPermission.VIEW_ANALYTICS,
    AdminPermission.MANAGE_CITY_CONFIG,
    AdminPermission.VIEW_AUDIT_LOG,
    AdminPermission.MANAGE_ELECTIONS,
    AdminPermission.BULK_OPERATIONS,
  ],
  [UserRole.MODERATOR]: [
    AdminPermission.VIEW_DASHBOARD,
    AdminPermission.MODERATE_QUESTIONS,
    AdminPermission.MODERATE_CONTENT,
    AdminPermission.VIEW_ANALYTICS,
  ],
  [UserRole.VOTER]: [],
  [UserRole.CANDIDATE]: [],
};

export const usePermissions = () => {
  const { user } = useAuthContext();

  const hasPermission = (permission: AdminPermission): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;

    const userPermissions = ROLE_PERMISSIONS[user.role as UserRole] || [];
    return userPermissions.includes(permission);
  };

  const hasAnyPermission = (permissions: AdminPermission[]): boolean => {
    return permissions.some(permission => hasPermission(permission));
  };

  const hasAllPermissions = (permissions: AdminPermission[]): boolean => {
    return permissions.every(permission => hasPermission(permission));
  };

  const isAdmin = (): boolean => {
    if (!user) return false;
    return (
      user.is_superuser ||
      user.role === UserRole.ADMIN ||
      user.role === UserRole.CITY_STAFF ||
      user.role === UserRole.MODERATOR
    );
  };

  const canAccessAdminPanel = (): boolean => {
    return hasPermission(AdminPermission.VIEW_DASHBOARD);
  };

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
    canAccessAdminPanel,
  };
};

export default usePermissions;
