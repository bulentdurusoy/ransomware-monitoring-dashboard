# ── Ransomware Monitoring Dashboard ────────────────────────────────────────────
# Lightweight Streamlit image for the CTI dashboard.
# ───────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create the data directory for volume mounts
RUN mkdir -p /app/data

# Expose the default Streamlit port
EXPOSE 8501

# Health-check (optional but nice to have)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
