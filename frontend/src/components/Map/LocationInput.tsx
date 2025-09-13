import React, { useState, useEffect, useRef, useCallback } from 'react';
import { geocodingService } from '../../services/geocodingService';
import { Location } from '../../types/map';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface LocationInputProps {
  value?: Location | null;
  onChange: (location: Location | null) => void;
  placeholder?: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  proximity?: [number, number];
}

function LocationInput({
  value,
  onChange,
  placeholder = 'Search for a location...',
  label,
  required = false,
  disabled = false,
  className = '',
  proximity,
}: LocationInputProps) {
  const [query, setQuery] = useState(value?.name || '');
  const [suggestions, setSuggestions] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Update query when value changes externally
  useEffect(() => {
    if (value) {
      setQuery(value.name);
    } else {
      setQuery('');
    }
  }, [value]);

  // Debounced search function
  const searchLocations = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      setIsLoading(true);
      const results = await geocodingService.getAutocompleteSuggestions(searchQuery, {
        proximity,
        limit: 5,
      });
      setSuggestions(results);
      setShowSuggestions(true);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Location search error:', error);
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setIsLoading(false);
    }
  }, [proximity]);

  // Handle input change with debouncing
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);

    // Clear existing timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // If query is empty, clear selection
    if (!newQuery.trim()) {
      onChange(null);
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Debounce search
    debounceRef.current = setTimeout(() => {
      searchLocations(newQuery);
    }, 300);
  }, [onChange, searchLocations]);

  // Handle suggestion selection
  const handleSuggestionSelect = useCallback((location: Location) => {
    setQuery(location.name);
    onChange(location);
    setShowSuggestions(false);
    setSelectedIndex(-1);
    inputRef.current?.blur();
  }, [onChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedIndex]);
        }
        break;
      
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  }, [showSuggestions, suggestions, selectedIndex, handleSuggestionSelect]);

  // Handle input focus
  const handleFocus = useCallback(() => {
    if (suggestions.length > 0) {
      setShowSuggestions(true);
    }
  }, [suggestions.length]);

  // Handle input blur
  const handleBlur = useCallback(() => {
    // Delay hiding suggestions to allow for clicks
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }, 200);
  }, []);

  // Clear selection
  const handleClear = useCallback(() => {
    setQuery('');
    onChange(null);
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  }, [onChange]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {isLoading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          ) : (
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          )}
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          className={`form-input pl-10 ${value ? 'pr-10' : ''}`}
          autoComplete="off"
        />
        
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            disabled={disabled}
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-auto"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion.metadata?.id || index}
              type="button"
              onClick={() => handleSuggestionSelect(suggestion)}
              className={`w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 focus:bg-gray-50 dark:focus:bg-gray-700 focus:outline-none ${
                index === selectedIndex ? 'bg-gray-50 dark:bg-gray-700' : ''
              }`}
            >
              <div className="flex items-start space-x-3">
                <MapPinIcon className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {suggestion.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {suggestion.address}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* No results message */}
      {showSuggestions && suggestions.length === 0 && query.length >= 2 && !isLoading && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg">
          <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
            No locations found for "{query}"
          </div>
        </div>
      )}
    </div>
  );
}

export default LocationInput;