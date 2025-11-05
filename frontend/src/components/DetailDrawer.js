// DetailDrawer component for showing full item details
import React, { useEffect, useState } from 'react';
import JsonBlock from './JsonBlock';
import Badge from './Badge';

const DetailDrawer = ({
  isOpen,
  onClose,
  title,
  data,
  onTriggerFunction,
  aiFunctions = [],
  functionLabels = {},
  meta = {}
}) => {
  const [loading, setLoading] = useState({});

  const {
    idField = 'id',
    titleField = 'title',
    typeField = 'category',
    themeField = 'risk_theme',
    subthemeField = 'risk_subtheme'
  } = meta;

  const raw = data?.raw || {};
  const record = raw.record || {};
  const idValue = raw[idField] || record[idField] || '';
  const titleValue = record[titleField] || raw[titleField] || '';
  const typeValue = typeField ? (record[typeField] ?? raw[typeField]) : null;
  const themeValue = record[themeField] || raw[themeField] || '';
  const subthemeValue = record[subthemeField] || raw[subthemeField] || '';

  const aiKeys = aiFunctions.length ? aiFunctions : Object.keys(data?.ai || {});

  const labelForFunction = (key) => {
    if (!key) return '';
    if (functionLabels[key]) {
      return functionLabels[key];
    }
    return key
      .split('_')
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  };

  const handleTriggerFunction = async (functionKey) => {
    if (!onTriggerFunction) return;
    setLoading(prev => ({ ...prev, [functionKey]: true }));
    try {
      await onTriggerFunction(functionKey);
    } catch (error) {
      console.error(`Error triggering ${functionKey}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [functionKey]: false }));
    }
  };

  const renderAISection = (functionKey, aiData) => {
    const displayName = labelForFunction(functionKey);
    const isLoading = loading[functionKey];
    const hasData = aiData !== null && aiData !== undefined;

    return (
      <div className="border-t border-ubs-gray-200 pt-4 mt-4" key={functionKey}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-semibold text-ubs-gray-800">{displayName}</h3>
          {!hasData && onTriggerFunction && (
            <button
              onClick={() => handleTriggerFunction(functionKey)}
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

  // Close drawer on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

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
                <h3 className="text-lg font-semibold text-ubs-gray-800 mb-3">Summary</h3>

                <div className="mb-4 space-y-2">
                  {idValue && (
                    <div>
                      <span className="text-ubs-gray-600">ID: </span>
                      <Badge text={idValue} variant="primary" />
                    </div>
                  )}
                  {titleValue && (
                    <div>
                      <span className="text-ubs-gray-600">Title: </span>
                      <span className="text-ubs-gray-800">{titleValue}</span>
                    </div>
                  )}
                  {typeField && (
                    <div>
                      <span className="text-ubs-gray-600">Type: </span>
                      {typeValue ? <Badge text={typeValue} size="sm" /> : <span className="text-ubs-gray-500">—</span>}
                    </div>
                  )}
                  {(themeValue || subthemeValue) && (
                    <div>
                      <span className="text-ubs-gray-600">Risk Theme: </span>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {themeValue && <Badge text={themeValue} variant="info" size="sm" />}
                        {subthemeValue && <Badge text={subthemeValue} size="sm" />}
                      </div>
                    </div>
                  )}
                </div>

                {/* Full raw data */}
                {record && Object.keys(record).length > 0 && (
                  <div className="mb-4">
                    <span className="text-ubs-gray-600">Complete Data:</span>
                    <div className="mt-2">
                      <JsonBlock data={record} />
                    </div>
                  </div>
                )}
              </div>

              {/* AI Results Section */}
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-ubs-gray-800 mb-3">AI Analysis</h3>
                {aiKeys.length === 0 && (
                  <div className="bg-ubs-gray-50 p-4 text-ubs-gray-500 italic">
                    No AI functions configured
                  </div>
                )}
                {aiKeys.map((fnKey) => {
                  const aiData = data.ai?.[fnKey] || null;
                  return renderAISection(fnKey, aiData);
                })}
              </div>
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
