'use client';

import { useAdminAuth } from '@/hooks/useAdminAuth';
import { useState } from 'react';

function AdminLogin({ onLogin }: { onLogin: (username: string, password: string) => Promise<boolean> }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const success = await onLogin(username, password);
    if (!success) {
      setError('Invalid credentials');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8 p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">
            Admin Access
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Restricted area - Authorized personnel only
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}

function AdminNavbar({ user, onLogout }: { user: string | null; onLogout: () => void }) {
  return (
    <nav className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <span className="text-xl font-bold">HAL Admin</span>
            <div className="hidden md:flex space-x-4">
              <a href="/control-panel-x7k9m2" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Dashboard
              </a>
              <a href="/control-panel-x7k9m2/courses" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Courses
              </a>
              <a href="/control-panel-x7k9m2/advisors" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Advisors
              </a>
              <a href="/control-panel-x7k9m2/policies" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Policies
              </a>
              <a href="/control-panel-x7k9m2/deadlines" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Deadlines
              </a>
              <a href="/control-panel-x7k9m2/feedback" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Feedback
              </a>
              <a href="/control-panel-x7k9m2/conversations" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Conversations
              </a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-300">Logged in as: {user}</span>
            <button
              onClick={onLogout}
              className="px-3 py-2 rounded-md text-sm font-medium bg-red-600 hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading, user, login, logout } = useAdminAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-gray-600 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLogin onLogin={login} />;
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <AdminNavbar user={user} onLogout={logout} />
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
