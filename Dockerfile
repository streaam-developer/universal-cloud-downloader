# Stage 1: Build dependencies
FROM python:3.10-slim as builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Add the local bin to the PATH
ENV PATH=/root/.local/bin:$PATH

# Expose the download directory as a volume
VOLUME /app/downloads

# Run the bot
CMD ["python", "-m", "bot.main"]
