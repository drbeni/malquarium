FROM python:3.7-alpine

# install dependencies
RUN apk add --no-cache --virtual \
    exiftool

ADD exif_tool.py /exif_tool.py

CMD ["/usr/local/bin/python3", "/exif_tool.py"]