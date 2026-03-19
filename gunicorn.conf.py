# Gunicorn configuration for Investment Portfolio Analyzer
# Used by Render deployment

import os

# Bind to port from environment or default to 10000 (Render default)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker settings
workers = 1  # Use single worker to minimize memory usage on 512MB instances
worker_class = "sync"

# Timeout settings - increased for PDF processing
timeout = 120  # Allow 2 minutes for large PDF processing (default is 30s)
graceful_timeout = 30

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Memory optimization
max_requests = 100  # Restart worker after 100 requests to prevent memory leaks
max_requests_jitter = 10  # Add randomness to prevent all workers restarting at once
