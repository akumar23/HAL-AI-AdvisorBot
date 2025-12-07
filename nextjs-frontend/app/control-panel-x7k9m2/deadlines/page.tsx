'use client';

import { useState, useEffect } from 'react';
import { getDeadlines, createDeadline, updateDeadline, deleteDeadline } from '@/lib/adminApi';
import type { AdminDeadline } from '@/types';

function DeadlineModal({
  deadline,
  deadlineTypes,
  semesters,
  onSave,
  onClose,
}: {
  deadline: AdminDeadline | null;
  deadlineTypes: string[];
  semesters: string[];
  onSave: (data: Partial<AdminDeadline>) => Promise<void>;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState<Partial<AdminDeadline>>(
    deadline || { semester: '', deadline_type: deadlineTypes[0] || '', date: '' }
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full m-4">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            {deadline ? 'Edit Deadline' : 'Add Deadline'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Semester *</label>
              <input
                type="text"
                value={formData.semester || ''}
                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                required
                list="semesters"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Spring 2025"
              />
              <datalist id="semesters">
                {semesters.map((s) => <option key={s} value={s} />)}
              </datalist>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deadline Type *</label>
              <select
                value={formData.deadline_type || ''}
                onChange={(e) => setFormData({ ...formData, deadline_type: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select type...</option>
                {deadlineTypes.map((type) => <option key={type} value={type}>{type.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date *</label>
              <input
                type="date"
                value={formData.date || ''}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
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

export default function DeadlinesPage() {
  const [deadlines, setDeadlines] = useState<AdminDeadline[]>([]);
  const [deadlineTypes, setDeadlineTypes] = useState<string[]>([]);
  const [semesters, setSemesters] = useState<string[]>([]);
  const [selectedSemester, setSelectedSemester] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [editingDeadline, setEditingDeadline] = useState<AdminDeadline | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const fetchDeadlines = async () => {
    setIsLoading(true);
    try {
      const result = await getDeadlines({ semester: selectedSemester });
      setDeadlines(result.items);
      setDeadlineTypes(result.deadline_types);
      setSemesters(result.semesters);
    } catch (error) {
      console.error('Failed to fetch deadlines:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchDeadlines(); }, [selectedSemester]);

  const handleCreate = async (data: Partial<AdminDeadline>) => { await createDeadline(data); fetchDeadlines(); };
  const handleUpdate = async (data: Partial<AdminDeadline>) => { if (editingDeadline) { await updateDeadline(editingDeadline.id, data); fetchDeadlines(); } };
  const handleDelete = async (id: number) => { if (confirm('Delete this deadline?')) { await deleteDeadline(id); fetchDeadlines(); } };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Deadlines</h1>
        <button onClick={() => setIsCreating(true)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Add Deadline</button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <select
            value={selectedSemester}
            onChange={(e) => setSelectedSemester(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Semesters</option>
            {semesters.map((sem) => <option key={sem} value={sem}>{sem}</option>)}
          </select>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Semester</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Description</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {deadlines.map((deadline) => (
                <tr key={deadline.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{deadline.semester}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{deadline.deadline_type.replace(/_/g, ' ')}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{formatDate(deadline.date)}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{deadline.description}</td>
                  <td className="px-4 py-3 text-right space-x-2">
                    <button onClick={() => setEditingDeadline(deadline)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 text-sm">Edit</button>
                    <button onClick={() => handleDelete(deadline.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 text-sm">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {(isCreating || editingDeadline) && (
        <DeadlineModal deadline={editingDeadline} deadlineTypes={deadlineTypes} semesters={semesters} onSave={editingDeadline ? handleUpdate : handleCreate} onClose={() => { setEditingDeadline(null); setIsCreating(false); }} />
      )}
    </div>
  );
}
