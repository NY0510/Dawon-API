# SRC MODULE

**Generated:** 2025-04-02

## OVERVIEW
Application code - FastAPI routes and API client logic (~490 LOC total).

## STRUCTURE
```
src/
├── main.py         # FastAPI app, 3 routes, lifespan with auto-login
├── lib.py          # DwClient: HTTP + WebSocket client with retry
└── models/         # Pydantic schemas (see models/AGENTS.md)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Route definitions | main.py | @app.get for /devices, /chart, /current |
| Client initialization | main.py:12-20 | lifespan() - login on startup, store in app.state |
| Session management | lib.py:31-40 | __aenter__/__aexit__ for aiohttp.ClientSession |
| Login retry | lib.py:67-86 | _request_with_retry - auto re-login on session expiry |
| WebSocket connection | lib.py:143-189 | get_websocket_data - 3 messages, 2s timeout |
| HTML parsing | lib.py:112-141 | get_websocket_payload - regex extract wsUri/message |

## CONVENTIONS
- All async methods in DwClient
- Session checked via `_is_session_expired()` (HTML meta-refresh or "login" text)
- Max 2 attempts per request (original + re-login retry)
- WebSocket uses cookies from HTTP session via `Cookie` header
- print() for logging (no logging module)

## ANTI-PATTERNS
- No __init__.py - flat module imports
- Mixed concerns: DwClient handles HTTP, WebSocket, HTML parsing, retry logic

## NOTES
- `get_current_data()` assumes wsUri/message extraction succeeds before WebSocket connect
- No explicit session cleanup on error in `get_current_data()`
