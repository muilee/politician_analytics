FROM python:3.6

MAINTAINER matt

ADD ./g2_project /web

WORKDIR /web

RUN pip install -r /web/requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
