FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN cat /tmp/requirements.txt

RUN python -m pip install --upgrade pip

RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY app.py .
COPY model.py .
COPY plant_model.keras .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]