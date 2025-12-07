'use client';

import React from 'react';
import type { Message } from '@/types';
import { CourseCard } from './CourseCard';
import { EscalationCard } from './EscalationCard';
import { FeedbackButtons } from './FeedbackButtons';
import { getConfidenceBadgeClass, formatResponse } from '@/lib/utils';

interface ChatMessageProps {
  message: Message;
  onFeedback: (rating: 1 | 2) => void;
}

export function ChatMessage({ message, onFeedback }: ChatMessageProps) {
  if (message.role === 'user') {
    return (
      <div className="message-animate flex justify-end">
        <div className="bg-sjsu-blue text-white rounded-2xl rounded-tr-none p-4 max-w-[85%]">
          <p>{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  const confidenceBadge = message.confidence !== undefined
    ? getConfidenceBadgeClass(message.confidence, message.confidenceLevel)
    : null;

  return (
    <div className="message-animate">
      <div className="flex gap-3">
        <div className="flex-shrink-0 w-8 h-8 bg-sjsu-blue rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-bold">H</span>
        </div>
        <div className="flex-1 max-w-[85%]">
          <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none p-4">
            <p
              className="text-gray-800 dark:text-gray-200"
              dangerouslySetInnerHTML={{ __html: formatResponse(message.content) }}
            />
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            {confidenceBadge && (
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${confidenceBadge.className}`}
              >
                {confidenceBadge.text}
              </span>
            )}
            {message.intent && message.intent !== 'general_question' && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {message.intent.replace(/_/g, ' ')}
              </span>
            )}

            <FeedbackButtons messageId={message.id} onFeedback={onFeedback} />
          </div>

          {message.resolvedQuery && (
            <p className="mt-2 text-xs text-gray-400 italic">
              Understood as: &quot;{message.resolvedQuery}&quot;
            </p>
          )}

          {message.courseCards && message.courseCards.length > 0 && (
            <div className="mt-4 space-y-3">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Related Courses
              </p>
              <div
                className={`grid gap-3 ${
                  message.courseCards.length > 1 ? 'md:grid-cols-2' : ''
                }`}
              >
                {message.courseCards.map((course, index) => (
                  <CourseCard key={index} course={course} />
                ))}
              </div>
            </div>
          )}

          {message.escalate && message.escalationReason && (
            <EscalationCard reason={message.escalationReason} />
          )}
        </div>
      </div>
    </div>
  );
}
