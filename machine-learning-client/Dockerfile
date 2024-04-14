FROM python:3.8-slim

WORKDIR /app

RUN pip install pymongo opencv-python-headless numpy

COPY ml_client.py .

CMD ["python", "ml_client.py"]