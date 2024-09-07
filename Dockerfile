FROM python:3.12.5
# set work directory
WORKDIR /
# copy source files
COPY src /src
# copy requirements
COPY ./requirements.txt /requirements.txt
# install requirements
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
# run app
CMD cd src;\
    waitress-serve --host 127.0.0.1 habrhub.wsgi:application &\
    celery -A habrhub beat -l INFO &\
    celery -A habrhub worker -l INFO &&