# Gunicorn configuration file

# Number of worker processes
workers = 2

# Number of threads per worker
threads = 2

# Bind address
bind = "0.0.0.0:12999"

# Timeout
timeout = 30

# Access log - records incoming HTTP requests
accesslog = "/var/log/gunicorn.access.log"

# Error log - records Gunicorn server going-ons
errorlog = "/var/log/gunicorn.error.log"

# Whether to send Flask output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
loglevel = "debug"
