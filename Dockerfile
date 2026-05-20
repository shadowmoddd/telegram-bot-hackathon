FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directory
RUN mkdir -p data

# Populate DB at build time
RUN python scripts/populate_db.py

CMD ["python", "-m", "bot.main"]
