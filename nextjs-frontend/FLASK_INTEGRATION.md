# Flask Backend Integration Guide

This guide explains how to configure the Flask backend to work seamlessly with the Next.js frontend.

## Required Flask Changes

### 1. Install Flask-CORS

The Next.js frontend runs on a different port (3000) than Flask (5000) during development, so you need CORS support.

```bash
pip install flask-cors
```

Add to `requirements.txt`:
```
flask-cors>=4.0.0
```

### 2. Configure CORS in Flask

Edit `/Users/aryankumar/Documents/personal-projects/HAL-AI-AdvisorBot/hal/app.py`:

```python
from flask_cors import CORS

def create_app(config_class=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Configure CORS for Next.js development
    CORS(app,
         origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
         supports_credentials=True,
         allow_headers=['Content-Type'],
         methods=['GET', 'POST', 'OPTIONS'])

    # Initialize extensions
    Session(app)
    init_db(app)
    init_admin(app)

    # Register routes
    register_routes(app)

    return app
```

### 3. Production CORS Configuration

For production, use environment variable for allowed origins:

```python
import os
from flask_cors import CORS

def create_app(config_class=None):
    app = Flask(__name__)

    # ... other config ...

    # CORS configuration
    allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app,
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=['Content-Type'],
         methods=['GET', 'POST', 'OPTIONS'])

    return app
```

Add to `.env`:
```bash
# Development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production
CORS_ORIGINS=https://your-frontend-domain.com
```

### 4. Session Configuration

Ensure session cookies work cross-origin:

```python
# hal/config.py
class Config:
    # ... existing config ...

    # Session configuration
    SESSION_COOKIE_SAMESITE = 'Lax'  # or 'None' for cross-domain
    SESSION_COOKIE_SECURE = False     # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
```

For production with separate domains:
```python
class ProductionConfig(Config):
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_DOMAIN = '.yourdomain.com'  # Shared domain
```

## API Endpoints Checklist

Verify these endpoints return JSON (not HTML):

### ✅ Existing JSON Endpoints

- `POST /api/chat` - Main chat endpoint
- `POST /api/feedback` - Submit feedback
- `POST /api/quick-replies` - Get suggestions
- `POST /api/clear-history` - Clear chat
- `GET /api/status` - System status

### ⚠️ Legacy Endpoints

- `GET /get` - Returns plain text (legacy, can keep for compatibility)
- `GET /` - Renders HTML template (keep for Flask UI)

## Testing the Integration

### 1. Start Flask Backend

```bash
python3 run.py
```

Verify it's running:
```bash
curl http://127.0.0.1:5000/api/status
```

Expected response:
```json
{
  "status": "ok",
  "provider": "claude",
  "model": "claude-3-5-sonnet-20241022",
  "session_id": "..."
}
```

### 2. Test CORS

From your browser console (or use curl):

```javascript
fetch('http://127.0.0.1:5000/api/status', {
  credentials: 'include'
})
  .then(r => r.json())
  .then(console.log)
```

Should return JSON without CORS errors.

### 3. Test Chat Endpoint

```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CS 149?"}'
```

Expected response:
```json
{
  "response": "CS 149 is Operating Systems...",
  "confidence": 0.95,
  "intent": "course_prerequisites",
  "course_cards": [...]
}
```

## Environment Setup

### Development

```bash
# .env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Production

```bash
# .env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-...
CORS_ORIGINS=https://hal-advisor.vercel.app
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=True
```

## Deployment Scenarios

### Scenario 1: Same Domain

**Frontend**: `https://hal.sjsu.edu`
**Backend**: `https://hal.sjsu.edu/api`

No CORS needed, use reverse proxy:

```nginx
# nginx.conf
server {
    listen 80;
    server_name hal.sjsu.edu;

    location / {
        proxy_pass http://localhost:3000;  # Next.js
    }

    location /api {
        proxy_pass http://localhost:5000;  # Flask
    }

    location /admin {
        proxy_pass http://localhost:5000;  # Flask Admin
    }
}
```

### Scenario 2: Different Subdomains

**Frontend**: `https://app.hal.sjsu.edu`
**Backend**: `https://api.hal.sjsu.edu`

