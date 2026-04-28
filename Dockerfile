FROM mcr.microsoft.com/playwright/python:v1.49.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install --with-deps

CMD ["python", "-m", "app.main"]