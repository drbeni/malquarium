FROM debian:9-slim as base

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        python-dev \
        python-pip \
    && rm -r /var/lib/apt/lists/*


RUN /usr/bin/pip install \
        oletools \
        python-magic


FROM debian:9-slim

# Install python2
RUN apt-get update \
    && apt-get install -y \
        python2.7-minimal \
    && rm -r /var/lib/apt/lists/*


RUN mkdir -p /usr/local/lib/python2.7/
COPY --from=base /usr/local/lib/python2.7 /usr/local/lib/python2.7

ADD run_oletools.py /run_oletools.py

CMD ["/usr/bin/python2.7", "/run_oletools.py"]
