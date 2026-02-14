import React, { useEffect, useState } from 'react';
import { FlagIcon, CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';
import DataTable from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { contentModerationAPI } from '../../services/adminApi';
import { Report } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const ContentModeration: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('pending');

  useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await contentModerationAPI.getReports({
        status: statusFilter !== 'all' ? statusFilter : undefined,
        page: 1,
        page_size: 100,
      });
      setReports(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (reportId: number, action: string) => {
    try {
      await contentModerationAPI.resolveReport(reportId, action);
      loadReports();
    } catch (err: any) {
      alert(`Failed to resolve report: ${err.message}`);
    }
  };

  const handleDismiss = async (reportId: number) => {
    try {
      await contentModerationAPI.dismissReport(reportId);
      loadReports();
    } catch (err: any) {
      alert(`Failed to dismiss report: ${err.message}`);
    }
  };

  const columns = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-20',
    },
    {
      key: 'target_type',
      header: 'Type',
      render: (r: Report) => (
        <span className="text-sm capitalize">{r.target_type}</span>
      ),
    },
    {
      key: 'reason',
      header: 'Reason',
      render: (r: Report) => (
        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
          {r.reason}
        </span>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (r: Report) => (
        <p className="text-sm text-gray-600 line-clamp-2">{r.description || 'No description'}</p>
      ),
    },
    {
      key: 'created_at',
      header: 'Reported',
      render: (r: Report) => (
        <span className="text-sm text-gray-500">
          {new Date(r.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r: Report) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setSelectedReport(r);
              setModalOpen(true);
            }}
            className="text-indigo-600 hover:text-indigo-700"
            title="View details"
          >
            <FlagIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleResolve(r.id, 'remove_content')}
            className="text-red-600 hover:text-red-700"
            title="Remove content"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleDismiss(r.id)}
            className="text-green-600 hover:text-green-700"
            title="Dismiss report"
          >
            <CheckCircleIcon className="h-5 w-5" />
          </button>
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
        <h1 className="text-2xl font-bold text-gray-900">Content Moderation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Review flagged content and user reports
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="block w-full sm:w-48 pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        >
          <option value="pending">Pending</option>
          <option value="under_review">Under Review</option>
          <option value="resolved">Resolved</option>
          <option value="all">All</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={reports}
        keyExtractor={(r) => r.id}
        emptyMessage="No reports found"
      />

      <Modal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedReport(null);
        }}
        title="Report Details"
      >
        {selectedReport && (
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-700">Type:</p>
              <p className="text-sm text-gray-900 capitalize">{selectedReport.target_type}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Reason:</p>
              <p className="text-sm text-gray-900">{selectedReport.reason}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Description:</p>
              <p className="text-sm text-gray-900">{selectedReport.description || 'None'}</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ContentModeration;
