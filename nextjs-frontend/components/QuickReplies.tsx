'use client';

import React from 'react';

interface QuickRepliesProps {
  suggestions: string[];
  onSend: (message: string) => void;
}

export function QuickReplies({ suggestions, onSend }: QuickRepliesProps) {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-3">
      <div
        className="flex gap-2 overflow-x-auto quick-replies-scroll pb-1"
        role="group"
        aria-label="Quick reply suggestions"
      >
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSend(suggestion)}
            className="quick-reply-btn flex-shrink-0 px-4 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-full text-sm text-gray-700 dark:text-gray-200 hover:border-sjsu-blue hover:text-sjsu-blue dark:hover:border-sjsu-gold dark:hover:text-sjsu-gold transition-colors focus-ring"
            tabIndex={0}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
