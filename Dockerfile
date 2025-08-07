FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
COPY order_router.py .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "order_router.py" ]