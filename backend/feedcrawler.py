#!/usr/bin/env python
import csv
import io
import os
from json.decoder import JSONDecodeError

import feedparser
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout


def fetch_sample_file(sample, sample_url, crawl_user):
    print("Trying to fetch {}".format(sample_url))

    try:
        r = requests.get(sample_url, timeout=(30, 30))
        sample_binary = io.BytesIO(r.content)

        try:
            original_name = r.headers['Content-Disposition'].split('filename=')[1].strip('"')
        except KeyError:
            if not sample_url.endswith('/'):
                original_name = sample_url.split('/')[-1]
            else:
                original_name = None

        try:
            persisted_sample, file_info = sample_utils.create(sample_binary, crawl_user, False, original_name,
                                                              False, url=sample_url)
            sample_utils.add_source(persisted_sample, feed.source.name, crawl_user, False)

            print("Added sample {}".format(file_info.sha2))

            if 'tags_field' in feed.format:
                for tag in sample[int(feed.format['tags_field'])].split(','):
                    sample_utils.add_tag(persisted_sample, tag, crawl_user, False)
        except sample_utils.UnwantedSampleFormatException as e:
            print("Skipped {} because of {}".format(sample_url, e))

    except ConnectTimeout:
        print("Timeout while connecting to {}".format(sample_url))
        pass

    except ReadTimeout:
        print("Timeout while reading from {}".format(sample_url))
        pass

    except Exception as e:
        print("Failed to process {} because of {}".format(sample_url, e))


def process_url(feed, sample_url, sample, crawl_user):
    if not CrawledUrl.objects.filter(url=sample_url).exists():
        CrawledUrl.objects.create(url=sample_url, feed=feed)
        fetch_sample_file(sample, sample_url, crawl_user)


def crawl_feed(feed):
    try:
        crawl_user = User.objects.get(username='drbeni')
    except User.DoesNotExist:
        crawl_user = User.objects.get(username='beni')

    r = requests.get(feed.url)

    if feed.format['type'] == 'csv':
        data = '\n'.join([x for x in r.text.splitlines() if not x.startswith("#")])
        samples = csv.reader(data.splitlines(), dialect='unix')
        for sample in samples:

            if 'sha2_field' in feed.format:
                if Sample.objects.filter(sha2=sample[int(feed.format['sha2_field'])]).exists():
                    continue

            if 'online_field' in feed.format:
                if sample[int(feed.format['online_field'])] in ('offline', 'false', 'False', False, 0, '0'):
                    continue

            sample_url = sample[int(feed.format['url_field'])]
            process_url(feed, sample_url, sample, crawl_user)

    elif feed.format['type'] == 'json':
        try:
            data = r.json()
            for sample in data:
                if 'sha2_field' in feed.format:
                    if Sample.objects.filter(sha2=sample[feed.format['sha2_field']]).exists():
                        continue
                # malshare style
                if 'api_url' in feed.format:
                    if not 'api_param' in feed.format:
                        raise Exception(
                            "Invalid JSON feed configured for feed {}: 'api_param' is missing".format(feed.url))

                    sample_url = feed.format['api_url'] + sample[feed.format['api_param']]
                    process_url(feed, sample_url, sample, crawl_user)

        except JSONDecodeError as e:
            print("Error while decoding json: {}".format(e))

    elif feed.format['type'] == 'rss':
        parser = feedparser.parse(feed.url)
        # Hardcoded special treatment for each feed
        if 'malc0de' in feed.url:
            for sample in parser['entries']:
                data = sample['summary'].split(",")
                sample_url = None
                md5 = None
                for part in data:
                    if 'URL:' in part:
                        sample_url = part.split("URL: ")[1].strip()
                    elif 'MD5:' in part:
                        md5 = part.split("MD5: ")[1].strip()

                if Sample.objects.filter(md5=md5).exists():
                    continue

                if not sample_url.startswith("http"):
                    sample_url = "http://" + sample_url

                process_url(feed, sample_url, sample, crawl_user)

    else:
        raise Exception("Invalid feed type configured for feed {}".format(feed.url))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()

    from backend.models import Feed, CrawledUrl, Sample, User
    from backend.utils import samples as sample_utils

    for feed in Feed.objects.filter(disabled=False):
        crawl_feed(feed)
