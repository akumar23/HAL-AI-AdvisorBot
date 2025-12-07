# HAL AI Advisor - Next.js Frontend

Modern Next.js 14+ frontend for the HAL AI Advisor chatbot, providing academic advising assistance to SJSU CMPE and SE students.

## Features

- **Next.js 14+ App Router** - Modern React framework with server components
- **TypeScript** - Full type safety across the application
- **Tailwind CSS** - Utility-first styling with custom SJSU branding
- **Dark Mode** - System preference detection with manual toggle
- **Responsive Design** - Mobile-first design that works on all devices
- **Accessibility** - ARIA labels, keyboard shortcuts, and screen reader support
- **Real-time Chat** - Smooth chat interface with typing indicators
- **Course Cards** - Rich course information display
- **Quick Replies** - Contextual suggestions based on conversation
- **Feedback System** - Thumbs up/down with optional comments
- **Human Handoff** - Escalation to human advisors when needed

## Tech Stack

- **Framework**: Next.js 14.2+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3.4+
- **Backend API**: Flask (separate service at http://127.0.0.1:5000)

## Architecture

### App Router Structure

```
nextjs-frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Home page (chat interface)
│   └── globals.css         # Global styles + Tailwind
├── components/
│   ├── ChatInterface.tsx   # Main chat orchestration
│   ├── ChatMessage.tsx     # Individual message rendering
│   ├── ChatInput.tsx       # Message input with send button
│   ├── Header.tsx          # App header with controls
│   ├── CourseCard.tsx      # Course information card
│   ├── EscalationCard.tsx  # Human handoff card
│   ├── FeedbackButtons.tsx # Thumbs up/down
│   ├── FeedbackModal.tsx   # Feedback comment modal
│   ├── QuickReplies.tsx    # Contextual suggestions
│   └── TypingIndicator.tsx # Loading animation
├── hooks/
│   ├── useChat.ts          # Chat state management
│   └── useDarkMode.ts      # Dark mode toggle
├── lib/
│   ├── api.ts              # Flask API client
│   └── utils.ts            # Utility functions
├── types/
│   └── index.ts            # TypeScript interfaces
└── public/                 # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Flask backend running at http://127.0.0.1:5000

### Installation

1. Install dependencies:

```bash
cd nextjs-frontend
npm install
```

2. Create `.env.local`:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` if your Flask backend runs on a different URL:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup

Make sure the Flask backend is running:

```bash
# In the project root
python3 run.py
```

The Flask app should be accessible at http://127.0.0.1:5000.

## Development

### Commands

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Key Features Implementation

#### Chat State Management

The `useChat` hook manages all chat state:
- Message history
- Loading states
- Last query/response for context
- Feedback metadata

#### Dark Mode

The `useDarkMode` hook:
- Checks localStorage preference
- Falls back to system preference
- Syncs with `<html>` class for Tailwind

#### API Integration

The `lib/api.ts` module:
- Centralizes all Flask API calls
- Handles credentials (cookies for session)
- Type-safe responses
- Error handling

#### TypeScript Types

All API responses are fully typed in `types/index.ts`:
- `Message` - Chat message structure
- `ChatResponse` - API response
- `CourseCard` - Course information
- `FeedbackPayload` - Feedback data

## API Endpoints

The frontend calls these Flask backend endpoints:

- `POST /api/chat` - Send message, get response
- `POST /api/quick-replies` - Get contextual suggestions
- `POST /api/feedback` - Submit feedback
- `POST /api/clear-history` - Clear chat history
- `GET /api/status` - Get provider/model info

## Styling

### Tailwind Configuration

Custom SJSU colors defined in `tailwind.config.ts`:
- `sjsu-blue`: #0055A2
- `sjsu-gold`: #E5A823

### Custom CSS

Additional styles in `app/globals.css`:
- Custom scrollbars
- Message animations
- Typing indicator animation
- Quick reply scroll behavior

## Accessibility

- Skip to main content link
- ARIA labels on all interactive elements
- Keyboard shortcuts (Alt+M to focus input)
- Focus indicators
- Screen reader announcements for messages

## Performance Optimization

- Server Components by default
- Client Components only where needed (`'use client'`)
- Code splitting via Next.js
- Optimized Tailwind CSS output
- Lazy loading for heavy components

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL`: Your production Flask API URL
4. Deploy

### Self-Hosting

1. Build the app:

```bash
npm run build
```

2. Start the production server:

```bash
npm start
```

3. Or use a process manager like PM2:

```bash
npm install -g pm2
pm2 start npm --name "hal-frontend" -- start
```

### Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

Build and run:

```bash
docker build -t hal-nextjs .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api hal-nextjs
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Flask backend URL (required)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

1. Follow the existing code structure
2. Use TypeScript strict mode
3. Follow Tailwind utility-first approach
4. Add ARIA labels for accessibility
5. Test on mobile devices
6. Run `npm run lint` before committing

## License

Same as the parent HAL AI AdvisorBot project.
