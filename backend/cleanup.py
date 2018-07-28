#!/usr/bin/env python
import os


def delete_sample(sample):
    print("Trying to remove Sample {}".format(sample.sha2))
    try:
        sample_store.delete_sample_file(sample)
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

    for sample in Sample.objects.filter(size__lt=1000):
        delete_sample(sample)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()
    from backend.models import Sample
    from backend.utils.sample_store import SampleStore

    sample_store = SampleStore()

    main()
