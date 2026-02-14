import React, { useEffect, useState } from 'react';
import {
  ExclamationTriangleIcon,
  NoSymbolIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import DataTable from '../../components/admin/DataTable';
import BulkActionBar from '../../components/admin/BulkActionBar';
import Modal from '../../components/admin/Modal';
import { userManagementAPI } from '../../services/adminApi';
import { UserActivity, UserRole } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<UserActivity[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<Set<string | number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Modal state
  const [actionModalOpen, setActionModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserActivity | null>(null);
  const [actionType, setActionType] = useState<'warn' | 'suspend' | 'ban' | 'restore'>('warn');
  const [actionReason, setActionReason] = useState('');
  const [suspensionDays, setSuspensionDays] = useState(7);

  useEffect(() => {
    loadUsers();
  }, [roleFilter, statusFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await userManagementAPI.getUsers({
        role: roleFilter !== 'all' ? roleFilter : undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        page: 1,
        page_size: 100,
      });
      setUsers(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async () => {
    if (!selectedUser || !actionReason) return;

    try {
      switch (actionType) {
        case 'warn':
          await userManagementAPI.warnUser(selectedUser.user.id, actionReason);
          break;
        case 'suspend':
          await userManagementAPI.suspendUser(selectedUser.user.id, suspensionDays, actionReason);
          break;
        case 'ban':
          await userManagementAPI.banUser(selectedUser.user.id, actionReason);
          break;
        case 'restore':
          await userManagementAPI.restoreUser(selectedUser.user.id, actionReason);
          break;
      }
      setActionModalOpen(false);
      setSelectedUser(null);
      setActionReason('');
      loadUsers();
    } catch (err: any) {
      alert(`Failed to ${actionType} user: ${err.message}`);
    }
  };

  const openActionModal = (user: UserActivity, action: typeof actionType) => {
    setSelectedUser(user);
    setActionType(action);
    setActionModalOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      warned: 'bg-yellow-100 text-yellow-800',
      suspended: 'bg-orange-100 text-orange-800',
      banned: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const filteredUsers = users.filter(u =>
    u.user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.user.full_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const columns = [
    {
      key: 'user',
      header: 'User',
      render: (u: UserActivity) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{u.user.full_name || 'N/A'}</p>
          <p className="text-sm text-gray-500">{u.user.email}</p>
        </div>
      ),
    },
    {
      key: 'role',
      header: 'Role',
      sortable: true,
      render: (u: UserActivity) => (
        <span className="text-sm text-gray-900 capitalize">{u.user.role}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (u: UserActivity) => getStatusBadge(u.account_status),
    },
    {
      key: 'activity',
      header: 'Activity',
      render: (u: UserActivity) => (
        <div className="text-sm text-gray-500">
          <p>{u.questions_submitted} questions</p>
          <p>{u.votes_cast} votes</p>
        </div>
      ),
    },
    {
      key: 'warnings',
      header: 'Warnings',
      sortable: true,
      render: (u: UserActivity) => (
        <span className="text-sm text-gray-900">{u.warnings}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (u: UserActivity) => (
        <div className="flex items-center space-x-2">
          {u.account_status !== 'banned' && u.account_status !== 'suspended' && (
            <>
              <button
                onClick={() => openActionModal(u, 'warn')}
                className="text-yellow-600 hover:text-yellow-700"
                title="Warn"
              >
                <ExclamationTriangleIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => openActionModal(u, 'suspend')}
                className="text-orange-600 hover:text-orange-700"
                title="Suspend"
              >
                <NoSymbolIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => openActionModal(u, 'ban')}
                className="text-red-600 hover:text-red-700"
                title="Ban"
              >
                <NoSymbolIcon className="h-5 w-5" />
              </button>
            </>
          )}
          {(u.account_status === 'banned' || u.account_status === 'suspended') && (
            <button
              onClick={() => openActionModal(u, 'restore')}
              className="text-green-600 hover:text-green-700"
              title="Restore"
            >
              <CheckCircleIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage user accounts and moderation actions
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search users..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          </div>
          <div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Roles</option>
              <option value={UserRole.VOTER}>Voters</option>
              <option value={UserRole.CANDIDATE}>Candidates</option>
              <option value={UserRole.MODERATOR}>Moderators</option>
            </select>
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="warned">Warned</option>
              <option value="suspended">Suspended</option>
              <option value="banned">Banned</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filteredUsers}
        keyExtractor={(u) => u.user.id}
        selectable
        selectedItems={selectedUsers}
        onSelectionChange={setSelectedUsers}
        emptyMessage="No users found"
      />

      {/* Action Modal */}
      <Modal
        isOpen={actionModalOpen}
        onClose={() => {
          setActionModalOpen(false);
          setSelectedUser(null);
          setActionReason('');
        }}
        title={`${actionType.charAt(0).toUpperCase() + actionType.slice(1)} User`}
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setActionModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUserAction}
              disabled={!actionReason}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Confirm {actionType}
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-gray-900 mb-2">User:</p>
            <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
              {selectedUser?.user.full_name || selectedUser?.user.email}
            </p>
          </div>

          {actionType === 'suspend' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Suspension Duration (days)
              </label>
              <input
                type="number"
                value={suspensionDays}
                onChange={(e) => setSuspensionDays(parseInt(e.target.value))}
                min="1"
                max="365"
                className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason *
            </label>
            <textarea
              value={actionReason}
              onChange={(e) => setActionReason(e.target.value)}
              rows={3}
              placeholder={`Enter reason for ${actionType}...`}
              className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </Modal>

      <BulkActionBar
        selectedCount={selectedUsers.size}
        actions={[]}
        onClear={() => setSelectedUsers(new Set())}
      />
    </div>
  );
};

export default UserManagement;
