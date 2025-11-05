// Section component for dataset management
import React, { useState } from 'react';
import SearchBar from './SearchBar';
import JsonBlock from './JsonBlock';
import Badge from './Badge';
import DetailDrawer from './DetailDrawer';

const Section = ({
  title,
  api,
  idField,
  placeholder = 'Enter ID...',
  sessionId,
  userId
}) => {
  const [searchId, setSearchId] = useState('');
  const [description, setDescription] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiResults, setAiResults] = useState({});
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState(null);
  const [aiLoading, setAiLoading] = useState({});

  const { meta = {}, aiTriggers = {} } = api;
  const functionKeys = Object.keys(aiTriggers);
  const primaryFunction = meta.primaryFunction || functionKeys[0] || null;
  const titleField = meta.titleField || 'title';
  const typeField = meta.typeField || 'category';
  const themeField = meta.themeField || 'risk_theme';
  const subthemeField = meta.subthemeField || 'risk_subtheme';
  const functionLabels = meta.functionLabels || {};

  const formatFunctionLabel = (key) => {
    if (!key) return '';
    if (functionLabels[key]) {
      return functionLabels[key];
    }
    return key
      .split('_')
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  };

  const searchMeta = searchResult
    ? {
        aiStatus: searchResult.ai_status || {},
        titleValue: searchResult[titleField] || searchResult.title || '',
        typeValue: typeField ? (searchResult[typeField] ?? searchResult.category ?? '') : null,
        themeValue: searchResult[themeField] || searchResult.risk_theme || '',
        subthemeValue: searchResult[subthemeField] || searchResult.risk_subtheme || ''
      }
    : null;

  // Handle search
  const handleSearch = async (id) => {
    setLoading(true);
    setError(null);
    setSearchResult(null);
    setAiResults({});

    try {
      const result = await api.search(id, 1);
      if (result.items && result.items.length > 0) {
        setSearchResult(result.items[0]);
      } else {
        setError('No results found');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle view details
  const handleViewDetails = async () => {
    if (!searchResult) return;

    const itemId = searchResult[idField];
    setLoading(true);

    try {
      const details = await api.getDetails(itemId);
      setDrawerData(details);
      setDrawerOpen(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load details');
      console.error('Details error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle AI function trigger in main view
  const handleTriggerAI = async (functionKey) => {
    if (!searchResult) return;

    const triggerFunc = aiTriggers[functionKey];
    if (!triggerFunc) return;

    const itemId = searchResult[idField];
    const contextValue =
      description || searchResult.record?.[titleField] || searchResult[titleField] || '';

    setAiLoading(prev => ({ ...prev, [functionKey]: true }));

    try {
      const result = await triggerFunc(itemId, contextValue, false);
      setAiResults(prev => ({ ...prev, [functionKey]: result }));
      setSearchResult(prev => ({
        ...prev,
        ai_status: {
          ...(prev?.ai_status || {}),
          [functionKey]: true
        }
      }));
    } catch (err) {
      console.error(`Error triggering ${functionKey}:`, err);
      setError(err.response?.data?.detail || `Failed to compute ${formatFunctionLabel(functionKey)}`);
    } finally {
      setAiLoading(prev => ({ ...prev, [functionKey]: false }));
    }
  };

  // Handle AI function trigger in drawer
  const handleDrawerTriggerFunction = async (functionKey, desc) => {
    if (!drawerData) return;

    const itemId = drawerData.raw[idField];
    const triggerFunc = aiTriggers[functionKey];
    if (!triggerFunc) return;
    const contextValue =
      desc || drawerData.raw?.record?.[titleField] || drawerData.raw?.[titleField] || '';

    try {
      const result = await triggerFunc(itemId, contextValue, false);
      // Update drawer data with new AI results
      setDrawerData(prev => ({
        ...prev,
        ai: {
          ...prev.ai,
          [functionKey]: result.payload
        }
      }));
    } catch (err) {
      console.error(`Error triggering ${functionKey}:`, err);
      throw err;
    }
  };

  // Truncate description
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-ubs-gray-900 mb-6">{title}</h2>

      {/* Search inputs */}
      <div className="space-y-4 mb-6">
        <SearchBar
          placeholder={placeholder}
          onSearch={handleSearch}
          value={searchId}
          onChange={setSearchId}
          disabled={loading}
        />

        <div>
          <label className="block text-sm font-medium text-ubs-gray-700 mb-1">
            Context (Optional - overrides default input)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter description override for AI functions..."
            className="w-full px-4 py-2 border border-ubs-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ubs-red focus:border-transparent resize-none"
            rows={3}
          />
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-ubs-red"></div>
          <p className="mt-2 text-ubs-gray-600">Loading...</p>
        </div>
      )}

      {/* Search result */}
      {searchResult && !loading && (
        <div className="space-y-4">
          {/* Result card */}
          <div className="border border-ubs-gray-200 rounded-lg p-4 space-y-4">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-2">
                <Badge text={searchResult[idField]} variant="primary" size="lg" />
                {primaryFunction && searchMeta?.aiStatus?.[primaryFunction] && (
                  <Badge text="AI Computed" variant="success" size="sm" />
                )}
              </div>
              <button
                onClick={handleViewDetails}
                className="px-4 py-2 bg-ubs-gray-100 text-ubs-gray-700 rounded-lg hover:bg-ubs-gray-200 transition-colors"
              >
                View Details
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-ubs-gray-600 mb-1">Title:</p>
                <p className="text-ubs-gray-800">{searchMeta?.titleValue || '—'}</p>
              </div>
              {typeField && (
                <div>
                  <p className="text-sm text-ubs-gray-600 mb-1">Type:</p>
                  {searchMeta?.typeValue ? (
                    <Badge text={searchMeta.typeValue} size="sm" />
                  ) : (
                    <p className="text-ubs-gray-500 text-sm">—</p>
                  )}
                </div>
              )}
              <div>
                <p className="text-sm text-ubs-gray-600 mb-1">Risk Theme:</p>
                <div className="flex flex-wrap gap-2">
                  {searchMeta?.themeValue && <Badge text={searchMeta.themeValue} variant="info" size="sm" />}
                  {searchMeta?.subthemeValue && <Badge text={searchMeta.subthemeValue} size="sm" />}
                </div>
              </div>
            </div>

            {functionKeys.length > 0 && (
              <div className="space-y-4">
                {functionKeys.map((fnKey) => {
                  const isComputed = !!searchMeta?.aiStatus?.[fnKey];
                  const isLoadingFn = aiLoading[fnKey];
                  const label = formatFunctionLabel(fnKey);
                  const result = aiResults[fnKey];
                  return (
                    <div key={fnKey} className="border border-ubs-gray-100 rounded-md p-3 bg-ubs-gray-50">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-semibold text-ubs-gray-700">{label}</h4>
                        <div className="flex items-center gap-2">
                          {isComputed && !isLoadingFn && (
                            <Badge text="Computed" variant="success" size="sm" />
                          )}
                          <button
                            onClick={() => handleTriggerAI(fnKey)}
                            disabled={isLoadingFn}
                            className={`px-3 py-1 text-xs font-medium transition-colors ${
                              isLoadingFn
                                ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                                : 'bg-ubs-red text-white hover:bg-ubs-dark-red active:scale-95'
                            }`}
                          >
                            {isLoadingFn ? 'Computing...' : isComputed ? 'Recompute' : 'Compute'}
                          </button>
                        </div>
                      </div>
                      {result && result.payload && (
                        <div className="mt-3">
                          <JsonBlock data={result.payload} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Detail Drawer */}
      <DetailDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`${title} Details`}
        data={drawerData}
        onTriggerFunction={handleDrawerTriggerFunction}
        aiFunctions={functionKeys}
        functionLabels={functionLabels}
        meta={{ idField, titleField, typeField, themeField, subthemeField }}
      />
    </div>
  );
};

export default Section;
