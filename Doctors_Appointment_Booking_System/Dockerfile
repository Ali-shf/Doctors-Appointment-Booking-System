# pull official base image
FROM python:3.11-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# copy project
COPY . .

# copy entrypoint and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# set entrypoint
ENTRYPOINT ["sh", "./entrypoint.sh"]

