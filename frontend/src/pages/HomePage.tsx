import React from 'react';

const HomePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-civic-blue mb-4">
          CivicQ
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Turning campaigning into a standardized, verifiable public record of candidates
          answering the public's top questions, city by city, with integrity by design.
        </p>
      </header>

      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-semibold mb-4">Welcome to CivicQ</h2>
        <p className="text-gray-700 mb-4">
          This is the CivicQ MVP. The platform will allow:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-700 mb-6">
          <li>Voters to submit and rank questions for local candidates</li>
          <li>Candidates to record structured video answers</li>
          <li>Transparent, anti-polarization question ranking</li>
          <li>Side-by-side candidate comparisons</li>
          <li>Full ballot information in one place</li>
        </ul>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800 font-medium">
            🚧 This application is under active development
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
