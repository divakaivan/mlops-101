FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

EXPOSE 8000

ARG MLFLOW_TRACKING_URI=http://localhost:5000
ENV MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
