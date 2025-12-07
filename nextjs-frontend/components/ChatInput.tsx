'use client';

import React, { useState, KeyboardEvent } from 'react';
import { ADVISOR_URL } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTalkToHuman = () => {
    window.open(ADVISOR_URL, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg z-50">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-sjsu-blue focus:outline-none"
            placeholder="Type your message..."
            aria-label="Type your message"
            autoComplete="off"
            disabled={disabled}
          />
          <button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            className="p-3 bg-sjsu-blue hover:bg-blue-700 text-white rounded-xl transition-colors focus-ring disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Send message"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-2">
          Press Enter to send •{' '}
          <button
            onClick={handleTalkToHuman}
            className="text-sjsu-blue hover:underline focus-ring"
          >
            Talk to a human advisor
          </button>
        </p>
      </div>
    </div>
  );
}
