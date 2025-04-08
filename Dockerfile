FROM python:3.11.11-bookworm AS builder

# Installing poetry
RUN pip install poetry==1.8.3
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Configure Git to use HTTPS instead of SSH
RUN git config --global url."https://".insteadOf git://
RUN git config --global url."https://github.com/".insteadOf git@github.com:

# Copying and installing dependencies
WORKDIR /app
COPY pyproject.toml ./
RUN touch README.md # Poetry needs an (empty) README file
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.11.11-slim-bookworm AS runner

# Using virtualenv from builder
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copying and installing the application code
COPY public_hub_services ./public_hub_services
COPY run-public_hub_services.py ./run-public_hub_services.py
COPY gunicorn.conf.py ./gunicorn.conf.py

# Creating directories
RUN mkdir -p /app/logs
ENV LOGGER_DIR=/app/logs

# Adding non-root user
RUN adduser public-services-user
RUN chown -R public-services-user:public-services-user /app
RUN chown -R public-services-user:public-services-user /var/log
USER public-services-user

# RUN
ENV SERVER_DEBUG=0
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run-public_hub_services:app"]