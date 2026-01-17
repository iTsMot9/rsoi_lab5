FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src/auth-service /app/auth-service
WORKDIR /app/auth-service
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .
ENV HOST 0.0.0.0
ENV PORT 8050
EXPOSE 8050
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]
