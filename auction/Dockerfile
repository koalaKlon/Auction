FROM python:3.9-alpine

RUN apk add --no-cache build-base libffi-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["daphne", "-p", "8000", "auction.asgi:application"]
