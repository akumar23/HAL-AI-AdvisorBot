'use client';

import React from 'react';

export function TypingIndicator() {
  return (
    <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-sjsu-blue rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-bold">H</span>
        </div>
        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-full px-4 py-2">
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
        </div>
      </div>
    </div>
  );
}
