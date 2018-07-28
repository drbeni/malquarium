#!/usr/bin/env python
import os
from datetime import datetime

import pytz
import requests

API_KEY = os.getenv('VT_API_KEY', 'your-VT-key-if-you-dont-like-docker')
VT_REPORT_URL = 'https://www.virustotal.com/vtapi/v2/file/report'
VT_QUOTA = 4


class SampleDoesNotExistOnVirusTotalException(Exception):
    pass


class VirusTotalQuotaExceededException(Exception):
    print("Virus Total quota exceeded")


def get_vt_report(sha2):
    r = requests.get(VT_REPORT_URL, params={'apikey': API_KEY, 'resource': sha2})

    if r.status_code == 200:
        data = r.json()
        if data['response_code'] == 1:
            return data
        elif data['response_code'] == 0:
            raise SampleDoesNotExistOnVirusTotalException
    elif r.status_code == 204:
        raise VirusTotalQuotaExceededException
    else:
        raise Exception("Fetching data from VT failed with status {} and response {}".format(r.status_code, r.text))


def update_sample_with_vt_report(sample, vt_report):
    if not vt_report:
        sample.vt_checked = True
        sample.save()
        return

    scan_date = datetime.strptime(vt_report['scan_date'], '%Y-%m-%d %H:%M:%S')
    localized_scan_date = timezone.make_aware(scan_date, timezone=pytz.timezone('UTC'))

    sample.vt_permalink = vt_report['permalink']
    sample.vt_scan_date = localized_scan_date
    sample.vt_total = vt_report['total']
    sample.vt_positives = vt_report['positives']
    sample.vt_checked = True

    scans = vt_report['scans']
    for av in scans:
        if scans[av]['detected']:
            result, created = VirusTotalResult.objects.get_or_create(av=av, malware_name=scans[av]['result'])
            if result not in sample.vt_results.all():
                sample.vt_results.add(result)

    sample.save()


def main():
    checked_sample_ids = set()

    # Check VT_QUOTA samples in one run
    checked_samples = 0
    for sample in Sample.objects.filter(vt_checked=False).order_by('-create_date')[:10]:
        if checked_samples == VT_QUOTA:
            break

        if sample.id in checked_sample_ids:
            continue

        try:
            vt_report = get_vt_report(sample.sha2)
            update_sample_with_vt_report(sample, vt_report)
            checked_sample_ids.add(sample.id)
            checked_samples += 1

        except SampleDoesNotExistOnVirusTotalException:
            sample.vt_checked = True
            sample.save()

        except VirusTotalQuotaExceededException:
            break

        except Exception as e:
            print("Error: {}".format(e))
            break


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "malquarium.settings")
    import django

    django.setup()

    from django.utils import timezone
    from backend.models import Sample, VirusTotalResult

    main()
