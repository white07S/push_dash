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
  const handleTriggerAI = async (functionName, functionCall) => {
    if (!searchResult) return;

    const itemId = searchResult[idField];
    const desc = description || searchResult.description;

    setAiLoading(prev => ({ ...prev, [functionName]: true }));

    try {
      const result = await functionCall(itemId, desc, false);
      setAiResults(prev => ({ ...prev, [functionName]: result }));

      // Update search result to reflect AI taxonomy computed
      if (functionName === 'taxonomy') {
        setSearchResult(prev => ({ ...prev, ai_taxonomy_present: true }));
      }
    } catch (err) {
      console.error(`Error triggering ${functionName}:`, err);
      setError(err.response?.data?.detail || `Failed to compute ${functionName}`);
    } finally {
      setAiLoading(prev => ({ ...prev, [functionName]: false }));
    }
  };

  // Handle AI function trigger in drawer
  const handleDrawerTriggerFunction = async (functionName, desc) => {
    if (!drawerData) return;

    const itemId = drawerData.raw[idField];
    const functionMap = {
      'taxonomy': api.triggerAITaxonomy,
      'root_causes': api.triggerAIRootCauses,
      'enrichment': api.triggerAIEnrichment,
      'similar_controls': api.triggerSimilarControls,
      'similar_external_loss': api.triggerSimilarExternalLoss,
      'similar_internal_loss': api.triggerSimilarInternalLoss,
      'similar_issues': api.triggerSimilarIssues,
    };

    const functionCall = functionMap[functionName];
    if (!functionCall) return;

    try {
      const result = await functionCall(itemId, desc, false);
      // Update drawer data with new AI results
      setDrawerData(prev => ({
        ...prev,
        ai: {
          ...prev.ai,
          [functionName]: result.payload
        }
      }));
    } catch (err) {
      console.error(`Error triggering ${functionName}:`, err);
      throw err;
    }
  };

  // Truncate description
  const truncateText = (text, maxLength = 200) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

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
            Description (Optional - for AI functions)
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
          <div className="border border-ubs-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <Badge text={searchResult[idField]} variant="primary" size="lg" />
                {searchResult.ai_taxonomy_present && (
                  <Badge text="AI Computed" variant="success" size="sm" className="ml-2" />
                )}
              </div>
              <button
                onClick={handleViewDetails}
                className="px-4 py-2 bg-ubs-gray-100 text-ubs-gray-700 rounded-lg hover:bg-ubs-gray-200 transition-colors"
              >
                View Details
              </button>
            </div>

            <div className="mb-3">
              <p className="text-sm text-ubs-gray-600 mb-1">Description:</p>
              <p className="text-ubs-gray-800">{truncateText(searchResult.description)}</p>
            </div>

            {searchResult.nfr_taxonomy && (
              <div className="mb-3">
                <p className="text-sm text-ubs-gray-600 mb-1">NFR Taxonomy:</p>
                <div className="flex flex-wrap gap-2">
                  {searchResult.nfr_taxonomy.split('|').filter(t => t).map((tax, idx) => (
                    <Badge key={idx} text={tax} variant="info" size="sm" />
                  ))}
                </div>
              </div>
            )}

            {/* AI Taxonomy button/result */}
            {!searchResult.ai_taxonomy_present && !aiResults.taxonomy && (
              <button
                onClick={() => handleTriggerAI('taxonomy', api.triggerAITaxonomy)}
                disabled={aiLoading.taxonomy}
                className={`mt-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  aiLoading.taxonomy
                    ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                    : 'bg-ubs-red text-white hover:bg-ubs-dark-red active:scale-95'
                }`}
              >
                {aiLoading.taxonomy ? 'Computing AI Taxonomy...' : 'Compute AI Taxonomy'}
              </button>
            )}

            {aiResults.taxonomy && (
              <div className="mt-4">
                <p className="text-sm font-medium text-ubs-gray-700 mb-2">AI Taxonomy Result:</p>
                <JsonBlock data={aiResults.taxonomy.payload} />
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
      />
    </div>
  );
};

export default Section;