'use client';

import { useState, useEffect } from 'react';
import {
  getAnalyticsOverview,
  getDailyUsage,
  getFeedbackBreakdown,
  getPopularTopics,
  getCourseQueries,
  getFeedbackAnalysis,
} from '@/lib/adminApi';
import type {
  AdminOverviewStats,
  DailyUsage,
  FeedbackBreakdown,
  PopularTopic,
  CourseQuery,
  FeedbackInsight,
} from '@/types';

function StatCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</h3>
      <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
      {subtitle && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
    </div>
  );
}

function UsageChart({ data }: { data: DailyUsage[] }) {
  if (data.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No usage data available</p>;
  }

  const maxMessages = Math.max(...data.map(d => d.messages), 1);
  
  return (
    <div className="space-y-2">
      <div className="flex items-end space-x-1 h-40">
        {data.slice(-14).map((day, i) => (
          <div key={i} className="flex-1 flex flex-col items-center">
            <div
              className="w-full bg-blue-500 rounded-t"
              style={{ height: `${(day.messages / maxMessages) * 100}%`, minHeight: '4px' }}
              title={`${day.date}: ${day.messages} messages, ${day.sessions} sessions`}
            />
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{data.slice(-14)[0]?.date}</span>
        <span>{data.slice(-14)[data.slice(-14).length - 1]?.date}</span>
      </div>
    </div>
  );
}

function TopicsList({ topics }: { topics: PopularTopic[] }) {
  if (topics.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No topic data available</p>;
  }

  const maxCount = Math.max(...topics.map(t => t.count), 1);

  return (
    <div className="space-y-3">
      {topics.map((topic, i) => (
        <div key={i}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700 dark:text-gray-300">{topic.topic}</span>
            <span className="text-gray-500 dark:text-gray-400">{topic.count} ({topic.percentage}%)</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${(topic.count / maxCount) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function CoursesList({ courses }: { courses: CourseQuery[] }) {
  if (courses.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No course query data available</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {courses.slice(0, 10).map((course, i) => (
        <span
          key={i}
          className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
        >
          {course.code} ({course.count})
        </span>
      ))}
    </div>
  );
}

function FeedbackSection({ feedback }: { feedback: FeedbackBreakdown }) {
  const total = feedback.positive + feedback.negative;
  const positivePercent = total > 0 ? Math.round((feedback.positive / total) * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-green-600 dark:text-green-400">Positive</span>
            <span>{feedback.positive}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className="bg-green-500 h-3 rounded-full"
              style={{ width: `${positivePercent}%` }}
            />
          </div>
        </div>
        <div className="flex-1">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-red-600 dark:text-red-400">Negative</span>
            <span>{feedback.negative}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className="bg-red-500 h-3 rounded-full"
              style={{ width: `${100 - positivePercent}%` }}
            />
          </div>
        </div>
      </div>
      
      {feedback.recent_issues.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Issues</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {feedback.recent_issues.map((issue, i) => (
              <div key={i} className="p-2 bg-red-50 dark:bg-red-900/20 rounded text-sm">
                <p className="text-gray-600 dark:text-gray-400 text-xs">{issue.date}</p>
                <p className="text-gray-800 dark:text-gray-200">{issue.comment}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AIInsightsSection({ insight }: { insight: FeedbackInsight | null }) {
  if (!insight) {
    return <p className="text-gray-500 dark:text-gray-400">Loading AI analysis...</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Summary</h4>
        <p className="text-gray-600 dark:text-gray-400 text-sm">{insight.summary}</p>
      </div>
      
      {insight.themes.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Key Themes</h4>
          <div className="flex flex-wrap gap-2">
            {insight.themes.map((theme, i) => (
              <span key={i} className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-xs">
                {theme}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {insight.recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recommendations</h4>
          <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {insight.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      
      <p className="text-xs text-gray-400">
        Analyzed {insight.analyzed_count} feedback items on {insight.analysis_date}
      </p>
    </div>
  );
}

export default function AdminDashboard() {
  const [days, setDays] = useState(30);
  const [overview, setOverview] = useState<AdminOverviewStats | null>(null);
  const [dailyUsage, setDailyUsage] = useState<DailyUsage[]>([]);
  const [feedback, setFeedback] = useState<FeedbackBreakdown | null>(null);
  const [topics, setTopics] = useState<PopularTopic[]>([]);
  const [courses, setCourses] = useState<CourseQuery[]>([]);
  const [aiInsight, setAiInsight] = useState<FeedbackInsight | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      setError(null);
      
      try {
        const [overviewData, usageData, feedbackData, topicsData, coursesData] = await Promise.all([
          getAnalyticsOverview(days),
          getDailyUsage(days),
          getFeedbackBreakdown(days),
          getPopularTopics(days),
          getCourseQueries(days),
        ]);

        setOverview(overviewData);
        setDailyUsage(usageData);
        setFeedback(feedbackData);
        setTopics(topicsData);
        setCourses(coursesData);

        // Load AI insights separately (can be slow)
        try {
          const insightData = await getFeedbackAnalysis(days);
          setAiInsight(insightData);
        } catch {
          console.error('Failed to load AI insights');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics');
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, [days]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-gray-400">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-md">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Overview Stats */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Sessions" value={overview.total_sessions} />
          <StatCard title="User Questions" value={overview.user_messages} />
          <StatCard 
            title="Satisfaction Rate" 
            value={`${overview.satisfaction_rate}%`}
            subtitle={`${overview.positive_feedback} positive / ${overview.total_feedback} total`}
          />
          <StatCard 
            title="Avg Messages/Session" 
            value={overview.avg_messages_per_session}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Usage Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Daily Usage</h2>
          <UsageChart data={dailyUsage} />
        </div>

        {/* Feedback Breakdown */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Feedback</h2>
          {feedback && <FeedbackSection feedback={feedback} />}
        </div>

        {/* Popular Topics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Popular Topics</h2>
          <TopicsList topics={topics} />
        </div>

        {/* Top Courses */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Most Queried Courses</h2>
          <CoursesList courses={courses} />
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">AI-Powered Insights</h2>
        <AIInsightsSection insight={aiInsight} />
      </div>
    </div>
  );
}
