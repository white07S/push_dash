// DataTable component with pagination
import React, { useState, useEffect, useCallback } from 'react';
import Badge from './Badge';
import DetailDrawer from './DetailDrawer';

const DataTable = ({
  title,
  api,
  idField,
  sessionId,
  userId
}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState(null);
  const [aiLoading, setAiLoading] = useState({});

  const { meta = {}, aiTriggers = {} } = api;
  const primaryFunction = meta.primaryFunction || Object.keys(aiTriggers)[0] || null;
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

  const itemsPerPage = 20;

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const offset = (currentPage - 1) * itemsPerPage;
      const result = await api.list(offset, itemsPerPage);
      setData(result.items || []);
      setTotalItems(result.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  }, [api, currentPage]);

  const handleSearch = useCallback(async () => {
    if (!searchTerm.trim()) {
      loadData();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.search(searchTerm, 100);
      setData(result.items || []);
      setTotalItems(result.items?.length || 0);
      setCurrentPage(1);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
      setData([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [api, loadData, searchTerm]);

  // Load data when component mounts or page/search criteria change
  useEffect(() => {
    if (searchTerm) {
      handleSearch();
    } else {
      loadData();
    }
  }, [searchTerm, loadData, handleSearch]);

  const handleViewDetails = async (item) => {
    setLoading(true);

    try {
      const details = await api.getDetails(item[idField]);
      setDrawerData(details);
      setDrawerOpen(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load details');
      console.error('Details error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerAI = async (item) => {
    if (!primaryFunction) return;

    const itemId = item[idField];
    const key = `${itemId}_${primaryFunction}`;
    const triggerFunc = aiTriggers[primaryFunction];
    if (!triggerFunc) return;

    const contextValue = item.record?.[titleField] || item[titleField] || '';

    setAiLoading(prev => ({ ...prev, [key]: true }));

    try {
      const result = await triggerFunc(itemId, contextValue, false);
      const updatedData = [...data];
      const index = updatedData.findIndex(d => d[idField] === itemId);
      if (index !== -1) {
        const currentStatus = updatedData[index].ai_status || {};
        updatedData[index] = {
          ...updatedData[index],
          ai_status: { ...currentStatus, [primaryFunction]: true }
        };
        setData(updatedData);
      }
      return result;
    } catch (err) {
      console.error(`Error triggering ${primaryFunction}:`, err);
      setError(err.response?.data?.detail || `Failed to compute ${formatFunctionLabel(primaryFunction)}`);
    } finally {
      setAiLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleDrawerTriggerFunction = async (functionKey, desc) => {
    if (!drawerData) return;

    const itemId = drawerData.raw[idField];
    const triggerFunc = aiTriggers[functionKey];
    if (!triggerFunc) return;
    const contextValue =
      desc || drawerData.raw?.record?.[titleField] || drawerData.raw?.[titleField] || '';

    try {
      const result = await triggerFunc(itemId, contextValue, false);
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

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const truncateText = (text, maxLength = 150) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const renderPagination = () => {
    const pages = [];
    const maxVisible = 5;
    const halfVisible = Math.floor(maxVisible / 2);

    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, currentPage + halfVisible);

    if (currentPage <= halfVisible) {
      endPage = Math.min(totalPages, maxVisible);
    }
    if (currentPage > totalPages - halfVisible) {
      startPage = Math.max(1, totalPages - maxVisible + 1);
    }

    if (startPage > 1) {
      pages.push(
        <button
          key="first"
          onClick={() => goToPage(1)}
          className="px-3 py-1 border border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50"
        >
          1
        </button>
      );
      if (startPage > 2) {
        pages.push(<span key="dots1" className="px-2">...</span>);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => goToPage(i)}
          className={`px-3 py-1 border ${
            i === currentPage
              ? 'bg-ubs-red text-white border-ubs-red'
              : 'border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50'
          }`}
        >
          {i}
        </button>
      );
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(<span key="dots2" className="px-2">...</span>);
      }
      pages.push(
        <button
          key="last"
          onClick={() => goToPage(totalPages)}
          className="px-3 py-1 border border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50"
        >
          {totalPages}
        </button>
      );
    }

    return pages;
  };

  return (
    <div className="bg-white shadow-sm border border-ubs-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-ubs-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-ubs-gray-900">{title}</h2>
            <span className="px-3 py-1 bg-ubs-gray-100 text-ubs-gray-700 rounded-md text-sm font-medium">
              Total: {totalItems.toLocaleString()} records
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder={`Search by ${idField}...`}
              className="px-4 py-2 border border-ubs-gray-300 focus:outline-none focus:ring-2 focus:ring-ubs-red focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className={`px-6 py-2 font-medium transition-colors ${
                loading
                  ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                  : 'bg-ubs-red text-white hover:bg-ubs-dark-red active:scale-95'
              }`}
            >
              Search
            </button>
            {searchTerm && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  loadData();
                }}
                className="px-4 py-2 border border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="inline-block animate-spin h-8 w-8 border-b-2 border-ubs-red"></div>
            <p className="ml-4 text-ubs-gray-600">Loading...</p>
          </div>
        ) : data.length > 0 ? (
          <table className="w-full">
            <thead className="bg-ubs-gray-50 border-b border-ubs-gray-200 sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                  Title
                </th>
                {typeField && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                    Type
                  </th>
                )}
                <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                  Risk Theme
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                  AI Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-ubs-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ubs-gray-200">
              {data.map((item) => {
                const itemId = item[idField];
                const aiKey = `${itemId}_${primaryFunction}`;
                const isAiLoading = aiLoading[aiKey];
                const aiStatus = primaryFunction ? item.ai_status?.[primaryFunction] : false;
                const titleValue = item[titleField] || item.title || '';
                const typeValue = typeField ? (item[typeField] ?? item.category ?? '') : null;
                const themeValue = item[themeField] || item.risk_theme || '';
                const subthemeValue = item[subthemeField] || item.risk_subtheme || '';

                return (
                  <tr key={itemId} className="hover:bg-ubs-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge text={itemId} variant="primary" />
                    </td>
                    <td className="px-6 py-4 text-sm text-ubs-gray-900">
                      {truncateText(titleValue)}
                    </td>
                    {typeField && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-ubs-gray-700">
                        {typeValue ? <Badge text={typeValue} size="sm" /> : '—'}
                      </td>
                    )}
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {themeValue && <Badge text={themeValue} variant="info" size="sm" />}
                        {subthemeValue && <Badge text={subthemeValue} size="sm" />}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {primaryFunction ? (
                        aiStatus ? (
                          <Badge text="Computed" variant="success" size="sm" />
                        ) : (
                          <button
                            onClick={() => handleTriggerAI(item)}
                            disabled={isAiLoading}
                            className={`px-3 py-1 text-xs font-medium transition-colors ${
                              isAiLoading
                                ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                                : 'bg-ubs-red text-white hover:bg-ubs-dark-red'
                            }`}
                            aria-label={`Compute ${formatFunctionLabel(primaryFunction)}`}
                          >
                            {isAiLoading ? 'Computing...' : 'Compute'}
                          </button>
                        )
                      ) : (
                        <span className="text-xs text-ubs-gray-500">No AI functions</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleViewDetails(item)}
                        className="px-4 py-1 text-sm font-medium bg-ubs-gray-100 text-ubs-gray-700 hover:bg-ubs-gray-200 transition-colors"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="flex items-center justify-center h-64 text-ubs-gray-500">
            No data available
          </div>
        )}
      </div>

      {/* Pagination */}
      {!loading && data.length > 0 && (
        <div className="border-t border-ubs-gray-200 px-6 py-3 flex items-center justify-between bg-white">
          <div className="text-sm text-ubs-gray-700">
            Showing {((currentPage - 1) * itemsPerPage) + 1} to{' '}
            {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} items
          </div>
          {totalPages > 1 && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                className={`px-3 py-1 border ${
                  currentPage === 1
                    ? 'border-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                    : 'border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50'
                }`}
              >
                Previous
              </button>
              {renderPagination()}
              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`px-3 py-1 border ${
                  currentPage === totalPages
                    ? 'border-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
                    : 'border-ubs-gray-300 text-ubs-gray-700 hover:bg-ubs-gray-50'
                }`}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}

      {/* Detail Drawer */}
      <DetailDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`${title} Details`}
        data={drawerData}
        onTriggerFunction={handleDrawerTriggerFunction}
        aiFunctions={Object.keys(aiTriggers)}
        functionLabels={functionLabels}
        meta={{ idField, titleField, typeField, themeField, subthemeField }}
      />
    </div>
  );
};

export default DataTable;
