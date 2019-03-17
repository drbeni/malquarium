FROM debian:9-slim

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        libfuzzy-dev \
        libltdl7 \
        python3-pip \
        python3-virtualenv \
        virtualenv \
    && rm -r /var/lib/apt/lists/*

# Create Virtualenv for Python3
RUN mkdir -p /app/env
RUN mkdir -p /app/static
WORKDIR /app/env

RUN virtualenv --python=/usr/bin/python3 malquarium
ENV VIRTUAL_ENV /app/env/malquarium

RUN $VIRTUAL_ENV/bin/pip3 install \
        Django \
        django-cors-headers \
        djangorestframework \
        djangorestframework-simplejwt \
        drf-yasg \
        feedparser \
        gunicorn \
        ngram \
        psycopg2-binary \
        pyminizip \
        python-magic \
        ssdeep \
        yara-python \
    --no-warn-script-location

ADD backend /app/backend
ADD malquarium /app/malquarium
ADD tools /app/tools
ADD manage.py /app/manage.py
ADD init_all.py /app/init_all.py
ADD manage_yara.py /app/manage_yara.py
ADD feedcrawler.py /app/feedcrawler.py
ADD virus_total.py /app/virus_total.py
ADD tag_manager.py /app/tag_manager.py
ADD cleanup.py /app/cleanup.py
ADD update_trid_format.py /app/update_trid_format.py

WORKDIR /app/

# Compile yara rules
RUN $VIRTUAL_ENV/bin/python3 /app/manage_yara.py generate && $VIRTUAL_ENV/bin/python3 /app/manage_yara.py compile

# Cleanup
RUN rm -rf /app/backend/migrations
RUN rm -rf /tools/yara

CMD /app/env/malquarium/bin/python3 /app/init_all.py && /app/env/malquarium/bin/gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 4 malquarium.wsgi
