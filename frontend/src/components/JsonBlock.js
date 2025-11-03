// JsonBlock component for pretty-printing JSON
import React, { useState } from 'react';

const JsonBlock = ({ data, className = '' }) => {
  const [isCopied, setIsCopied] = useState(false);

  const formatJson = (data) => {
    try {
      if (typeof data === 'string') {
        return JSON.stringify(JSON.parse(data), null, 2);
      }
      return JSON.stringify(data, null, 2);
    } catch (e) {
      return typeof data === 'string' ? data : String(data);
    }
  };

  const handleCopy = () => {
    const jsonString = formatJson(data);
    navigator.clipboard.writeText(jsonString).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };

  if (!data) {
    return (
      <div className={`bg-ubs-gray-100 p-4 text-ubs-gray-500 italic ${className}`}>
        No data available
      </div>
    );
  }

  return (
    <div className={`relative group ${className}`}>
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white shadow-md px-3 py-1 text-sm text-ubs-gray-700 hover:bg-ubs-gray-50 active:scale-95 z-10"
      >
        {isCopied ? 'Copied!' : 'Copy'}
      </button>
      <pre className="bg-ubs-gray-50 border border-ubs-gray-200 p-4 overflow-x-auto font-mono text-sm text-ubs-gray-800 shadow-sm">
        {formatJson(data)}
      </pre>
    </div>
  );
};

export default JsonBlock;