import React, { useEffect, useState } from 'react';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import DataTable from '../../components/admin/DataTable';
import Modal from '../../components/admin/Modal';
import { cityConfigAPI } from '../../services/adminApi';
import { ElectionConfig, CitySettings } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const CityConfiguration: React.FC = () => {
  const [elections, setElections] = useState<ElectionConfig[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [settings, setSettings] = useState<CitySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Election modal
  const [electionModalOpen, setElectionModalOpen] = useState(false);
  const [editingElection, setEditingElection] = useState<ElectionConfig | null>(null);
  const [electionForm, setElectionForm] = useState<Partial<ElectionConfig>>({
    city_id: '',
    election_date: '',
    election_name: '',
    is_active: true,
  });

  // Settings modal - reserved for future use
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [settingsForm, setSettingsForm] = useState<Partial<CitySettings>>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [electionsData] = await Promise.all([
        cityConfigAPI.getElections(),
      ]);
      setElections(electionsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveElection = async () => {
    try {
      if (editingElection) {
        await cityConfigAPI.updateElection(editingElection.id!, electionForm);
      } else {
        await cityConfigAPI.createElection(electionForm as Omit<ElectionConfig, 'id'>);
      }
      setElectionModalOpen(false);
      setEditingElection(null);
      setElectionForm({
        city_id: '',
        election_date: '',
        election_name: '',
        is_active: true,
      });
      loadData();
    } catch (err: any) {
      alert(`Failed to save election: ${err.message}`);
    }
  };

  const handleDeleteElection = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this election?')) return;

    try {
      await cityConfigAPI.deleteElection(id);
      loadData();
    } catch (err: any) {
      alert(`Failed to delete election: ${err.message}`);
    }
  };

  const columns = [
    {
      key: 'election_name',
      header: 'Election Name',
      sortable: true,
    },
    {
      key: 'city_id',
      header: 'City',
      sortable: true,
    },
    {
      key: 'election_date',
      header: 'Election Date',
      sortable: true,
      render: (e: ElectionConfig) => (
        <span className="text-sm text-gray-900">
          {new Date(e.election_date).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (e: ElectionConfig) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          e.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {e.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (e: ElectionConfig) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setEditingElection(e);
              setElectionForm(e);
              setElectionModalOpen(true);
            }}
            className="text-indigo-600 hover:text-indigo-700"
            title="Edit"
          >
            <PencilIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleDeleteElection(e.id!)}
            className="text-red-600 hover:text-red-700"
            title="Delete"
          >
            <TrashIcon className="h-5 w-5" />
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">City Configuration</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage elections, contests, and city settings
          </p>
        </div>
        <button
          onClick={() => {
            setEditingElection(null);
            setElectionForm({
              city_id: '',
              election_date: '',
              election_name: '',
              is_active: true,
            });
            setElectionModalOpen(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Election
        </button>
      </div>

      {/* Elections Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Elections</h2>
        </div>
        <div className="p-6">
          <DataTable
            columns={columns}
            data={elections}
            keyExtractor={(e) => e.id!}
            emptyMessage="No elections configured"
          />
        </div>
      </div>

      {/* Election Modal */}
      <Modal
        isOpen={electionModalOpen}
        onClose={() => {
          setElectionModalOpen(false);
          setEditingElection(null);
        }}
        title={editingElection ? 'Edit Election' : 'Create Election'}
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setElectionModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveElection}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Save Election
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Election Name *
            </label>
            <input
              type="text"
              value={electionForm.election_name || ''}
              onChange={(e) => setElectionForm({ ...electionForm, election_name: e.target.value })}
              className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., 2024 General Election"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              City ID *
            </label>
            <input
              type="text"
              value={electionForm.city_id || ''}
              onChange={(e) => setElectionForm({ ...electionForm, city_id: e.target.value })}
              className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., seattle-wa"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Election Date *
            </label>
            <input
              type="date"
              value={electionForm.election_date || ''}
              onChange={(e) => setElectionForm({ ...electionForm, election_date: e.target.value })}
              className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={electionForm.is_active || false}
              onChange={(e) => setElectionForm({ ...electionForm, is_active: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Active Election
            </label>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CityConfiguration;
