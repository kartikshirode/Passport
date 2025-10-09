# Gunicorn configuration file
# Run with: gunicorn -c gunicorn.conf.py main:app

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'passport-photo-api'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
enable_stdio_inheritance = True

# Worker lifecycle hooks
def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal (pid: %s)", worker.pid)

# Environment-specific configurations
if os.getenv('ENVIRONMENT') == 'development':
    reload = True
    workers = 1
    loglevel = 'debug'
elif os.getenv('ENVIRONMENT') == 'production':
    preload_app = True
    workers = max(2, multiprocessing.cpu_count())
    
# Memory and resource limits
worker_tmp_dir = "/dev/shm"  # Use RAM for worker tmp files
max_worker_memory = 500 * 1024 * 1024  # 500MB per worker

# SSL settings (if needed)
if os.getenv('SSL_CERT') and os.getenv('SSL_KEY'):
    certfile = os.getenv('SSL_CERT')
    keyfile = os.getenv('SSL_KEY')
    ssl_version = 2  # TLS 1.2+