'use client';

import React, { useState, useEffect } from 'react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (comment: string) => void;
}

export function FeedbackModal({ isOpen, onClose, onSubmit }: FeedbackModalProps) {
  const [comment, setComment] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setComment('');
    }
  }, [isOpen]);

  const handleSubmit = () => {
    onSubmit(comment);
    setComment('');
  };

  const handleSkip = () => {
    onClose();
    setComment('');
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={handleSkip}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-6 shadow-xl"
        role="dialog"
        aria-labelledby="feedbackTitle"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 id="feedbackTitle" className="text-lg font-bold text-gray-900 dark:text-white mb-2">
          Help us improve
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          What went wrong with this response? (Optional)
        </p>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-sjsu-blue focus:outline-none"
          rows={3}
          placeholder="The information was incorrect, unclear, etc..."
        />
        <div className="mt-4 flex gap-2 justify-end">
          <button
            onClick={handleSkip}
            className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Skip
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-sjsu-blue text-white rounded-lg hover:bg-blue-700"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
