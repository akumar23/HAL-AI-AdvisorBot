'use client';

import { useState, useEffect } from 'react';
import { getPolicies, createPolicy, updatePolicy, deletePolicy } from '@/lib/adminApi';
import type { AdminPolicy } from '@/types';

function PolicyModal({
  policy,
  categories,
  onSave,
  onClose,
}: {
  policy: AdminPolicy | null;
  categories: string[];
  onSave: (data: Partial<AdminPolicy>) => Promise<void>;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState<Partial<AdminPolicy>>(
    policy || { category: categories[0] || 'general', question: '', answer: '' }
  );
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Save error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            {policy ? 'Edit Policy' : 'Add Policy'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category *</label>
              <select
                value={formData.category || ''}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Question *</label>
              <textarea
                value={formData.question || ''}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                required
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Answer *</label>
              <textarea
                value={formData.answer || ''}
                onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Keywords (comma-separated)</label>
              <input
                type="text"
                value={formData.keywords || ''}
                onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="enrollment, deadline, add class"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">URL</label>
              <input
                type="url"
                value={formData.url || ''}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">Cancel</button>
              <button type="submit" disabled={isSaving} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<AdminPolicy[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [editingPolicy, setEditingPolicy] = useState<AdminPolicy | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const fetchPolicies = async () => {
    setIsLoading(true);
    try {
      const result = await getPolicies({ category: selectedCategory, search });
      setPolicies(result.items);
      setCategories(result.categories);
    } catch (error) {
      console.error('Failed to fetch policies:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchPolicies(); }, [selectedCategory, search]);

  const handleCreate = async (data: Partial<AdminPolicy>) => { await createPolicy(data); fetchPolicies(); };
  const handleUpdate = async (data: Partial<AdminPolicy>) => { if (editingPolicy) { await updatePolicy(editingPolicy.id, data); fetchPolicies(); } };
  const handleDelete = async (id: number) => { if (confirm('Delete this policy?')) { await deletePolicy(id); fetchPolicies(); } };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Policies</h1>
        <button onClick={() => setIsCreating(true)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Add Policy</button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex gap-4">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {policies.map((policy) => (
              <div key={policy.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <span className="inline-block px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded mb-2">{policy.category}</span>
                    <h3 className="font-medium text-gray-900 dark:text-white">{policy.question}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">{policy.answer}</p>
                  </div>
                  <div className="ml-4 space-x-2">
                    <button onClick={() => setEditingPolicy(policy)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 text-sm">Edit</button>
                    <button onClick={() => handleDelete(policy.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 text-sm">Delete</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {(isCreating || editingPolicy) && (
        <PolicyModal policy={editingPolicy} categories={categories} onSave={editingPolicy ? handleUpdate : handleCreate} onClose={() => { setEditingPolicy(null); setIsCreating(false); }} />
      )}
    </div>
  );
}
