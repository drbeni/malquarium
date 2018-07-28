#!/usr/bin/env python
import os
import sys


def main(old_tag, new_tag):
    for sample in Sample.objects.filter(tags__name__startswith=old_tag)[:10000]:

        sample_utils.add_tag(sample, new_tag, None, False)

        for tag_to_remove in Tag.objects.filter(name__startswith=old_tag):
            if tag_to_remove in sample.tags.all():
                sample.tags.remove(tag_to_remove)
                print("{}: {} => {}".format(sample.sha2, tag_to_remove.name, new_tag))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tag_manager.py old_tag new_tag")
        exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()
    from backend.models import Sample, Tag
    from backend.utils import samples as sample_utils

    main(sys.argv[1], sys.argv[2])