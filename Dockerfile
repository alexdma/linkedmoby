FROM python:3.8-alpine

LABEL maintainer="alexdma@apache.org" 

# TODO separate app from configuration and data
COPY . /app
WORKDIR /app

# Update & Install packages
# Note that some Python packages might be built using gcc
RUN apk add --no-cache --update \
    bash \
    curl

RUN pip install --upgrade pip && pip install -r requirements.txt

# Cleanup
RUN rm -rf ~/.cache/pip

WORKDIR /app
CMD ["python", "linkedmoby.py", "all" ]