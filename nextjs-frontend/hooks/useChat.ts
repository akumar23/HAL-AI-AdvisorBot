'use client';

import { useState, useCallback } from 'react';
import type { Message } from '@/types';
import { sendMessage } from '@/lib/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastQuery, setLastQuery] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [lastIntent, setLastIntent] = useState('');
  const [lastConfidence, setLastConfidence] = useState(0);
  const [lastEscalated, setLastEscalated] = useState(false);
  const [lastResponseTime, setLastResponseTime] = useState(0);

  const sendUserMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const startTime = Date.now();
    setLastQuery(content);
    setIsLoading(true);

    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessage(content);
      const responseTime = Date.now() - startTime;

      setLastResponse(response.response);
      setLastConfidence(response.confidence || 0);
      setLastIntent(response.intent || '');
      setLastEscalated(response.escalate_to_human || false);
      setLastResponseTime(responseTime);

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        confidence: response.confidence,
        confidenceLevel: response.confidence_level,
        intent: response.intent,
        escalate: response.escalate || response.escalate_to_human,
        escalationReason: response.escalation_reason,
        courseCards: response.course_cards,
        resolvedQuery: response.resolved_query,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Add error message
      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or contact an advisor.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setLastQuery('');
    setLastResponse('');
    setLastIntent('');
    setLastConfidence(0);
    setLastEscalated(false);
    setLastResponseTime(0);
  }, []);

  return {
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
  };
}
