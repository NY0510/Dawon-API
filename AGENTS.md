# PROJECT KNOWLEDGE BASE

**Generated:** 2025-04-02
**Commit:** N/A
**Branch:** main

## OVERVIEW
Unofficial FastAPI wrapper for Dawon AIPM smart plug control (Python 3.13+, ~490 LOC).

## STRUCTURE
```
Dawon-API/
├── src/
│   ├── main.py      # FastAPI app & routes
│   ├── lib.py       # API client (DwClient) with WebSocket & session retry
│   └── models/      # Pydantic schemas (device, chart, current, enums)
├── pyproject.toml   # uv-based Python 3.13+ project
├── .env.example     # Auth credentials template
└── README.md        # Setup & usage docs
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API routes | src/main.py | 3 endpoints: /, /devices, /devices/{id}/chart, /devices/{id}/current |
| API client | src/lib.py | DwClient class - login, session retry, WebSocket parsing |
| Response models | src/models/ | Pydantic schemas for all API responses |
| Auth setup | .env | USER_ID, SSO_TOKEN, TERMINAL_ID, TERMINAL_NAME from mitmproxy capture |

## CONVENTIONS
- Python 3.13+ with uv (no venv management)
- Flat src/ layout (no package/__init__.py)
- Session retry on 401/redirect to login page
- WebSocket for real-time device data (3 messages, 2s timeout)
- JSON parsing with key_mapping for API field renames

## ANTI-PATTERNS (THIS PROJECT)
- None found in code comments (LICENSE has legal "do not" only)
- No test coverage
- No CI/CD (no .github/workflows)
- No linting/formatting config (no ruff, black, mypy config)

## UNIQUE STYLES
- `lib.py` contains both HTTP client and WebSocket logic in one class
- `get_current_data()` chains: HTTP → extract wsUri/message → WebSocket connect → parse 3 responses
- Session expiry detected via HTML meta-refresh or "login" in response text
- Re-login happens automatically in `_request_with_retry()` (max 2 attempts)

## COMMANDS
```bash
uv sync                                    # Install dependencies
uv run fastapi run src/main.py             # Start server
```

## NOTES
- Requires mitmproxy packet capture to extract auth credentials
- Tested on firmware 1.01.36 with B540-W model
- WebSocket connection uses cookies from HTTP session
- Chart data transforms "n"→"date", "sv"→"value" from API
- No async context manager for session in `get_current_data()` - session passed implicitly
