'use client';

import React from 'react';
import { ADVISOR_URL, ESCALATION_REASONS } from '@/lib/utils';

interface EscalationCardProps {
  reason?: string;
}

export function EscalationCard({ reason }: EscalationCardProps) {
  const reasonText = reason ? ESCALATION_REASONS[reason] : 'I recommend verifying this with an advisor.';

  return (
    <div className="mt-4 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border border-orange-200 dark:border-orange-800 rounded-xl p-4">
      <h4 className="font-semibold text-orange-800 dark:text-orange-300 flex items-center gap-2">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
          />
        </svg>
        I recommend speaking with an advisor
      </h4>
      <p className="mt-2 text-sm text-orange-700 dark:text-orange-400">{reasonText}</p>
      <a
        href={ADVISOR_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm font-medium transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        Book Appointment
      </a>
    </div>
  );
}