Set shared cookie domain:

```python
SESSION_COOKIE_DOMAIN = '.hal.sjsu.edu'
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
```

CORS origins:
```python
CORS(app, origins=['https://app.hal.sjsu.edu'], ...)
```

### Scenario 3: Completely Different Domains

**Frontend**: `https://hal-advisor.vercel.app`
**Backend**: `https://hal-api.railway.app`

Full CORS configuration:

```python
from flask_cors import CORS

CORS(app,
     origins=['https://hal-advisor.vercel.app'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     expose_headers=['Content-Type', 'Set-Cookie'])
```

## Security Considerations

### 1. CORS Origins

**Never** use `origins='*'` with `supports_credentials=True`:

```python
# ❌ DANGEROUS
CORS(app, origins='*', supports_credentials=True)

# ✅ SAFE
CORS(app, origins=['https://specific-domain.com'], supports_credentials=True)
```

### 2. Session Security

Production settings:

```python
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # 1 hour
```

### 3. Rate Limiting

Add rate limiting to API endpoints:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    # ... existing code ...
```

### 4. API Key Protection

Never expose API keys to frontend:

```python
# ❌ DON'T send to frontend
return jsonify({
    "api_key": app.config['ANTHROPIC_API_KEY']  # NEVER!
})

# ✅ Keep on server only
# API keys stay in server-side .env
```

## Monitoring

### Request Logging

Add request logging for debugging:

```python
@app.before_request
def log_request():
    app.logger.info(f"{request.method} {request.path}")
    app.logger.debug(f"Origin: {request.headers.get('Origin')}")
    app.logger.debug(f"User-Agent: {request.headers.get('User-Agent')}")

@app.after_request
def log_response(response):
    app.logger.info(f"Response: {response.status_code}")
    return response
```

### Health Check

Add a comprehensive health endpoint:

```python
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db.engine.url.database,
        "provider": Config.LLM_PROVIDER.value,
        "frontend_allowed": request.headers.get('Origin') in allowed_origins
    })
```

## Troubleshooting

### CORS Error: "No 'Access-Control-Allow-Origin' header"

1. Check Flask-CORS is installed: `pip list | grep -i cors`
2. Verify CORS is configured in `create_app()`
3. Check allowed origins match frontend URL exactly
4. Restart Flask server after changes

### Session Not Persisting

1. Check `credentials: 'include'` in fetch calls
2. Verify `supports_credentials=True` in CORS
3. Check browser cookies (Developer Tools → Application → Cookies)
4. Ensure `SESSION_COOKIE_SAMESITE` is correct

### 500 Internal Server Error

1. Check Flask logs: `python3 run.py`
2. Verify all environment variables are set
3. Check database connection
4. Test endpoints with curl

### Preflight OPTIONS Request Failing

CORS preflight checks happen before actual request:

```python
# Flask should handle OPTIONS automatically, but if not:
@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 204
    # ... rest of chat logic ...
```

## Complete Example

Here's a complete minimal Flask setup for Next.js:

```python
# hal/app.py
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
import os

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'

    # CORS
    allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)

    # Session
    Session(app)

    # Routes
    @app.route('/api/status')
    def status():
        return jsonify({
            'status': 'ok',
            'session_id': session.get('session_id')
        })

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json()
        # ... your chat logic ...
        return jsonify({'response': 'Hello!'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
```

Run it:
```bash
python3 run.py
```

Test it:
```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Next Steps

1. Install flask-cors: `pip install flask-cors`
2. Update `hal/app.py` with CORS configuration
3. Update `requirements.txt`
4. Restart Flask server
5. Test from Next.js frontend
6. Deploy to production

## Production Checklist

- [ ] Flask-CORS installed and configured
- [ ] Allowed origins set via environment variable
- [ ] Session cookies secured (HTTPS, HttpOnly, SameSite)
- [ ] Rate limiting enabled
- [ ] Request logging configured
- [ ] Health check endpoint added
- [ ] API keys protected (not exposed to frontend)
- [ ] CORS origins limited to production domains only
- [ ] Database connection pooled for performance
- [ ] Error handling returns proper JSON responses
