FROM python:3.9

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt
RUN pip install uwsgi

#CMD ["chown -R user:user /usr/local/bin/uwsgi"]
CMD ["/usr/local/bin/uwsgi", "app.ini"]


