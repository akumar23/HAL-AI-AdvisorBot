# Quick Start Guide - Next.js Frontend

Get the Next.js frontend running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- Flask backend configured with API keys
- Terminal/command line access

## Step 1: Start Flask Backend

The Next.js frontend needs the Flask backend running to function.

```bash
# In project root directory
python3 run.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

Verify it's working:
```bash
curl http://127.0.0.1:5000/api/status
```

Should return JSON with provider info.

## Step 2: Install Frontend Dependencies

```bash
cd nextjs-frontend
npm install
```

This will install:
- Next.js 14.2+
- React 18+
- TypeScript
- Tailwind CSS
- All other dependencies

Takes about 30-60 seconds.

## Step 3: Configure API URL

The `.env.local` file is already configured for local development:

```bash
# nextjs-frontend/.env.local (already created)
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

If your Flask backend runs on a different port, edit this file.

## Step 4: Start Development Server

```bash
npm run dev
```

You should see:
```
> hal-nextjs-frontend@1.0.0 dev
> next dev

  ▲ Next.js 14.2.0
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in 2.3s
```

## Step 5: Open in Browser

Navigate to **http://localhost:3000**

You should see the HAL chat interface.

## Verification Checklist

- [ ] Flask backend is running on port 5000
- [ ] Next.js frontend is running on port 3000
- [ ] Chat interface loads without errors
- [ ] You can see the welcome message from HAL
- [ ] Provider info shows at the top (e.g., "Powered by claude (claude-3-5-sonnet...)")
- [ ] Quick reply buttons are visible
- [ ] You can type a message and send it
- [ ] Bot responds to your message
- [ ] Dark mode toggle works (moon/sun icon in header)

## Common Issues

### "ECONNREFUSED" Error

**Problem**: Frontend can't connect to Flask backend.

**Solution**:
1. Make sure Flask is running: `python3 run.py`
2. Check it's on port 5000: `curl http://127.0.0.1:5000/api/status`
3. Verify `.env.local` has correct URL

### CORS Error in Browser Console

**Problem**: "No 'Access-Control-Allow-Origin' header"

**Solution**: Install flask-cors in the backend:
```bash
pip install flask-cors
```

See `FLASK_INTEGRATION.md` for detailed CORS setup.

### Port 3000 Already in Use

**Problem**: "Port 3000 is already in use"

**Solution**:
1. Kill the process: `lsof -ti:3000 | xargs kill -9`
2. Or use a different port: `PORT=3001 npm run dev`

### Dark Mode Not Persisting

**Problem**: Dark mode resets on refresh

**Solution**: Check browser localStorage is enabled (not in private/incognito mode)

## What to Try

1. **Send a message**: "What are the prerequisites for CS 149?"
2. **Test dark mode**: Click the moon icon in the header
3. **Try quick replies**: Click any suggestion button
4. **Give feedback**: Click thumbs up/down on a response
5. **Clear chat**: Click "Clear" button in header
6. **Mobile view**: Resize browser or open on phone

## Next Steps

Once you've verified everything works:

1. Read `README.md` for full feature documentation
2. Review `MIGRATION_GUIDE.md` to understand the architecture
3. Check `FLASK_INTEGRATION.md` for production deployment
4. Explore the components in `components/` directory
5. Customize styles in `app/globals.css` and `tailwind.config.ts`

## Development Workflow

### Hot Reload

Next.js has hot module replacement - edit any file and see changes instantly:

1. Edit `components/ChatMessage.tsx`
2. Save the file
3. Browser updates automatically (no refresh needed)

### TypeScript Checking

TypeScript will catch errors as you type:

```bash
# Check types manually
npm run build
```

### Linting

```bash
npm run lint
```

## File Overview

```
nextjs-frontend/
├── app/
│   ├── layout.tsx          ← Root layout (edit for global changes)
│   ├── page.tsx            ← Home page (shows ChatInterface)
│   └── globals.css         ← Global styles (Tailwind + custom CSS)
│
├── components/
│   ├── ChatInterface.tsx  ← **START HERE** - Main component
│   ├── ChatMessage.tsx    ← Message display
│   ├── ChatInput.tsx      ← Input field
│   └── ...                ← Other UI components
│
├── hooks/
│   ├── useChat.ts         ← Chat state management
│   └── useDarkMode.ts     ← Dark mode logic
│
├── lib/
│   ├── api.ts             ← Flask API calls
│   └── utils.ts           ← Helper functions
│
└── types/
    └── index.ts           ← TypeScript types
```

## Making Your First Change

Let's customize the welcome message:

1. Open `components/ChatInterface.tsx`
2. Find the welcome message (around line 200)
3. Change the text:
```tsx
<p className="text-gray-800 dark:text-gray-200">
  Hi! I'm HAL, your CMPE/SE advising assistant. I can help you with:
</p>
```

4. Save the file
5. See the change instantly in your browser

## Customizing Colors

Edit `tailwind.config.ts`:

```typescript
colors: {
  'sjsu-blue': '#0055A2',    // Change this
  'sjsu-gold': '#E5A823',    // Or this
},
```

All blue/gold colors throughout the app will update.

## Production Build

When ready to deploy:

```bash
npm run build
npm start
```

This creates an optimized production build.

## Getting Help

- **Frontend issues**: Check browser console (F12)
- **Backend issues**: Check Flask terminal output
- **API errors**: Use browser Network tab to inspect requests
- **TypeScript errors**: Run `npm run build` to see all errors
- **Documentation**: Read `README.md` and `MIGRATION_GUIDE.md`

## Summary

You now have:
- ✅ Flask backend running on port 5000
- ✅ Next.js frontend running on port 3000
- ✅ Working chat interface
- ✅ All features from original Flask UI
- ✅ Modern React architecture with TypeScript

Enjoy building with Next.js! 🚀
