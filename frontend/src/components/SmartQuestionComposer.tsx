import React, { useState, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { llmAPI } from '../services/api';
import { QuestionAnalysis } from '../types';

interface SmartQuestionComposerProps {
  contestId: number;
  onSubmit: (questionText: string) => void;
  onCancel: () => void;
}

const SmartQuestionComposer: React.FC<SmartQuestionComposerProps> = ({
  contestId,
  onSubmit,
  onCancel,
}) => {
  const [questionText, setQuestionText] = useState('');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState<QuestionAnalysis | null>(null);
  const [isDuplicate, setIsDuplicate] = useState(false);

  // Analyze question mutation
  const analyzeMutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await llmAPI.analyzeQuestion(text, contestId);
      return response.analysis;
    },
    onSuccess: (data) => {
      setAnalysis(data);
      setShowAnalysis(true);
    },
  });

  // Check duplicate mutation
  const duplicateCheckMutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await llmAPI.checkDuplicate(text, contestId);
      return response;
    },
    onSuccess: (data) => {
      setIsDuplicate(data.is_duplicate);
    },
  });

  // Get suggested questions
  const { data: suggestedQuestions } = useQuery({
    queryKey: ['suggested-questions', contestId],
    queryFn: async () => {
      const response = await llmAPI.getSuggestedQuestions(contestId, 3);
      return response.questions;
    },
    enabled: questionText.length === 0, // Only show when starting fresh
  });

  // Auto-analyze when user pauses typing
  useEffect(() => {
    if (questionText.length < 10) {
      setShowAnalysis(false);
      setAnalysis(null);
      setIsDuplicate(false);
      return;
    }

    const timer = setTimeout(() => {
      analyzeMutation.mutate(questionText);
      duplicateCheckMutation.mutate(questionText);
    }, 1500);

    return () => clearTimeout(timer);
  }, [questionText]);

  const handleUseSuggestion = (suggestion: string) => {
    setQuestionText(suggestion);
  };

  const handleUseImprovedVersion = () => {
    if (analysis?.improved_version) {
      setQuestionText(analysis.improved_version);
    }
  };

  const handleSubmit = () => {
    if (!analysis?.is_appropriate) {
      alert('This question appears to be inappropriate. Please revise it.');
      return;
    }
    if (isDuplicate) {
      if (!confirm('This question appears to be a duplicate. Submit anyway?')) {
        return;
      }
    }
    onSubmit(questionText);
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold mb-4">Ask a Question</h3>

      {/* Question Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Question
        </label>
        <textarea
          value={questionText}
          onChange={(e) => setQuestionText(e.target.value)}
          placeholder="What would you like to ask the candidates?"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={4}
        />
        <p className="text-sm text-gray-500 mt-1">
          {questionText.length} characters
        </p>
      </div>

      {/* AI Analysis */}
      {showAnalysis && analysis && (
        <div className="mb-4 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold">AI Analysis</h4>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getQualityColor(analysis.quality_score)}`}>
              Quality: {Math.round(analysis.quality_score)}/100
            </div>
          </div>

          {/* Category */}
          <div className="mb-2">
            <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
              {analysis.category}
              {analysis.subcategory && ` • ${analysis.subcategory}`}
            </span>
          </div>

          {/* Appropriateness Warning */}
          {!analysis.is_appropriate && (
            <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
              <p className="text-red-800 text-sm font-medium">
                This question may not be appropriate for public discourse.
              </p>
            </div>
          )}

          {/* Duplicate Warning */}
          {isDuplicate && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
              <p className="text-yellow-800 text-sm font-medium">
                ⚠️ Similar question already exists
              </p>
            </div>
          )}

          {/* Issues */}
          {analysis.issues.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">Issues:</p>
              <ul className="list-disc list-inside space-y-1">
                {analysis.issues.map((issue, i) => (
                  <li key={i} className="text-sm text-gray-600">
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggestions */}
          {analysis.suggestions.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-1">
                Suggestions:
              </p>
              <ul className="list-disc list-inside space-y-1">
                {analysis.suggestions.map((suggestion, i) => (
                  <li key={i} className="text-sm text-gray-600">
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Improved Version */}
          {analysis.improved_version && (
            <div className="bg-green-50 border border-green-200 rounded p-3">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Suggested improvement:
              </p>
              <p className="text-sm text-gray-800 mb-2 italic">
                "{analysis.improved_version}"
              </p>
              <button
                onClick={handleUseImprovedVersion}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Use this version
              </button>
            </div>
          )}
        </div>
      )}

      {/* Suggested Questions */}
      {!questionText && suggestedQuestions && suggestedQuestions.length > 0 && (
        <div className="mb-4 border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold mb-3">Suggested Questions</h4>
          <div className="space-y-2">
            {suggestedQuestions.map((suggestion: string, i: number) => (
              <button
                key={i}
                onClick={() => handleUseSuggestion(suggestion)}
                className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm transition"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleSubmit}
          disabled={!questionText.trim() || analyzeMutation.isPending}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
        >
          {analyzeMutation.isPending ? 'Analyzing...' : 'Submit Question'}
        </button>
        <button
          onClick={onCancel}
          className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition"
        >
          Cancel
        </button>
      </div>

      {/* AI Powered Badge */}
      <div className="mt-4 flex items-center justify-center gap-2 text-xs text-gray-500">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a8 8 0 100 16 8 8 0 000-16zM9 9a1 1 0 112 0v4a1 1 0 11-2 0V9zm1-4a1 1 0 100 2 1 1 0 000-2z" />
        </svg>
        <span>AI-powered by Claude</span>
      </div>
    </div>
  );
};

export default SmartQuestionComposer;
