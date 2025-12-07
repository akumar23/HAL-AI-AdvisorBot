'use client';

import React, { useState } from 'react';

interface FeedbackButtonsProps {
  messageId: number;
  onFeedback: (rating: 1 | 2) => void;
}

export function FeedbackButtons({ messageId, onFeedback }: FeedbackButtonsProps) {
  const [selectedRating, setSelectedRating] = useState<1 | 2 | null>(null);
  const [showThanks, setShowThanks] = useState(false);

  const handleFeedback = (rating: 1 | 2) => {
    setSelectedRating(rating);
    onFeedback(rating);

    if (rating === 1) {
      setShowThanks(true);
    }
  };

  return (
    <div id={`feedback-${messageId}`} className="flex items-center gap-1 ml-auto">
      <button
        onClick={() => handleFeedback(2)}
        data-rating="2"
        className={`feedback-btn p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors focus-ring ${
          selectedRating === 2 ? 'text-sjsu-blue dark:text-sjsu-gold' : ''
        }`}
        title="Good response"
        aria-label="Mark as helpful"
        disabled={selectedRating !== null}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
          />
        </svg>
      </button>
      <button
        onClick={() => handleFeedback(1)}
        data-rating="1"
        className={`feedback-btn p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors focus-ring ${
          selectedRating === 1 ? 'text-sjsu-blue dark:text-sjsu-gold' : ''
        }`}
        title="Bad response"
        aria-label="Mark as not helpful"
        disabled={selectedRating !== null}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
          />
        </svg>
      </button>
      {showThanks && (
        <span className="text-xs text-gray-500 ml-2">Thanks for helping us improve!</span>
      )}
    </div>
  );
}
