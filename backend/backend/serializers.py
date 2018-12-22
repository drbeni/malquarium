from rest_framework import serializers

from backend.models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ('id',)


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        exclude = ('id',)


class VirusTotalResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirusTotalResult
        exclude = ('id',)


class FullSampleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    uploader = serializers.SerializerMethodField()
    analyzer_results = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [dict(t._asdict()) for t in obj.tags.all().values_list('name', named=True)]

    def get_source(self, obj):
        return SourceSerializer(obj.source, many=False).data

    def get_uploader(self, obj):
        return obj.uploader.username

    def get_analyzer_results(self, obj):
        analyzer_results = {}
        for analyzer_result in AnalyzerResult.objects.filter(sample=obj):
            analyzer_results[analyzer_result.analyzer.identifier] = {
                "name": analyzer_result.analyzer.name,
                "data": analyzer_result.result_data
            }
        return analyzer_results

    class Meta:
        model = Sample
        exclude = ('id', 'ssdeep_length', 'ssdeep_7grams')


class SimpleSampleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    vt_result = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [dict(t._asdict()) for t in obj.tags.all().values_list('name', named=True)]

    def get_source(self, obj):
        return obj.source.name if obj.source else None

    def get_vt_result(self, obj):
        return '{} / {}'.format(obj.vt_positives, obj.vt_total) if obj.vt_total else None

    class Meta:
        model = Sample
        fields = ('sha2', 'sha1', 'md5', 'tags', 'source', 'create_date', 'vt_result')


class ServicePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlan
        exclude = ('id',)


class ProfileSerializer(serializers.ModelSerializer):
    service_plan = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()

    def get_service_plan(self, obj):
        return ServicePlanSerializer(obj.profile.service_plan).data

    def get_usage_stats(self, obj):
        data_set = AccessStatistic.get_data_set(obj)
        return {
            'download_requests': data_set.download_requests,
            'upload_requests': data_set.upload_requests
        }

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'auth_token', 'service_plan', 'usage_stats')
