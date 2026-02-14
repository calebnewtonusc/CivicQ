import React, { useEffect, useState } from 'react';
import { ArrowDownTrayIcon, FunnelIcon } from '@heroicons/react/24/outline';
import DataTable from '../../components/admin/DataTable';
import { auditLogAPI } from '../../services/adminApi';
import { AuditLog as AuditLogType } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const AuditLog: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    loadLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eventTypeFilter, severityFilter]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const response = await auditLogAPI.getLogs({
        event_type: eventTypeFilter !== 'all' ? eventTypeFilter : undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        page: 1,
        page_size: 100,
      });
      setLogs(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await auditLogAPI.exportLogs({ format: 'csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-log-${new Date().toISOString()}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(`Failed to export: ${err.message}`);
    }
  };

  const getSeverityBadge = (severity: string) => {
    const styles = {
      info: 'bg-blue-100 text-blue-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${styles[severity as keyof typeof styles] || 'bg-gray-100 text-gray-800'}`}>
        {severity}
      </span>
    );
  };

  const columns = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-20',
      sortable: true,
    },
    {
      key: 'event_type',
      header: 'Event Type',
      sortable: true,
      render: (log: AuditLogType) => (
        <span className="text-sm text-gray-900">
          {log.event_type.replace(/_/g, ' ')}
        </span>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (log: AuditLogType) => getSeverityBadge(log.severity),
    },
    {
      key: 'target',
      header: 'Target',
      render: (log: AuditLogType) => (
        <span className="text-sm text-gray-600">
          {log.target_type ? `${log.target_type} #${log.target_id}` : 'N/A'}
        </span>
      ),
    },
    {
      key: 'actor_id',
      header: 'Actor',
      render: (log: AuditLogType) => (
        <span className="text-sm text-gray-600">
          User #{log.actor_id || 'System'}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Timestamp',
      sortable: true,
      render: (log: AuditLogType) => (
        <span className="text-sm text-gray-500">
          {new Date(log.created_at).toLocaleString()}
        </span>
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track all admin actions and system events
          </p>
        </div>
        <button
          onClick={handleExport}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-4">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">Filters</span>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Event Type
            </label>
            <select
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Events</option>
              <option value="moderation_action">Moderation Actions</option>
              <option value="user_created">User Created</option>
              <option value="question_submitted">Question Submitted</option>
              <option value="answer_published">Answer Published</option>
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <DataTable
        columns={columns}
        data={logs}
        keyExtractor={(log) => log.id}
        emptyMessage="No audit logs found"
      />
    </div>
  );
};

export default AuditLog;
