'use client';

import { useState, useEffect } from 'react';
import { getAdvisors, createAdvisor, updateAdvisor, deleteAdvisor } from '@/lib/adminApi';
import type { AdminAdvisor } from '@/types';

function AdvisorModal({
  advisor,
  onSave,
  onClose,
}: {
  advisor: AdminAdvisor | null;
  onSave: (data: Partial<AdminAdvisor>) => Promise<void>;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState<Partial<AdminAdvisor>>(
    advisor || { name: '', last_name_start: '', last_name_end: '', department: 'CMPE/SE' }
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
            {advisor ? 'Edit Advisor' : 'Add Advisor'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Last Name Start *
                </label>
                <input
                  type="text"
                  maxLength={1}
                  value={formData.last_name_start || ''}
                  onChange={(e) => setFormData({ ...formData, last_name_start: e.target.value.toUpperCase() })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="A"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Last Name End *
                </label>
                <input
                  type="text"
                  maxLength={1}
                  value={formData.last_name_end || ''}
                  onChange={(e) => setFormData({ ...formData, last_name_end: e.target.value.toUpperCase() })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="M"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Department
              </label>
              <input
                type="text"
                value={formData.department || ''}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Booking URL
              </label>
              <input
                type="url"
                value={formData.booking_url || ''}
                onChange={(e) => setFormData({ ...formData, booking_url: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">
                Cancel
              </button>
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

export default function AdvisorsPage() {
  const [advisors, setAdvisors] = useState<AdminAdvisor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingAdvisor, setEditingAdvisor] = useState<AdminAdvisor | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const fetchAdvisors = async () => {
    setIsLoading(true);
    try {
      const result = await getAdvisors();
      setAdvisors(result.items);
    } catch (error) {
      console.error('Failed to fetch advisors:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchAdvisors(); }, []);

  const handleCreate = async (data: Partial<AdminAdvisor>) => {
    await createAdvisor(data);
    fetchAdvisors();
  };

  const handleUpdate = async (data: Partial<AdminAdvisor>) => {
    if (editingAdvisor) {
      await updateAdvisor(editingAdvisor.id, data);
      fetchAdvisors();
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this advisor?')) {
      await deleteAdvisor(id);
      fetchAdvisors();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Advisors</h1>
        <button onClick={() => setIsCreating(true)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Add Advisor
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Last Names</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Department</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {advisors.map((advisor) => (
                <tr key={advisor.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{advisor.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{advisor.email}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{advisor.last_name_start} - {advisor.last_name_end}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{advisor.department}</td>
                  <td className="px-4 py-3 text-right space-x-2">
                    <button onClick={() => setEditingAdvisor(advisor)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 text-sm">Edit</button>
                    <button onClick={() => handleDelete(advisor.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 text-sm">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {(isCreating || editingAdvisor) && (
        <AdvisorModal advisor={editingAdvisor} onSave={editingAdvisor ? handleUpdate : handleCreate} onClose={() => { setEditingAdvisor(null); setIsCreating(false); }} />
      )}
    </div>
  );
}
