export function formatResponse(text: string): string {
  // Convert URLs to links
  let formatted = text.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-sjsu-blue hover:underline">$1</a>'
  );

  // Convert newlines to <br>
  formatted = formatted.replace(/\n/g, '<br>');

  return formatted;
}

export function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export function scrollToBottom(element: HTMLElement | null) {
  if (element) {
    element.scrollTop = element.scrollHeight;
  }
}

export function getConfidenceBadgeClass(
  confidence: number,
  level?: 'high' | 'medium' | 'low'
): { className: string; text: string } {
  const actualLevel = level || (confidence >= 0.8 ? 'high' : confidence >= 0.5 ? 'medium' : 'low');

  const levelClass =
    actualLevel === 'high'
      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      : actualLevel === 'medium'
      ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';

  const levelText = actualLevel.charAt(0).toUpperCase() + actualLevel.slice(1);

  return {
    className: levelClass,
    text: levelText,
  };
}

export const ADVISOR_URL = 'https://sjsu.campus.eab.com/student/appointments/new';

export const ESCALATION_REASONS: Record<string, string> = {
  low_confidence: "I'm not confident enough to answer this accurately.",
  no_relevant_documents: "I don't have this information in my knowledge base.",
  personal_situation: "This requires personalized attention.",
  appeals_or_exceptions: "Appeals and exceptions need advisor assistance.",
  academic_standing: "Academic standing should be discussed with an advisor.",
  out_of_scope: "This is outside my expertise.",
  user_requested_human: "You asked to speak with a human advisor.",
};
