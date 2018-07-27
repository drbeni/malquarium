#!/usr/bin/env python3

import argparse
import io
import json
import math
import os
import pathlib
import sys
import zipfile

import requests
from requests.auth import AuthBase

from settings import API_URL, API_KEY, LOCAL_SAMPLE_DIR, SAMPLE_ZIP_PASSWORD


class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token ' + self.token
        return r


def upload_sample(args):
    sample_file = args.sample

    if not os.path.isfile(sample_file):
        print("Upload failed: {} is not a valid file".format(sample_file))

    files = {'file': (sample_file.split(os.sep)[-1], open(sample_file, "r+b"))}
    data = {}
    if args.tags is not None:
        data["tags"] = args.tags
    if args.source is not None:
        data["source"] = args.source

    r = requests.post(API_URL.strip('/') + '/samples/', files=files, data=data, auth=TokenAuth(API_KEY))
    if r.status_code == 201:
        print("Successfully uploaded {}".format(sample_file))
        exit(0)
    elif r.status_code == 200 or r.status_code == 400:
        print(json.dumps(r.json()['details'], indent=4))
        exit(1)
    elif r.status_code == 415:
        error_message = r.json()['details']
        print("Unable to upload {} because of {}".format(sample_file, error_message))
        exit(0)
    elif r.status_code == 401:
        print(json.dumps(r.json(), indent=4))
        exit(1)
    else:
        print("Hmm, something went wrong with sample file: {}".format(sample_file))
        exit(1)


def search_samples(args):
    r = requests.get(API_URL.strip('/') + '/query/{}/?page={}'.format(args.sample, args.page))
    if r.status_code == 200:
        data = r.json()
        print(json.dumps({
            'count': data['count'],
            'pages': math.ceil(data['count'] / max(len(data['results']), 1)),
            'results': data['results']
        }, indent=4))
    else:
        print("Error: {}".format(r.text))
        exit(1)


def sample_info(args):
    r = requests.get(API_URL.strip('/') + '/samples/{}/'.format(args.sample))

    if r.status_code == 200:
        print(json.dumps(r.json(), indent=4))
    elif r.status_code == 404:
        print("Error: Sample {} does not exist".format(args.sample))
        exit(1)
    else:
        print("Error: {}".format(r.text))
        exit(1)


def download_sample(args):
    if not os.path.isdir(LOCAL_SAMPLE_DIR):
        try:
            pathlib.Path(LOCAL_SAMPLE_DIR).mkdir(parents=True, exist_ok=True)

        except OSError as e:
            print("Failed to create local sample dir {} because of {}".format(LOCAL_SAMPLE_DIR, e))
            exit(1)

    r = requests.get(API_URL.strip('/') + '/samples/download/{}/'.format(args.sample), auth=TokenAuth(API_KEY))
    if r.status_code == 200:
        print("Unpacking sample {} to {}/{}".format(args.sample, LOCAL_SAMPLE_DIR, args.sample))
        zip_data = io.BytesIO(r.content)
        with zipfile.ZipFile(zip_data) as zipped_sample:
            zipped_sample.extractall(LOCAL_SAMPLE_DIR, pwd=SAMPLE_ZIP_PASSWORD.encode())
    elif r.status_code == 404:
        print("Error: Sample {} does not exist".format(args.sample))
        exit(1)
    else:
        print("Failed to download sample: {}".format(r.text))
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="virus.exchange API client")
    parser.add_argument('action', help="Action to perform. One of: upload, download, info, search")
    parser.add_argument('sample', help="Sample file path for upload, SHA-256 for download/info, query for search")
    parser.add_argument('--page', help='Page number for large sample query results', default=1)
    parser.add_argument('--tags', nargs='*', help="Tags for the sample")
    parser.add_argument('--source', help="Source of the sample")

    if len(sys.argv) < 3:
        parser.print_help()
        exit(1)

    args = parser.parse_args()

    if args.action.lower().startswith('u'):
        upload_sample(args)
    elif args.action.lower().startswith('d'):
        download_sample(args)
    elif args.action.lower().startswith('s'):
        search_samples(args)
    elif args.action.lower().startswith('i'):
        sample_info(args)


if __name__ == '__main__':
    main()
