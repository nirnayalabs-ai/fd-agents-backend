# FD Agents Backend

## Overview

This backend project is designed as the core engine for a multi-agent AI system, where different agents collaborate, debate, and refine answers before producing a final response.

The idea is inspired by:

human-like discussion panels,

collaborative decision-making systems, and

AI debate frameworks.

## Getting Started

Follow these steps to set up the backend on your local environment.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # For Mac/Linux
venv\Scripts\activate      # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Your backend will now be accessible at:

```
http://127.0.0.1:8000/
```

### 6. Environment Variables (Optional)

Create a `.env` file in your root directory and add your configuration:

```
SECRET_KEY=your_secret_key
DEBUG=True
```

## License

This project is licensed under your preferred license.
