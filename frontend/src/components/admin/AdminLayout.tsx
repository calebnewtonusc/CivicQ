import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import {
  HomeIcon,
  QuestionMarkCircleIcon,
  UserGroupIcon,
  FlagIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { useAuthContext } from '../../contexts/AuthContext';
import { AdminPermission } from '../../types';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  permission?: AdminPermission;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/admin', icon: HomeIcon, permission: AdminPermission.VIEW_DASHBOARD },
  { name: 'Question Moderation', href: '/admin/questions', icon: QuestionMarkCircleIcon, permission: AdminPermission.MODERATE_QUESTIONS },
  { name: 'User Management', href: '/admin/users', icon: UserGroupIcon, permission: AdminPermission.MANAGE_USERS },
  { name: 'Content Moderation', href: '/admin/content', icon: FlagIcon, permission: AdminPermission.MODERATE_CONTENT },
  { name: 'Analytics', href: '/admin/analytics', icon: ChartBarIcon, permission: AdminPermission.VIEW_ANALYTICS },
  { name: 'City Configuration', href: '/admin/config', icon: Cog6ToothIcon, permission: AdminPermission.MANAGE_CITY_CONFIG },
  { name: 'Audit Log', href: '/admin/audit', icon: DocumentTextIcon, permission: AdminPermission.VIEW_AUDIT_LOG },
];

const AdminLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuthContext();

  const hasPermission = (permission?: AdminPermission): boolean => {
    if (!permission) return true;
    if (user?.is_superuser) return true;
    // In a real implementation, check user.permissions array
    return user?.role === 'admin' || user?.role === 'moderator' || user?.role === 'city_staff';
  };

  const filteredNavigation = navigation.filter(item => hasPermission(item.permission));

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? '' : 'pointer-events-none'}`}>
        <div
          className={`fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity ${
            sidebarOpen ? 'opacity-100' : 'opacity-0'
          }`}
          onClick={() => setSidebarOpen(false)}
        />
        <div
          className={`fixed inset-y-0 left-0 flex w-64 flex-col bg-white transform transition-transform ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-indigo-600">CivicQ Admin</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 min-h-0 bg-white border-r border-gray-200">
          <div className="flex items-center h-16 px-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-indigo-600">CivicQ Admin</h1>
          </div>
          <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          <div className="flex-shrink-0 px-4 py-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <p className="font-medium">{user?.full_name || user?.email}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
            <Link
              to="/"
              className="mt-2 block text-sm text-indigo-600 hover:text-indigo-700"
            >
              Back to Main Site
            </Link>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        <div className="sticky top-0 z-10 flex h-16 bg-white border-b border-gray-200 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          <div className="flex items-center px-4">
            <h1 className="text-lg font-semibold text-gray-900">Admin Panel</h1>
          </div>
        </div>

        <main className="flex-1">
          <div className="py-6 px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
