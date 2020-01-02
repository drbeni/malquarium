#!/usr/bin/env python
import os
from datetime import datetime, timedelta

MIN_SAMPLE_SIZE = 1000
MAX_SAMPLE_SIZE = 26214400
MAX_AGE_IN_DAYS = 365


def delete_sample(sample, keep_meta=False):
    print("Trying to remove Sample {}".format(sample.sha2))
    try:
        sample_store.delete_sample_file(sample, keep_meta)
    except Sample.DoesNotExist:
        print("Warning: no SampleFile for {}".format(sample.sha2))


def main():
    for sample in Sample.objects.filter(
            vt_checked=True,
            vt_permalink__isnull=False,
            vt_positives=0,
            original_filename__startswith='VirusShare'
    ):
        delete_sample(sample)

    for sample in Sample.objects.filter(size__lt=MIN_SAMPLE_SIZE):
        delete_sample(sample)

    for sample in Sample.objects.filter(size__gt=MAX_SAMPLE_SIZE):
        delete_sample(sample)

    max_age = datetime.now() - timedelta(days=MAX_AGE_IN_DAYS)
    for sample in Sample.objects.filter(create_date__lt=max_age):
        delete_sample(sample, keep_meta=True)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()
    from backend.models import Sample
    from backend.utils.sample_store import SampleStore

    sample_store = SampleStore()

    main()
