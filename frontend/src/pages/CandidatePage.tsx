import React from 'react';
import { useParams } from 'react-router-dom';

const CandidatePage: React.FC = () => {
  const { candidateId } = useParams<{ candidateId: string }>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Candidate Profile</h1>
      <p className="text-gray-600">Candidate {candidateId} - to be implemented</p>
    </div>
  );
};

export default CandidatePage;
