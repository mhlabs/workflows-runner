# Docker image with PYTHON3 and DEPENDENCES for pyodbc with MS ODBC 17 DRIVER, Debian GNU/Linux 10 (buster)
# Using the official Python image
FROM python:3.10-slim

# UPGRADE pip3
#RUN pip3 install --upgrade pip

###
#ARG PORT
#ENV PORT=${PORT:-8080}

WORKDIR /app
COPY ./app ./
COPY requirements.txt .

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

RUN pip3 install -r requirements.txt

#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --worker-class uvicorn.workers.UvicornWorker --log-level=debug main:app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --worker-class uvicorn.workers.UvicornWorker main:app