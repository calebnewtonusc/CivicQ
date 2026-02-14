import React, { useEffect, useState } from 'react';
import {
  CheckIcon,
  XMarkIcon,
  ArrowsRightLeftIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import DataTable from '../../components/admin/DataTable';
import BulkActionBar from '../../components/admin/BulkActionBar';
import Modal from '../../components/admin/Modal';
import { questionModerationAPI } from '../../services/adminApi';
import { Question } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const QuestionModeration: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedQuestions, setSelectedQuestions] = useState<Set<string | number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal states
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [mergeModalOpen, setMergeModalOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [mergeTargetId, setMergeTargetId] = useState<number | null>(null);
  const [duplicates, setDuplicates] = useState<Question[]>([]);

  useEffect(() => {
    loadQuestions();
  }, [statusFilter]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const response = await questionModerationAPI.getPendingQuestions({
        page: 1,
        page_size: 100,
      });
      setQuestions(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (questionId: number) => {
    try {
      await questionModerationAPI.approveQuestion(questionId);
      setQuestions(questions.filter(q => q.id !== questionId));
    } catch (err: any) {
      alert(`Failed to approve question: ${err.message}`);
    }
  };

  const handleBulkApprove = async () => {
    if (selectedQuestions.size === 0) return;

    if (!window.confirm(`Approve ${selectedQuestions.size} questions?`)) return;

    try {
      const ids = Array.from(selectedQuestions) as number[];
      const result = await questionModerationAPI.bulkApprove(ids);

      if (result.success_count > 0) {
        setQuestions(questions.filter(q => !selectedQuestions.has(q.id)));
        setSelectedQuestions(new Set());
        alert(`Successfully approved ${result.success_count} questions`);
      }

      if (result.failure_count > 0) {
        alert(`Failed to approve ${result.failure_count} questions`);
      }
    } catch (err: any) {
      alert(`Bulk approve failed: ${err.message}`);
    }
  };

  const handleRejectQuestion = async () => {
    if (!selectedQuestion || !rejectReason) return;

    try {
      await questionModerationAPI.rejectQuestion(selectedQuestion.id, rejectReason);
      setQuestions(questions.filter(q => q.id !== selectedQuestion.id));
      setRejectModalOpen(false);
      setSelectedQuestion(null);
      setRejectReason('');
    } catch (err: any) {
      alert(`Failed to reject question: ${err.message}`);
    }
  };

  const handleBulkReject = async () => {
    if (selectedQuestions.size === 0) return;

    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      const ids = Array.from(selectedQuestions) as number[];
      const result = await questionModerationAPI.bulkReject(ids, reason);

      if (result.success_count > 0) {
        setQuestions(questions.filter(q => !selectedQuestions.has(q.id)));
        setSelectedQuestions(new Set());
        alert(`Successfully rejected ${result.success_count} questions`);
      }

      if (result.failure_count > 0) {
        alert(`Failed to reject ${result.failure_count} questions`);
      }
    } catch (err: any) {
      alert(`Bulk reject failed: ${err.message}`);
    }
  };

  const handleFindDuplicates = async (questionId: number) => {
    try {
      const dups = await questionModerationAPI.findDuplicates(questionId);
      setDuplicates(dups);
      setSelectedQuestion(questions.find(q => q.id === questionId) || null);
      setMergeModalOpen(true);
    } catch (err: any) {
      alert(`Failed to find duplicates: ${err.message}`);
    }
  };

  const handleMerge = async () => {
    if (!selectedQuestion || !mergeTargetId) return;

    try {
      await questionModerationAPI.mergeQuestions([selectedQuestion.id], mergeTargetId);
      setQuestions(questions.filter(q => q.id !== selectedQuestion.id));
      setMergeModalOpen(false);
      setSelectedQuestion(null);
      setMergeTargetId(null);
      setDuplicates([]);
    } catch (err: any) {
      alert(`Failed to merge questions: ${err.message}`);
    }
  };

  const filteredQuestions = questions.filter(q =>
    q.question_text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const columns = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-20',
      sortable: true,
    },
    {
      key: 'question_text',
      header: 'Question',
      render: (q: Question) => (
        <div className="max-w-2xl">
          <p className="text-sm font-medium text-gray-900 line-clamp-2">{q.question_text}</p>
          {q.issue_tags && q.issue_tags.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {q.issue_tags.slice(0, 3).map((tag, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'upvotes',
      header: 'Votes',
      sortable: true,
      render: (q: Question) => (
        <span className="text-sm text-gray-600">
          {q.upvotes - q.downvotes}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Submitted',
      sortable: true,
      render: (q: Question) => (
        <span className="text-sm text-gray-500">
          {new Date(q.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (q: Question) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleApprove(q.id)}
            className="text-green-600 hover:text-green-700"
            title="Approve"
          >
            <CheckIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => {
              setSelectedQuestion(q);
              setRejectModalOpen(true);
            }}
            className="text-red-600 hover:text-red-700"
            title="Reject"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleFindDuplicates(q.id)}
            className="text-indigo-600 hover:text-indigo-700"
            title="Find duplicates"
          >
            <ArrowsRightLeftIcon className="h-5 w-5" />
          </button>
        </div>
      ),
    },
  ];

  const bulkActions = [
    {
      label: 'Approve Selected',
      onClick: handleBulkApprove,
      variant: 'success' as const,
      icon: CheckIcon,
    },
    {
      label: 'Reject Selected',
      onClick: handleBulkReject,
      variant: 'danger' as const,
      icon: XMarkIcon,
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
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Question Moderation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Review and approve voter questions
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
                placeholder="Search questions..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="all">All</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-500">Pending Review</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">
            {filteredQuestions.length}
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-500">Selected</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">
            {selectedQuestions.size}
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <p className="text-sm font-medium text-gray-500">Avg. Time</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">2.5 min</p>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filteredQuestions}
        keyExtractor={(q) => q.id}
        selectable
        selectedItems={selectedQuestions}
        onSelectionChange={setSelectedQuestions}
        emptyMessage="No questions to review"
      />

      {/* Bulk Actions Bar */}
      <BulkActionBar
        selectedCount={selectedQuestions.size}
        actions={bulkActions}
        onClear={() => setSelectedQuestions(new Set())}
      />

      {/* Reject Modal */}
      <Modal
        isOpen={rejectModalOpen}
        onClose={() => {
          setRejectModalOpen(false);
          setSelectedQuestion(null);
          setRejectReason('');
        }}
        title="Reject Question"
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setRejectModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleRejectQuestion}
              disabled={!rejectReason}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Reject Question
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-gray-900 mb-2">Question:</p>
            <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
              {selectedQuestion?.question_text}
            </p>
          </div>
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
              Rejection Reason *
            </label>
            <select
              id="reason"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="">Select a reason...</option>
              <option value="off_topic">Off topic</option>
              <option value="inappropriate">Inappropriate content</option>
              <option value="duplicate">Duplicate question</option>
              <option value="unclear">Unclear or poorly written</option>
              <option value="spam">Spam</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
      </Modal>

      {/* Merge Modal */}
      <Modal
        isOpen={mergeModalOpen}
        onClose={() => {
          setMergeModalOpen(false);
          setSelectedQuestion(null);
          setMergeTargetId(null);
          setDuplicates([]);
        }}
        title="Merge Duplicate Questions"
        size="lg"
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setMergeModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleMerge}
              disabled={!mergeTargetId}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Merge into Selected
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-gray-900 mb-2">Source Question:</p>
            <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
              {selectedQuestion?.question_text}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 mb-2">
              Potential Duplicates ({duplicates.length}):
            </p>
            <div className="space-y-2">
              {duplicates.length === 0 ? (
                <p className="text-sm text-gray-500">No duplicates found</p>
              ) : (
                duplicates.map((dup) => (
                  <label
                    key={dup.id}
                    className="flex items-start p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="radio"
                      name="merge_target"
                      value={dup.id}
                      checked={mergeTargetId === dup.id}
                      onChange={() => setMergeTargetId(dup.id)}
                      className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                    />
                    <div className="ml-3 flex-1">
                      <p className="text-sm text-gray-900">{dup.question_text}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {dup.upvotes - dup.downvotes} votes • {new Date(dup.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </label>
                ))
              )}
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default QuestionModeration;
