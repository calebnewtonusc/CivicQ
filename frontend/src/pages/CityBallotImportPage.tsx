import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface Candidate {
  name: string;
  email: string;
  phone: string;
  filing_id: string;
  website: string;
}

interface Contest {
  title: string;
  type: 'race' | 'measure';
  office: string;
  jurisdiction: string;
  seat_count: number;
  description: string;
  candidates: Candidate[];
  measure_number: string;
  measure_text: string;
  summary: string;
}

const CityBallotImportPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();
  const navigate = useNavigate();

  const [electionDate, setElectionDate] = useState('');
  const [contests, setContests] = useState<Contest[]>([]);
  const [currentContest, setCurrentContest] = useState<Contest>({
    title: '',
    type: 'race',
    office: '',
    jurisdiction: '',
    seat_count: 1,
    description: '',
    candidates: [],
    measure_number: '',
    measure_text: '',
    summary: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const getToken = () => localStorage.getItem('access_token');

  const addContest = () => {
    if (!currentContest.title) {
      alert('Please enter a contest title');
      return;
    }

    setContests([...contests, { ...currentContest }]);

    // Reset form
    setCurrentContest({
      title: '',
      type: 'race',
      office: '',
      jurisdiction: '',
      seat_count: 1,
      description: '',
      candidates: [],
      measure_number: '',
      measure_text: '',
      summary: '',
    });
  };

  const removeContest = (index: number) => {
    setContests(contests.filter((_, i) => i !== index));
  };

  const addCandidate = () => {
    setCurrentContest({
      ...currentContest,
      candidates: [
        ...currentContest.candidates,
        { name: '', email: '', phone: '', filing_id: '', website: '' }
      ]
    });
  };

  const updateCandidate = (index: number, field: keyof Candidate, value: string) => {
    const updatedCandidates = [...currentContest.candidates];
    updatedCandidates[index] = { ...updatedCandidates[index], [field]: value };
    setCurrentContest({ ...currentContest, candidates: updatedCandidates });
  };

  const removeCandidate = (index: number) => {
    setCurrentContest({
      ...currentContest,
      candidates: currentContest.candidates.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!electionDate) {
      setError('Please enter an election date');
      return;
    }

    if (contests.length === 0) {
      setError('Please add at least one contest');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.post(
        `${API_BASE_URL}/cities/${cityId}/import-ballot`,
        {
          election_date: electionDate,
          contests: contests,
          source_metadata: { import_method: 'manual' }
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      setSuccess(true);
      setTimeout(() => {
        navigate(`/city/${cityId}/setup`);
      }, 2000);
    } catch (err: any) {
      console.error('Error importing ballot:', err);
      setError(err.response?.data?.detail || 'Failed to import ballot');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/city/${cityId}/setup`)}
            className="text-blue-600 hover:text-blue-700 mb-4"
          >
            ← Back to Setup
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Import Ballot Data
          </h1>
          <p className="text-gray-600">
            Manually enter your election contests and candidates
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-6">
            Ballot imported successfully! Redirecting...
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Election Date */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Election Information
            </h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Election Date *
              </label>
              <input
                type="date"
                value={electionDate}
                onChange={(e) => setElectionDate(e.target.value)}
                required
                className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Current Contest Form */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Add Contest
            </h2>

            <div className="space-y-4">
              {/* Contest Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contest Type *
                </label>
                <select
                  value={currentContest.type}
                  onChange={(e) => setCurrentContest({ ...currentContest, type: e.target.value as 'race' | 'measure' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="race">Race (Candidates)</option>
                  <option value="measure">Measure (Ballot Proposition)</option>
                </select>
              </div>

              {/* Contest Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contest Title *
                </label>
                <input
                  type="text"
                  value={currentContest.title}
                  onChange={(e) => setCurrentContest({ ...currentContest, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Mayor, City Council District 1, Proposition A"
                />
              </div>

              {/* Race-specific fields */}
              {currentContest.type === 'race' && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Office
                      </label>
                      <input
                        type="text"
                        value={currentContest.office}
                        onChange={(e) => setCurrentContest({ ...currentContest, office: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Mayor, City Councilmember"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Jurisdiction
                      </label>
                      <input
                        type="text"
                        value={currentContest.jurisdiction}
                        onChange={(e) => setCurrentContest({ ...currentContest, jurisdiction: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Citywide, District 1"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Number of Seats
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={currentContest.seat_count}
                      onChange={(e) => setCurrentContest({ ...currentContest, seat_count: parseInt(e.target.value) || 1 })}
                      className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Candidates */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Candidates
                      </label>
                      <button
                        type="button"
                        onClick={addCandidate}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        + Add Candidate
                      </button>
                    </div>

                    {currentContest.candidates.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">No candidates added yet</p>
                    ) : (
                      <div className="space-y-3">
                        {currentContest.candidates.map((candidate, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-medium text-gray-900">Candidate {index + 1}</h4>
                              <button
                                type="button"
                                onClick={() => removeCandidate(index)}
                                className="text-red-600 hover:text-red-700 text-sm"
                              >
                                Remove
                              </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              <input
                                type="text"
                                value={candidate.name}
                                onChange={(e) => updateCandidate(index, 'name', e.target.value)}
                                placeholder="Name *"
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                              <input
                                type="email"
                                value={candidate.email}
                                onChange={(e) => updateCandidate(index, 'email', e.target.value)}
                                placeholder="Email"
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                              <input
                                type="tel"
                                value={candidate.phone}
                                onChange={(e) => updateCandidate(index, 'phone', e.target.value)}
                                placeholder="Phone"
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                              <input
                                type="url"
                                value={candidate.website}
                                onChange={(e) => updateCandidate(index, 'website', e.target.value)}
                                placeholder="Website"
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}

              {/* Measure-specific fields */}
              {currentContest.type === 'measure' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Measure Number
                    </label>
                    <input
                      type="text"
                      value={currentContest.measure_number}
                      onChange={(e) => setCurrentContest({ ...currentContest, measure_number: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Prop A, Measure 1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Measure Text *
                    </label>
                    <textarea
                      value={currentContest.measure_text}
                      onChange={(e) => setCurrentContest({ ...currentContest, measure_text: e.target.value })}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Full text of the ballot measure"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Summary
                    </label>
                    <textarea
                      value={currentContest.summary}
                      onChange={(e) => setCurrentContest({ ...currentContest, summary: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Brief summary of the measure"
                    />
                  </div>
                </>
              )}

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={currentContest.description}
                  onChange={(e) => setCurrentContest({ ...currentContest, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional description"
                />
              </div>

              <button
                type="button"
                onClick={addContest}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add Contest to Ballot
              </button>
            </div>
          </div>

          {/* Added Contests List */}
          {contests.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Added Contests ({contests.length})
              </h2>
              <div className="space-y-3">
                {contests.map((contest, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">{contest.title}</h3>
                        <p className="text-sm text-gray-600">
                          {contest.type === 'race'
                            ? `Race - ${contest.candidates.length} candidate(s)`
                            : 'Measure'}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeContest(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit */}
          {contests.length > 0 && (
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => navigate(`/city/${cityId}/setup`)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
              >
                {loading ? 'Importing...' : 'Import Ballot'}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default CityBallotImportPage;
