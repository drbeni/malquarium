FROM node:10-slim as base
# This intermediate container is needed to transpile and build the JS stuff

# Add sources
RUN mkdir /app
ADD public /app/public
ADD package.json /app/
ADD webpack.config.js /app/

# Get NPM dependencies
WORKDIR /app
RUN npm install

ADD src /app/src

# Build production scripts
RUN npm run-script build


FROM malquarium/backend:latest as backend
# This container collects the static files for DRF

ENV VIRTUAL_ENV /app/env/malquarium
WORKDIR /app/

# create temporary directory for static files
RUN mkdir /frontend
RUN $VIRTUAL_ENV/bin/python3 manage.py collectstatic --noinput


FROM nginx:latest

# Add static HTML, JS and CSS
RUN mkdir -p /var/www
COPY --from=base /app/build/static/css /var/www/static/css
COPY --from=base /app/build/static/js /var/www/static/js
COPY --from=base /app/build/static/media /var/www/static/media
COPY --from=base /app/build/index.html /var/www/
COPY --from=base /app/build/favicon.ico /var/www/
COPY --from=base /app/build/manifest.json /var/www/

# Add static files for Django admin and Rest Framework
COPY --from=backend /frontend/static_django/admin /var/www/static/admin
COPY --from=backend /frontend/static_django/rest_framework /var/www/static/rest_framework
COPY --from=backend /frontend/static_django/drf-yasg /var/www/static/drf-yasg

ADD nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]