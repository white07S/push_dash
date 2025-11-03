// Dashboard component with 4 dataset sections using tables
import React, { useState } from 'react';
import DataTable from './components/DataTable';
import controlsAPI from './api/controls';
import externalLossAPI from './api/externalLoss';
import internalLossAPI from './api/internalLoss';
import issuesAPI from './api/issues';

const Dashboard = ({ sessionId, userId }) => {
  const [activeTab, setActiveTab] = useState('controls');

  const tabs = [
    { id: 'controls', label: 'Controls', color: 'text-blue-600' },
    { id: 'external', label: 'External Loss', color: 'text-green-600' },
    { id: 'internal', label: 'Internal Loss', color: 'text-orange-600' },
    { id: 'issues', label: 'Issues', color: 'text-purple-600' }
  ];

  const renderSection = () => {
    switch (activeTab) {
      case 'controls':
        return (
          <DataTable
            title="Controls"
            api={controlsAPI}
            idField="control_id"
            sessionId={sessionId}
            userId={userId}
          />
        );
      case 'external':
        return (
          <DataTable
            title="External Loss"
            api={externalLossAPI}
            idField="ext_loss_id"
            sessionId={sessionId}
            userId={userId}
          />
        );
      case 'internal':
        return (
          <DataTable
            title="Internal Loss"
            api={internalLossAPI}
            idField="loss_id"
            sessionId={sessionId}
            userId={userId}
          />
        );
      case 'issues':
        return (
          <DataTable
            title="Issues"
            api={issuesAPI}
            idField="issue_id"
            sessionId={sessionId}
            userId={userId}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-ubs-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-ubs-gray-200 flex-shrink-0">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-3">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-ubs-gray-900">
                NFR Dashboard
              </h1>
              <div className="ml-4 h-6 w-px bg-ubs-gray-300"></div>
              <span className="ml-4 text-sm text-ubs-gray-600">
                Session: {sessionId} | User: {userId}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 animate-pulse"></div>
              <span className="text-sm text-ubs-gray-600">Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-ubs-gray-200 flex-shrink-0">
        <div className="px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-3 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-ubs-red text-ubs-red'
                    : 'border-transparent text-ubs-gray-500 hover:text-ubs-gray-700 hover:border-ubs-gray-300'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content - Full Height */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full animate-fade-in">
          {renderSection()}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-ubs-gray-200 flex-shrink-0">
        <div className="px-4 sm:px-6 lg:px-8 py-2">
          <p className="text-center text-xs text-ubs-gray-500">
            NFR Dashboard © 2025 - Built with React + FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;