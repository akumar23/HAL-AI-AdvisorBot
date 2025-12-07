'use client';

import { useState, useEffect } from 'react';
import { getFeedback, deleteFeedback, getFeedbackAnalysis, getTopicSuggestions } from '@/lib/adminApi';
import type { AdminFeedback, FeedbackInsight } from '@/types';

function FeedbackDetailModal({ feedback, onClose }: { feedback: AdminFeedback; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto m-4">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Feedback Details</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <span className="text-2xl">&times;</span>
            </button>
          </div>
          <div className="space-y-4">
            <div>
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                feedback.rating === 2 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {feedback.rating === 2 ? 'Positive' : 'Negative'}
              </span>
              <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">{feedback.created_at}</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">User Query</h3>
              <p className="text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded">{feedback.user_query}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bot Response</h3>
              <p className="text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded">{feedback.bot_response}</p>
            </div>
            {feedback.comment && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">User Comment</h3>
                <p className="text-gray-600 dark:text-gray-400 bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded">{feedback.comment}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AIAnalysisPanel({ insight, onGetSuggestions }: { insight: FeedbackInsight | null; onGetSuggestions: (topic: string) => void }) {
  const topics = ['prerequisites', 'enrollment', 'advisors', 'deadlines', 'graduation'];
  
  if (!insight) {
    return <div className="p-4 text-gray-500 dark:text-gray-400">Loading AI analysis...</div>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Analysis</h2>
      <p className="text-gray-600 dark:text-gray-400">{insight.summary}</p>
      
      {insight.themes.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Themes</h3>
          <div className="flex flex-wrap gap-2">
            {insight.themes.map((theme, i) => (
              <span key={i} className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-sm">{theme}</span>
            ))}
          </div>
        </div>
      )}
      
      {insight.recommendations.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recommendations</h3>
          <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {insight.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
          </ul>
        </div>
      )}
      
      <div>
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Get Topic Suggestions</h3>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <button
              key={topic}
              onClick={() => onGetSuggestions(topic)}
              className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm hover:bg-blue-200 dark:hover:bg-blue-800"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function FeedbackPage() {
  const [feedbackItems, setFeedbackItems] = useState<AdminFeedback[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [ratingFilter, setRatingFilter] = useState<number | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFeedback, setSelectedFeedback] = useState<AdminFeedback | null>(null);
  const [aiInsight, setAiInsight] = useState<FeedbackInsight | null>(null);
  const [suggestions, setSuggestions] = useState<{ topic: string; items: string[] } | null>(null);

  const fetchFeedback = async () => {
    setIsLoading(true);
    try {
      const result = await getFeedback({ page, per_page: 20, rating: ratingFilter });
      setFeedbackItems(result.items);
      setTotalPages(result.pages);
    } catch (error) {
      console.error('Failed to fetch feedback:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAIInsight = async () => {
    try {
      const insight = await getFeedbackAnalysis(30);
      setAiInsight(insight);
    } catch (error) {
      console.error('Failed to fetch AI insight:', error);
    }
  };

  useEffect(() => { fetchFeedback(); }, [page, ratingFilter]);
  useEffect(() => { fetchAIInsight(); }, []);

  const handleDelete = async (id: number) => {
    if (confirm('Delete this feedback?')) {
      await deleteFeedback(id);
      fetchFeedback();
    }
  };

  const handleGetSuggestions = async (topic: string) => {
    try {
      const result = await getTopicSuggestions(topic);
      setSuggestions({ topic: result.topic, items: result.suggestions });
    } catch (error) {
      console.error('Failed to get suggestions:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Feedback</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex gap-4">
              <select
                value={ratingFilter || ''}
                onChange={(e) => { setRatingFilter(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">All Ratings</option>
                <option value="2">Positive</option>
                <option value="1">Negative</option>
              </select>
            </div>

            {isLoading ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
            ) : (
              <>
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {feedbackItems.map((fb) => (
                    <div key={fb.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer" onClick={() => setSelectedFeedback(fb)}>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`inline-block w-3 h-3 rounded-full ${fb.rating === 2 ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-xs text-gray-500 dark:text-gray-400">{fb.created_at}</span>
                          </div>
                          <p className="text-sm text-gray-800 dark:text-gray-200 line-clamp-1">{fb.user_query}</p>
                          {fb.comment && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">&quot;{fb.comment}&quot;</p>}
                        </div>
                        <button onClick={(e) => { e.stopPropagation(); handleDelete(fb.id); }} className="text-red-600 hover:text-red-800 dark:text-red-400 text-sm ml-2">
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-center space-x-2">
                    <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-50 text-gray-700 dark:text-gray-300">Previous</button>
                    <span className="px-3 py-1 text-gray-700 dark:text-gray-300">Page {page} of {totalPages}</span>
                    <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-3 py-1 border rounded disabled:opacity-50 text-gray-700 dark:text-gray-300">Next</button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <AIAnalysisPanel insight={aiInsight} onGetSuggestions={handleGetSuggestions} />
          
          {suggestions && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Suggestions for: {suggestions.topic}</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                {suggestions.items.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>

      {selectedFeedback && <FeedbackDetailModal feedback={selectedFeedback} onClose={() => setSelectedFeedback(null)} />}
    </div>
  );
}
