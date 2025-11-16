FROM python:3.11-slim

ARG environment=prod
ARG VERSION=dev
ARG COMMIT=unknown
ARG BUILD_DATE=unknown
ENV APP_VERSION=$VERSION
ENV APP_COMMIT=$COMMIT
ENV APP_BUILD_DATE=$BUILD_DATE

WORKDIR /app

# Copy needed files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -e ".[${environment}]"

# Run the application
RUN chmod +x /app/start.sh

WORKDIR /app/src

CMD ["/app/start.sh"]

# Expose 9890 port
EXPOSE 9890