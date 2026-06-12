FROM python:3.10.10
WORKDIR /app
COPY requirements_docker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5000
CMD ["python", "flask_service.py"]
