'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { useDarkMode } from '@/hooks/useDarkMode';
import { Header } from './Header';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { QuickReplies } from './QuickReplies';
import { TypingIndicator } from './TypingIndicator';
import { FeedbackModal } from './FeedbackModal';
import { getQuickReplies, submitFeedback, clearHistory, getStatus } from '@/lib/api';
import { scrollToBottom } from '@/lib/utils';

export function ChatInterface() {
  const {
    messages,
    isLoading,
    sendUserMessage,
    clearMessages,
    lastQuery,
    lastResponse,
    lastIntent,
    lastConfidence,
    lastEscalated,
    lastResponseTime,
  } = useChat();

  const { isDark, toggleDarkMode } = useDarkMode();
  const chatboxRef = useRef<HTMLDivElement>(null);

  const [quickReplySuggestions, setQuickReplySuggestions] = useState<string[]>([
    'What are the prerequisites for CS 149?',
    'How do I add a class?',
    'Who is my advisor?',
    'What is the max units I can take?',
  ]);

  const [providerInfo, setProviderInfo] = useState('');
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [pendingFeedback, setPendingFeedback] = useState<{
    rating: 1 | 2;
    messageId: number;
  } | null>(null);

  // Fetch provider info on mount
  useEffect(() => {
    getStatus()
      .then((data) => {
        setProviderInfo(`Powered by ${data.provider} (${data.model})`);
      })
      .catch((error) => {
        console.error('Failed to get status:', error);
      });
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom(chatboxRef.current);
  }, [messages, isLoading]);

  // Load quick replies when conversation context changes
  useEffect(() => {
    if (lastResponse) {
      getQuickReplies(lastResponse, lastQuery, lastIntent)
        .then((data) => {
          if (data.suggestions && data.suggestions.length > 0) {
            setQuickReplySuggestions(data.suggestions);
          }
        })
        .catch((error) => {
          console.error('Failed to load quick replies:', error);
        });
    }
  }, [lastResponse, lastQuery, lastIntent]);

  const handleClearChat = async () => {
    try {
      await clearHistory();
      clearMessages();
      // Reset to default quick replies
      setQuickReplySuggestions([
        'What are the prerequisites for CS 149?',
        'How do I add a class?',
        'Who is my advisor?',
        'What is the max units I can take?',
      ]);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const handleFeedback = (messageId: number, rating: 1 | 2) => {
    if (rating === 1) {
      // Show modal for negative feedback
      setPendingFeedback({ rating, messageId });
      setIsFeedbackModalOpen(true);
    } else {
      // Submit positive feedback immediately
      submitFeedback({
        rating,
        query: lastQuery,
        response: lastResponse,
        intent: lastIntent,
        confidence: lastConfidence,
        escalated_to_human: lastEscalated,
        response_time_ms: lastResponseTime,
      }).catch((error) => {
        console.error('Failed to submit feedback:', error);
      });
    }
  };

  const handleFeedbackModalSubmit = (comment: string) => {
    if (pendingFeedback) {
      submitFeedback({
        rating: pendingFeedback.rating,
        query: lastQuery,
        response: lastResponse,
        comment: comment || undefined,
        intent: lastIntent,
        confidence: lastConfidence,
        escalated_to_human: lastEscalated,
        response_time_ms: lastResponseTime,
      }).catch((error) => {
        console.error('Failed to submit feedback:', error);
      });
    }
    setIsFeedbackModalOpen(false);
    setPendingFeedback(null);
  };

  const handleFeedbackModalClose = () => {
    if (pendingFeedback) {
      // Submit without comment
      submitFeedback({
        rating: pendingFeedback.rating,
        query: lastQuery,
        response: lastResponse,
        intent: lastIntent,
        confidence: lastConfidence,
        escalated_to_human: lastEscalated,
        response_time_ms: lastResponseTime,
      }).catch((error) => {
        console.error('Failed to submit feedback:', error);
      });
    }
    setIsFeedbackModalOpen(false);
    setPendingFeedback(null);
  };

  return (
    <>
      {/* Skip to main content for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-sjsu-blue text-white px-4 py-2 rounded z-50"
      >
        Skip to main content
      </a>

      <Header
        isDark={isDark}
        onToggleDarkMode={toggleDarkMode}
        onClearChat={handleClearChat}
      />

      <main id="main-content" className="max-w-4xl mx-auto px-4 pb-32 md:pb-24" role="main">
        {/* Provider info */}
        {providerInfo && (
          <div className="text-center text-xs text-gray-400 dark:text-gray-500 py-2">
            {providerInfo}
          </div>
        )}

        {/* Chat container */}
        <div
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden"
          role="region"
          aria-label="Chat interface"
        >
          {/* Chat messages */}
          <div
            id="chatbox"
            ref={chatboxRef}
            className="h-[60vh] md:h-[65vh] overflow-y-auto p-4 space-y-4"
            role="log"
            aria-live="polite"
            aria-atomic="false"
            tabIndex={0}
          >
            {/* Welcome message */}
            {messages.length === 0 && (
              <div className="message-animate">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-sjsu-blue rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">H</span>
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none p-4 max-w-[85%]">
                      <p className="text-gray-800 dark:text-gray-200">
                        Hi! I&apos;m HAL, your CMPE/SE advising assistant. I can help you with:
                      </p>
                      <ul className="mt-2 text-gray-700 dark:text-gray-300 text-sm space-y-1">
                        <li>• Course prerequisites</li>
                        <li>• Add/drop procedures</li>
                        <li>• Finding your advisor</li>
                        <li>• GPA and graduation requirements</li>
                      </ul>
                      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                        If I can&apos;t help with something, I&apos;ll connect you with a human
                        advisor.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Chat messages */}
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onFeedback={(rating) => handleFeedback(message.id, rating)}
              />
            ))}
          </div>

          {/* Quick replies */}
          <QuickReplies suggestions={quickReplySuggestions} onSend={sendUserMessage} />

          {/* Typing indicator */}
          {isLoading && <TypingIndicator />}
        </div>
      </main>

      {/* Fixed input at bottom */}
      <ChatInput onSend={sendUserMessage} disabled={isLoading} />

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={isFeedbackModalOpen}
        onClose={handleFeedbackModalClose}
        onSubmit={handleFeedbackModalSubmit}
      />
    </>
  );
}
