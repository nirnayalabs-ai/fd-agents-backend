# ---------------------------------
# 1. Base Image
# ---------------------------------
FROM python:3.11-slim

# ---------------------------------
# 2. Environment Variables
# ---------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------------------------
# 3. Work Directory
# ---------------------------------
WORKDIR /app

# ---------------------------------
# 4. System Dependencies
# ---------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------
# 5. Install Python Dependencies
# ---------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------------------------------
# 6. Copy Project
# ---------------------------------
COPY . .

# ---------------------------------
# 7. Expose Django Port
# ---------------------------------
EXPOSE 8000

# ---------------------------------
# 8. Run Gunicorn
# ---------------------------------
CMD ["bash", "-c", "python manage.py migrate && gunicorn your_project_name.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
