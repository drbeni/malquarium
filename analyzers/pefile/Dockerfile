FROM buildpack-deps:xenial

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
        libfuzzy-dev \
        python3-pip \
    && rm -r /var/lib/apt/lists/*


RUN /usr/bin/pip3 install \
        pefile \
        ssdeep

ADD run_pefile.py /run_pefile.py

CMD ["/usr/bin/python3", "/run_pefile.py"]
