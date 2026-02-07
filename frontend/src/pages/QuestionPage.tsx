import React from 'react';
import { useParams } from 'react-router-dom';

const QuestionPage: React.FC = () => {
  const { questionId } = useParams<{ questionId: string }>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Question Details</h1>
      <p className="text-gray-600">Question {questionId} - to be implemented</p>
    </div>
  );
};

export default QuestionPage;
