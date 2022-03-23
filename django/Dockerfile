FROM python:3.8.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
RUN pip install uwsgi
#RUN python manage.py collectstatic runserver 0.0.0.0:8000 --noinput --clear
#RUN python manage.py migrate                  # Apply database migrations

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#RUN python manage.py collectstatic --noinput