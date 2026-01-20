FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .

# Expose port
EXPOSE 8000

# Run the agent
CMD ["python", "agent.py"]
