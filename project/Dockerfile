FROM python:3.7
WORKDIR /usr/src/project

ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt /usr/src/project/
RUN pip install -r requirements.txt 

# copy project
COPY . /usr/src/project/
