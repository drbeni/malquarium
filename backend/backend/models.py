from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.utils import time as time_utils


class Sample(models.Model):
    sha1 = models.TextField(db_index=True, verbose_name=' sha1')
    sha2 = models.TextField(db_index=True, verbose_name=' sha2')
    md5 = models.TextField(db_index=True, verbose_name=' md5')
    ssdeep = models.TextField(verbose_name=' ssdeep')
    original_filename = models.TextField()
    size = models.IntegerField()
    magic = models.TextField()
    vt_permalink = models.TextField(null=True, blank=True, verbose_name='VT Permalink')
    vt_total = models.SmallIntegerField(null=True, blank=True, verbose_name='VT total')
    vt_positives = models.SmallIntegerField(null=True, blank=True, verbose_name='VT positives')
    vt_scan_date = models.DateTimeField(null=True, blank=True, verbose_name='VT scan date')
    vt_results = models.ManyToManyField('VirusTotalResult', blank=True, verbose_name='VT results')
    vt_checked = models.BooleanField(default=False, verbose_name='VT checked')
    tags = models.ManyToManyField('Tag')
    source = models.ForeignKey('Source', on_delete=models.SET_NULL, null=True, db_index=True)
    url = models.TextField(null=True, blank=True, verbose_name='URL')
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    create_date = models.DateTimeField()
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.sha2

    def get_identifier(self):
        return {'id': self.id, 'name': self.sha2}

    @staticmethod
    def get_similar_sample_to(imphash, size, pe_meta):
        for similar_candidate in Sample.objects.filter(imphash=imphash, size=size):
            found_similar = True
            for i in range(len(similar_candidate.pe_meta['Sections'])):
                try:
                    new_section = pe_meta['Sections'][i]
                    cand_section = similar_candidate.pe_meta['Sections'][i]

                    if new_section['Name'] != cand_section['Name'] \
                            or new_section['VirtualAddress'] != cand_section['VirtualAddress'] \
                            or new_section['RawSize'] != cand_section['RawSize'] \
                            or new_section['Entropy'] != cand_section['Entropy']:
                        found_similar = False
                        break

                except IndexError:
                    found_similar = False
                    break

            if found_similar:
                return similar_candidate

    class Meta:
        db_table = 'sample'


class Analyzer(models.Model):
    identifier = models.TextField(unique=True)
    name = models.TextField(unique=True)
    docker_image_name = models.TextField(unique=True)
    mime_whitelist = ArrayField(models.TextField(), null=True, blank=True)
    mime_blacklist = ArrayField(models.TextField(), null=True, blank=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'analyzer'


class AnalyzerResult(models.Model):
    analyzer = models.ForeignKey('Analyzer', on_delete=models.CASCADE)
    result_data = JSONField(blank=True)
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(self.analyzer.name, self.id)

    class Meta:
        db_table = 'analyzer_result'


class VirusTotalResult(models.Model):
    av = models.TextField(verbose_name='AV')
    malware_name = models.TextField(db_index=True)

    def __str__(self):
        return self.malware_name

    class Meta:
        db_table = 'virus_total_result'


class Tag(models.Model):
    name = models.TextField(db_index=True)

    def __str__(self):
        return self.name

    def get_identifier(self):
        return {'id': self.id, 'name': self.name}

    class Meta:
        db_table = 'tag'


class Source(models.Model):
    name = models.TextField(db_index=True)
    url = models.TextField(null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

    def get_identifier(self):
        return {'id': self.id, 'name': self.name}

    class Meta:
        db_table = 'source'


class Feed(models.Model):
    url = models.TextField()
    format = JSONField()
    source = models.ForeignKey('Source', on_delete=models.PROTECT)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.url

    def get_identifier(self):
        return {'id': self.id, 'name': self.url}

    class Meta:
        db_table = 'feed'


class CrawledUrl(models.Model):
    url = models.TextField()
    feed = models.ForeignKey('Feed', on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    class Meta:
        db_table = 'crawled_url'


class LogAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation = models.TextField()
    data = JSONField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return "{} - {}: {}".format(
            self.user,
            self.operation,
            ", ".join(["{}({})".format(x['entity'], x['name']) for x in self.data])
        )

    @staticmethod
    def add_log(user, operation, *entities):
        return LogAction.objects.create(
            user=user,
            operation=operation,
            timestamp=time_utils.get_datetime_now(),
            data=[
                {
                    'entity': str(x.__class__.__name__),
                    'name': x.get_identifier()['name'],
                    'id': x.get_identifier()['id']
                } for x in entities
            ]
        )

    class Meta:
        db_table = 'log_action'


class AccessStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    day = models.DateField()
    download_requests = models.IntegerField(default=0)
    search_requests = models.IntegerField(default=0)
    upload_requests = models.IntegerField(default=0)

    def __str__(self):
        return "{} - D: {}, S: {}, U: {}".format(self.user if self.user else 'AnonymousUser', self.download_requests,
                                                 self.search_requests, self.upload_requests)

    @staticmethod
    def increment_search(user):
        data_set = AccessStatistic.get_data_set(user)
        data_set.search_requests += 1
        data_set.save()

    @staticmethod
    def increment_download(user):
        data_set = AccessStatistic.get_data_set(user)
        data_set.download_requests += 1
        data_set.save()

    @staticmethod
    def increment_upload(user):
        data_set = AccessStatistic.get_data_set(user)
        data_set.upload_requests += 1
        data_set.save()

    @staticmethod
    def get_data_set(user):
        if user.id is not None:
            data_set_user = user
        else:
            data_set_user = None

        data_set, created = AccessStatistic.objects.get_or_create(user=data_set_user, day=time_utils.get_date_now())
        return data_set

    class Meta:
        db_table = 'access_statistic'


class ServicePlan(models.Model):
    name = models.TextField(default='Basic')
    download_quota = models.IntegerField(default=1000)
    upload_quota = models.IntegerField(default=1000)
    capabilities = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_compressed_capabilities(self):
        compressed_capabilities = {}
        if not self.capabilities:
            return compressed_capabilities

        if "private_samples" in self.capabilities:
            compressed_capabilities['ps'] = 1
        if "source_access" in self.capabilities:
            compressed_capabilities['sa'] = 1

        return compressed_capabilities

    class Meta:
        db_table = 'service_plan'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.PROTECT)

    def __str__(self):
        return "{}: {}".format(self.user, self.service_plan)

    def in_download_quota(self):
        return AccessStatistic.get_data_set(self.user).download_requests <= self.service_plan.download_quota

    def in_upload_quota(self):
        return AccessStatistic.get_data_set(self.user).upload_requests <= self.service_plan.upload_quota

    class Meta:
        db_table = 'auth_user_profile'


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, service_plan=ServicePlan.objects.get(name='Basic'))
    instance.profile.save()
