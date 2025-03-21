FROM python:3.11-slim

ARG environment=prod

WORKDIR /app

# Copy needed files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -e ".[${environment}]"

# Run the application
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]

# Expose 8000 port
EXPOSE 8000