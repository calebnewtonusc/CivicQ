import React from 'react';
import { useParams } from 'react-router-dom';

const ContestPage: React.FC = () => {
  const { contestId } = useParams<{ contestId: string }>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Contest Details</h1>
      <p className="text-gray-600">Contest {contestId} - to be implemented</p>
    </div>
  );
};

export default ContestPage;
