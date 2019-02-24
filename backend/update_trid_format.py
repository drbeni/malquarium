#!/usr/bin/env python
import os

ENDING_TAG_MAP = {
    ".APK": "apk",
    ".EXE": "exe",
    ".DLL": "dll",
    ".DOC": "doc",
    ".DOCX": "docx",
    ".HTM/HTML": "html",
    ".HTML": "html",
    ".O": "elf",
    ".RAR": "rar",
    ".XLS": "xls",
    ".XLSX": "xlsx",
}


def main():
    try:
        update_user = User.objects.get(username='drbeni')
    except User.DoesNotExist:
        update_user = User.objects.first()

    for analyzer_result in AnalyzerResult.objects \
                                   .filter(analyzer__identifier='trid') \
                                   .exclude(result_data__has_key='data')[:10000]:

        print("Updating TRiD result of sample {}".format(analyzer_result.sample.sha2))

        ending = analyzer_result.result_data[0]['ending']

        new_result_data = {
            'data': analyzer_result.result_data,
            'ending': ending.lower().split('/')[0]
        }

        if ending in ENDING_TAG_MAP:
            tag = ENDING_TAG_MAP[ending]
            add_tag(analyzer_result.sample, tag, update_user, False)
            new_result_data['tags'] = [tag]

        analyzer_result.result_data = new_result_data
        analyzer_result.save(update_fields=('result_data',))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()

    from backend.models import AnalyzerResult, User
    from backend.utils.samples import add_tag

    main()
