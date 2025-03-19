## ---------------- Build Stage ----------------
FROM python:3.13-bookworm AS builder

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add astral uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod +x /install.sh && /install.sh && rm /install.sh

# Set up UV env correctly
ENV PATH="/root/.local/bin:${PATH}"

# Set the working directory in the container
WORKDIR /duck_db_api

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

## ---------------- Production Stage ----------------
FROM python:3.13-slim-bookworm AS production

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    jq \
    # dependencies for weasyprint
    poppler-utils libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
    # cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /duck_db_api
COPY --from=builder /duck_db_api/.venv ./.venv

# Set up UV env correctly
ENV PATH="/duck_db_api/.venv/bin:${PATH}"

# Copy the rest of the application code
COPY . .

# Create an alias for 'll' as 'ls -al'
RUN echo 'alias ll="ls -al"' >> /root/.bashrc && echo 'alias ll="ls -al"' > /root/.bash_aliases

# Expose the port your app runs on
EXPOSE 8000

# run the command from the src directory
# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
