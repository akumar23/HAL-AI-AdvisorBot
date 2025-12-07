'use client';

import { useState, useEffect } from 'react';
import { getConversations, getConversation, deleteConversation } from '@/lib/adminApi';
import type { AdminConversation, AdminConversationDetail } from '@/types';

function ConversationDetailModal({ sessionId, onClose }: { sessionId: string; onClose: () => void }) {
  const [detail, setDetail] = useState<AdminConversationDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetch() {
      try {
        const data = await getConversation(sessionId);
        setDetail(data);
      } catch (error) {
        console.error('Failed to fetch conversation:', error);
      } finally {
        setIsLoading(false);
      }
    }
    fetch();
  }, [sessionId]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden m-4 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Session: {sessionId.slice(0, 8)}...</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <span className="text-2xl">&times;</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="text-center text-gray-500 dark:text-gray-400">Loading...</div>
          ) : detail ? (
            <div className="space-y-4">
              {detail.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'}`}>
                      {msg.created_at}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 dark:text-gray-400">No messages found</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<AdminConversation[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const result = await getConversations({ page, per_page: 20 });
      setConversations(result.items);
      setTotalPages(result.pages);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchConversations(); }, [page]);

  const handleDelete = async (sessionId: string) => {
    if (confirm('Delete this entire conversation?')) {
      await deleteConversation(sessionId);
      fetchConversations();
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Conversations</h1>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
        ) : (
          <>
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Session ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Messages</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Last Activity</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {conversations.map((conv) => (
                  <tr key={conv.session_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setSelectedSession(conv.session_id)}
                        className="text-sm font-mono text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        {conv.session_id.slice(0, 8)}...
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{conv.message_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{formatDate(conv.last_message)}</td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => setSelectedSession(conv.session_id)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 text-sm"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDelete(conv.session_id)}
                        className="text-red-600 hover:text-red-800 dark:text-red-400 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-center space-x-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 border rounded disabled:opacity-50 text-gray-700 dark:text-gray-300"
                >
                  Previous
                </button>
                <span className="px-3 py-1 text-gray-700 dark:text-gray-300">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 border rounded disabled:opacity-50 text-gray-700 dark:text-gray-300"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {selectedSession && (
        <ConversationDetailModal sessionId={selectedSession} onClose={() => setSelectedSession(null)} />
      )}
    </div>
  );
}
