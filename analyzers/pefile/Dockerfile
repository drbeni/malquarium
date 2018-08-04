FROM buildpack-deps:stretch as base

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        libfuzzy-dev \
        python3-pip \
    && rm -r /var/lib/apt/lists/*


RUN /usr/bin/pip3 install \
        pefile \
        ssdeep


FROM debian:9-slim

# Install python3
RUN apt-get update \
    && apt-get install -y \
        libfuzzy2 \
        python3.5-minimal \
    && rm -r /var/lib/apt/lists/*

RUN mkdir -p /usr/local/lib/python3.5
COPY --from=base /usr/local/lib/python3.5 /usr/local/lib/python3.5

ADD run_pefile.py /run_pefile.py

CMD ["/usr/bin/python3.5", "/run_pefile.py"]
