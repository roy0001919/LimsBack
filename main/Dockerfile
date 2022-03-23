FROM python:3.8.3
MAINTAINER Roy LO "RoyLuo@smarter.com.tw"

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt
RUN pip install uwsgi

#CMD ["chown -R user:user /usr/local/bin/uwsgi"]
CMD ["/usr/local/bin/uwsgi", "app.ini"]


