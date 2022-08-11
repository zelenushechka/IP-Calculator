FROM python:3.10
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
RUN pip install --upgrade pip & pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "ip_calculator/manage.py", "runserver", "0.0.0.0:8000"]