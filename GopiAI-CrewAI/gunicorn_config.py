#!/usr/bin/env python3
"""
Gunicorn configuration for production deployment of CrewAI API server
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5052"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/home/amritagopi/.gopiai/logs/gunicorn_access.log"
errorlog = "/home/amritagopi/.gopiai/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "crewai-api-server"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
enable_stdio_inheritance = True

print(f"🚀 Gunicorn configured with {workers} workers")
print(f"📊 Binding to {bind}")
print(f"📁 Logs: {accesslog} & {errorlog}")