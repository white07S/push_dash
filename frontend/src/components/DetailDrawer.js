// DetailDrawer component for showing full item details
import React, { useEffect, useState } from 'react';
import JsonBlock from './JsonBlock';
import Badge from './Badge';

const DetailDrawer = ({ isOpen, onClose, title, data, onTriggerFunction }) => {
  const [loading, setLoading] = useState({});

  // Close drawer on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when drawer is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleTriggerFunction = async (functionName) => {
    if (!onTriggerFunction) return;

    setLoading(prev => ({ ...prev, [functionName]: true }));
    try {
      await onTriggerFunction(functionName, data?.raw?.description);
    } catch (error) {
      console.error(`Error triggering ${functionName}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [functionName]: false }));
    }
  };

  const renderAISection = (functionName, displayName, aiData) => {
    const isLoading = loading[functionName];
    const hasData = aiData !== null && aiData !== undefined;

    return (
      <div className="border-t border-ubs-gray-200 pt-4 mt-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-semibold text-ubs-gray-800">{displayName}</h3>
          {!hasData && onTriggerFunction && (
            <button
              onClick={() => handleTriggerFunction(functionName)}
              disabled={isLoading}
              className={`px-4 py-1.5 text-sm font-medium transition-colors ${
                isLoading
                  ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                  : 'bg-ubs-red text-white hover:bg-ubs-dark-red active:scale-95'
              }`}
            >
              {isLoading ? 'Computing...' : 'Compute'}
            </button>
          )}
        </div>
        {hasData ? (
          <JsonBlock data={aiData} />
        ) : (
          <div className="bg-ubs-gray-50 p-4 text-ubs-gray-500 italic">
            Not computed yet
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 animate-fade-in"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full lg:w-2/3 xl:w-1/2 bg-white shadow-xl z-50 animate-slide-in overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-ubs-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-ubs-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-ubs-gray-500 hover:text-ubs-gray-700 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {data ? (
            <>
              {/* Raw Data Section */}
              <div>
                <h3 className="text-lg font-semibold text-ubs-gray-800 mb-3">Raw Data</h3>

                {/* Key fields */}
                <div className="mb-4 space-y-2">
                  {data.raw?.control_id && (
                    <div>
                      <span className="text-ubs-gray-600">Control ID: </span>
                      <Badge text={data.raw.control_id} variant="primary" />
                    </div>
                  )}
                  {data.raw?.ext_loss_id && (
                    <div>
                      <span className="text-ubs-gray-600">External Loss ID: </span>
                      <Badge text={data.raw.ext_loss_id} variant="primary" />
                    </div>
                  )}
                  {data.raw?.loss_id && (
                    <div>
                      <span className="text-ubs-gray-600">Internal Loss ID: </span>
                      <Badge text={data.raw.loss_id} variant="primary" />
                    </div>
                  )}
                  {data.raw?.issue_id && (
                    <div>
                      <span className="text-ubs-gray-600">Issue ID: </span>
                      <Badge text={data.raw.issue_id} variant="primary" />
                    </div>
                  )}
                </div>

                {/* Description */}
                {data.raw?.description && (
                  <div className="mb-4">
                    <span className="text-ubs-gray-600">Description:</span>
                    <p className="mt-1 text-ubs-gray-800 bg-ubs-gray-50 p-3 max-h-40 overflow-y-auto">
                      {data.raw.description}
                    </p>
                  </div>
                )}

                {/* NFR Taxonomy */}
                {data.raw?.nfr_taxonomy && (
                  <div className="mb-4">
                    <span className="text-ubs-gray-600">NFR Taxonomy:</span>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {data.raw.nfr_taxonomy.split('|').filter(t => t).map((taxonomy, index) => (
                        <Badge key={index} text={taxonomy} variant="info" size="sm" />
                      ))}
                    </div>
                  </div>
                )}

                {/* Full raw data */}
                {data.raw?.raw_data && (
                  <div className="mb-4">
                    <span className="text-ubs-gray-600">Complete Data:</span>
                    <div className="mt-2">
                      <JsonBlock data={data.raw.raw_data} />
                    </div>
                  </div>
                )}
              </div>

              {/* AI Results Section */}
              {data.ai && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-ubs-gray-800 mb-3">AI Analysis</h3>

                  {/* AI Taxonomy */}
                  {renderAISection('taxonomy', 'AI Taxonomy', data.ai.taxonomy)}

                  {/* Root Causes */}
                  {renderAISection('root_causes', 'Root Cause Analysis', data.ai.root_causes)}

                  {/* Enrichment */}
                  {renderAISection('enrichment', 'AI Enrichment', data.ai.enrichment)}

                  {/* Similar Items */}
                  {data.ai.similar_controls !== undefined &&
                    renderAISection('similar_controls', 'Similar Controls', data.ai.similar_controls)}
                  {data.ai.similar_external_loss !== undefined &&
                    renderAISection('similar_external_loss', 'Similar External Losses', data.ai.similar_external_loss)}
                  {data.ai.similar_internal_loss !== undefined &&
                    renderAISection('similar_internal_loss', 'Similar Internal Losses', data.ai.similar_internal_loss)}
                  {data.ai.similar_issues !== undefined &&
                    renderAISection('similar_issues', 'Similar Issues', data.ai.similar_issues)}
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-ubs-gray-500 py-8">
              <p>No data available</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default DetailDrawer;