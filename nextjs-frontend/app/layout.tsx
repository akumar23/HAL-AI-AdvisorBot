import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'HAL - CMPE/SE Advisor',
  description: 'HAL - AI-powered academic advisor for SJSU CMPE and SE students',
  viewport: 'width=device-width, initial-scale=1.0',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
