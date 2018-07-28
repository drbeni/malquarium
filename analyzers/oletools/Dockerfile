FROM buildpack-deps:xenial

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        python-dev \
        python-pip \
    && rm -r /var/lib/apt/lists/*


RUN /usr/bin/pip install \
        oletools

ADD run_oletools.py /run_oletools.py

CMD ["/usr/bin/python2", "/run_oletools.py"]
