# This Dockerfile is for the backend service
# DigitalOcean will detect this in the root

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy backend requirements and install
COPY backend/resume_maker/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    shared-mime-info \
    fonts-dejavu-core fonts-liberation fonts-noto-core \
 && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/resume_maker/ .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "resume_maker.wsgi:application", "--bind", "0.0.0.0:8000"]
