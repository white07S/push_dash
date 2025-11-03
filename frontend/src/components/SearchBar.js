// SearchBar component with debounce
import React, { useState, useEffect } from 'react';

const SearchBar = ({
  placeholder = 'Enter ID...',
  onSearch,
  debounceMs = 300,
  disabled = false,
  value: externalValue
}) => {
  const [inputValue, setInputValue] = useState(externalValue || '');
  const [isDebouncing, setIsDebouncing] = useState(false);

  // Update internal value when external value changes
  useEffect(() => {
    if (externalValue !== undefined) {
      setInputValue(externalValue);
    }
  }, [externalValue]);

  // Debounce search
  useEffect(() => {
    if (!inputValue) {
      setIsDebouncing(false);
      return;
    }

    setIsDebouncing(true);
    const timer = setTimeout(() => {
      setIsDebouncing(false);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [inputValue, debounceMs]);

  const handleSearch = () => {
    if (inputValue.trim() && !isDebouncing && onSearch) {
      onSearch(inputValue.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleChange = (e) => {
    setInputValue(e.target.value);
  };

  const isSearchDisabled = disabled || isDebouncing || !inputValue.trim();

  return (
    <div className="flex space-x-2">
      <input
        type="text"
        value={inputValue}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 px-4 py-2 border border-ubs-gray-300 focus:outline-none focus:ring-2 focus:ring-ubs-red focus:border-transparent disabled:bg-ubs-gray-100 disabled:cursor-not-allowed"
      />
      <button
        onClick={handleSearch}
        disabled={isSearchDisabled}
        className={`px-6 py-2 font-medium transition-colors ${
          isSearchDisabled
            ? 'bg-ubs-gray-200 text-ubs-gray-400 cursor-not-allowed'
            : 'bg-ubs-red text-white hover:bg-ubs-dark-red active:scale-95'
        }`}
      >
        {isDebouncing ? 'Wait...' : 'Search'}
      </button>
    </div>
  );
};

export default SearchBar;