import multiprocessing

# Gunicorn Configuration
bind = "0.0.0.0:8080"           # required for DigitalOcean container networking
workers = 1                     # one worker to avoid memory duplication
threads = 2                     # enable light concurrency
worker_class = "gthread"        # better for IO-heavy (OpenAI API) tasks
timeout = 180                   # allow long AI generation requests
keepalive = 5                   # keep connections alive
max_requests = 30               # recycle worker to prevent leaks
max_requests_jitter = 5         # randomize restarts slightly
preload_app = False             # prevent preloading large models into memory
log_level = "info"              # clean, useful logs
