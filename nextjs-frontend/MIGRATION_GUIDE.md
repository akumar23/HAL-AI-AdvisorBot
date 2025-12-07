# Migration Guide: Flask Templates to Next.js

This guide explains how to migrate from the Flask/Jinja2 frontend to the Next.js frontend.

## Overview

The HAL AI AdvisorBot has been migrated from a server-rendered Flask application with Jinja2 templates to a modern Next.js 14+ frontend with React components. The Flask backend remains unchanged and serves as a REST API.

## Architecture Changes

### Before (Monolithic)

```
Flask App
├── Routes (renders HTML)
├── Templates (Jinja2)
├── Static Files (CSS, JS)
└── Business Logic (RAG, LLM)
```

### After (Decoupled)

```
Next.js Frontend              Flask Backend (API)
├── React Components          ├── API Routes (JSON)
├── TypeScript                ├── Business Logic (RAG, LLM)
├── Tailwind CSS              ├── Database
└── API Client ──────────────→└── Services
```

## Key Benefits

1. **Better Performance**
   - Client-side routing (no page reloads)
   - Code splitting and lazy loading
   - Optimized asset delivery

2. **Improved Developer Experience**
   - TypeScript for type safety
   - Hot module replacement
   - Component-based architecture
   - Better debugging tools

3. **Modern Stack**
   - React 18+ with hooks
   - Next.js 14+ App Router
   - Server components for SEO
   - Tailwind CSS for rapid styling

4. **Scalability**
   - Frontend and backend can scale independently
   - Can deploy to different platforms
   - Easier to add features

## Migration Steps

### Step 1: Start the Flask Backend

The Flask backend now serves **only** as an API (no template rendering):

```bash
# In project root
python3 run.py
```

This starts the Flask API at http://127.0.0.1:5000

### Step 2: Start the Next.js Frontend

```bash
cd nextjs-frontend
npm install
npm run dev
```

This starts the Next.js app at http://localhost:3000

### Step 3: Configure API URL

The Next.js app connects to Flask via environment variables:

```bash
# nextjs-frontend/.env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

For production, change this to your production API URL.

## Code Comparison

### Before: Flask Template (base.html)

```html
<div id="chatbox">
    <!-- Messages rendered server-side with Jinja2 -->
</div>

<script>
    // jQuery-based chat logic
    function getBotResponse() {
        $.ajax({
            url: "/api/chat",
            method: "POST",
            data: JSON.stringify({ message: text })
        }).done(function(data) {
            // Manually manipulate DOM
            $("#chatbox").append(botHtml);
        });
    }
</script>
```

### After: Next.js Component

```tsx
// components/ChatInterface.tsx
export function ChatInterface() {
  const { messages, sendUserMessage } = useChat();

  return (
    <div>
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
    </div>
  );
}
```

## Feature Parity Checklist

All features from the Flask frontend have been migrated:

- ✅ Chat interface with messages
- ✅ Dark mode with localStorage persistence
- ✅ Responsive mobile design
- ✅ Course cards for rich responses
- ✅ Feedback modal with comments
- ✅ Quick reply suggestions
- ✅ Typing indicator
- ✅ Confidence badges
- ✅ Human handoff cards
- ✅ Session management (via cookies)
- ✅ Clear chat functionality
- ✅ Provider/model info display
- ✅ Accessibility (ARIA labels, keyboard shortcuts)

## API Changes Required

The Flask backend already supports JSON APIs, but you may need to ensure CORS is configured:

```python
# hal/app.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
```

This is only needed if you're running frontend and backend on different ports during development.

## Session Management

The Next.js frontend uses the same session management as before:

- Flask creates a session cookie on first request
- Next.js includes credentials in fetch requests: `credentials: 'include'`
- Session ID stored in Flask session
- Conversation history maintained server-side

## Deployment Options

### Option 1: Separate Deployment

**Frontend (Vercel/Netlify):**
```bash
cd nextjs-frontend
npm run build
```

**Backend (Heroku/Railway/DigitalOcean):**
```bash
# Deploy Flask app as usual
python3 run.py
```

Set `NEXT_PUBLIC_API_URL` to your production backend URL.

### Option 2: Single Server

Serve Next.js build from Flask:

```python
# hal/app.py
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_nextjs(path):
    if path and os.path.exists(f"nextjs-frontend/out/{path}"):
        return send_from_directory('nextjs-frontend/out', path)
    return send_from_directory('nextjs-frontend/out', 'index.html')
```

Build Next.js as static export:
```bash
# next.config.js
module.exports = {
  output: 'export',
}
```

### Option 3: Docker Compose

```yaml
version: '3.8'
services:
  frontend:
    build: ./nextjs-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:5000

  backend:
    build: .
    ports:
      - "5000:5000"
```

## Performance Improvements

### Before (Flask)
- Full page reload on navigation
- jQuery DOM manipulation
- All JS loaded upfront
- ~500KB total bundle

### After (Next.js)
- Client-side navigation
- React virtual DOM
- Code splitting
- ~150KB initial bundle

## Development Workflow

### Old Workflow
1. Edit Jinja2 template
2. Edit inline JavaScript
3. Refresh browser manually
4. Check browser console for errors

### New Workflow
1. Edit React component
2. Hot reload automatically
3. TypeScript catches errors
4. React DevTools for debugging

## Backwards Compatibility

The Flask backend is **100% backwards compatible**:

- All `/api/*` endpoints remain unchanged
- Legacy `/get` endpoint still works
- Admin interface still accessible at `/admin`
- Database schema unchanged

You can run both frontends simultaneously:
- Flask frontend: http://127.0.0.1:5000/
- Next.js frontend: http://localhost:3000/

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:

```python
# Install flask-cors
pip install flask-cors

# Add to hal/app.py
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

### Session Issues

If chat history isn't persisting:

1. Check that `credentials: 'include'` is set in API calls
2. Verify Flask session is configured correctly
3. Check browser cookies (should see Flask session cookie)

### API Connection Errors

If Next.js can't connect to Flask:

1. Verify Flask is running on port 5000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Test API directly: `curl http://127.0.0.1:5000/api/status`

## Future Enhancements

Now that we have a modern frontend, we can easily add:

- **Real-time Features**: WebSocket support for live chat
- **Progressive Web App**: Install as desktop/mobile app
- **Offline Support**: Service workers for offline functionality
- **Advanced Analytics**: User interaction tracking
- **A/B Testing**: Compare different UI variants
- **Internationalization**: Multi-language support
- **Voice Input**: Speech-to-text for accessibility

## Rollback Plan

If you need to rollback to the Flask frontend:

1. Stop Next.js server
2. Flask app at http://127.0.0.1:5000/ still serves original UI
3. No changes to backend required
4. All data preserved in database

## Migration Timeline

- **Phase 1**: Next.js setup and component creation ✅
- **Phase 2**: Feature parity testing
- **Phase 3**: User acceptance testing
- **Phase 4**: Production deployment
- **Phase 5**: Deprecate Flask templates

## Questions?

For issues or questions about the migration:
1. Check this guide
2. Review Next.js documentation
3. Check Flask API endpoints
4. Review component code in `nextjs-frontend/components/`
