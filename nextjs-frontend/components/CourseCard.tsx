'use client';

import React from 'react';
import type { CourseCard as CourseCardType } from '@/types';

interface CourseCardProps {
  course: CourseCardType;
}

export function CourseCard({ course }: CourseCardProps) {
  // Build prerequisites section
  let prereqSection: React.ReactNode = null;

  if (course.prerequisites || course.prerequisites_cmpe || course.prerequisites_se) {
    const hasDifferentPrereqs =
      course.prerequisites_cmpe &&
      course.prerequisites_se &&
      course.prerequisites_cmpe !== course.prerequisites_se;

    prereqSection = (
      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Prerequisites:</p>
        {hasDifferentPrereqs ? (
          <>
            <p className="text-xs text-gray-600 dark:text-gray-300">
              <strong>CMPE:</strong> {course.prerequisites_cmpe}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-300">
              <strong>SE:</strong> {course.prerequisites_se}
            </p>
          </>
        ) : (
          <p className="text-xs text-gray-600 dark:text-gray-300">
            {course.prerequisites || course.prerequisites_cmpe || course.prerequisites_se || 'None'}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="course-card bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-sjsu-blue to-blue-700 text-white rounded-xl flex items-center justify-center font-bold text-sm">
          {course.code.split(' ')[0]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-bold text-gray-900 dark:text-white">{course.code}</h4>
            {course.units && (
              <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
                {course.units} units
              </span>
            )}
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">{course.name}</p>
          {course.description && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
              {course.description}
            </p>
          )}
          {prereqSection}
        </div>
      </div>
    </div>
  );
}
