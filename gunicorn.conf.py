# Gunicorn configuration file
import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Number of threads per worker
threads = 2

# Bind address
bind = "0.0.0.0:5001"

# Timeout
timeout = 30

# Access log - records incoming HTTP requests
accesslog = "/var/log/gunicorn.access.log"

# Error log - records Gunicorn server goings-on
errorlog = "/var/log/gunicorn.error.log"

# Whether to send Flask output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
loglevel = "info"
