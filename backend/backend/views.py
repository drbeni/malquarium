import os
import pyminizip
import shutil
import tempfile
from urllib.parse import unquote

import ssdeep
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, StreamingHttpResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from backend.models import Sample, Tag, AccessStatistic, LogAction, AnalyzerResult
from backend.serializers import SimpleSampleSerializer, FullSampleSerializer, ProfileSerializer, TagSerializer
from backend.utils import samples as sample_utils
from backend.utils import time
from backend.utils.sample_store import SampleStore, SampleNotFoundException
from malquarium import constants
from malquarium.settings import MAX_SAMPLE_SIZE, SAMPLE_ZIP_PASSWORD, MIN_SSDEEP_MATCH


class SampleList(APIView):
    queryset = Sample.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    match_scores = {}

    def get(self, request, search_string, format=None):
        AccessStatistic.increment_search(request.user)

        sample_results = None
        search_string = unquote(search_string)
        search_string = search_string.strip().lower()

        if request.user.id:
            query = Sample.objects.filter(Q(private=False) | Q(uploader=request.user))
        else:
            query = Sample.objects.filter(private=False)

        if constants.SHA256_PATTERN.match(search_string):
            sample_results = query.filter(sha2=search_string)
        elif constants.SHA1_PATTERN.match(search_string):
            sample_results = query.filter(sha1=search_string)
        elif constants.MD5_PATTERN.match(search_string):
            sample_results = query.filter(md5=search_string)
        elif constants.SSDEEP_PATTERN.match(search_string):
            chunk_length = int(search_string.split(':')[0])
            seven_grams = sample_utils.ssdeep_to_int_ngram(search_string)

            verified_samples = []
            for sample in query.filter(ssdeep_length__in=[chunk_length, chunk_length * 2, chunk_length / 2],
                                       ssdeep_7grams__overlap=seven_grams):
                match = ssdeep.compare(sample.ssdeep, search_string)
                if match >= MIN_SSDEEP_MATCH:
                    verified_samples.append(sample.id)
                    self.match_scores[sample.sha2] = match

            sample_results = query.filter(id__in=verified_samples)

        if sample_results is None:
            for word in search_string.split(" "):
                query = query.filter(tags__name__startswith=word)

            sample_results = query.prefetch_related('tags', 'source').order_by('-create_date').distinct()[:500]

        page = self.paginate_queryset(sample_results)
        if page is not None:
            serializer = SimpleSampleSerializer(page, many=True)
            serializer_data = self.enrich_samples_with_match_score(serializer.data)
            return self.get_paginated_response(serializer_data)
        else:
            serializer = SimpleSampleSerializer(sample_results, many=True)
            serializer_data = self.enrich_samples_with_match_score(serializer.data)
            return Response(serializer_data)

    def enrich_samples_with_match_score(self, serializer_data):
        for i in range(len(serializer_data)):
            sample_id = serializer_data[i]['sha2']
            if sample_id in self.match_scores:
                serializer_data[i]['match_score'] = self.match_scores[sample_id]

        return serializer_data

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class SampleFeed(ListAPIView):
    queryset = Sample
    serializer_class = SimpleSampleSerializer

    def get(self, request, *args, **kwargs):
        """
        Get the latest samples by number, timestamp or hash
        """

        if request.user.id:
            query = Sample.objects.filter(Q(private=False) | Q(uploader=request.user))
        else:
            query = Sample.objects.filter(private=False)

        sample_filter = kwargs['filter']
        tag_filter = kwargs.get('tags')

        if tag_filter is not None:
            for word in tag_filter.split(","):
                query = query.filter(tags__name__startswith=word)

        samples = []

        try:
            sample_num = int(sample_filter)
            if 0 < sample_num < 1001:
                samples = query.prefetch_related('tags', 'source').order_by('-create_date')[:sample_num]

        except ValueError:
            pass

        if not samples:
            last_sample = None

            if constants.SHA256_PATTERN.match(sample_filter):
                last_sample = query.filter(private=False).filter(sha2=sample_filter).first()
            elif constants.SHA1_PATTERN.match(sample_filter):
                last_sample = query.filter(private=False).filter(sha1=sample_filter).first()
            elif constants.MD5_PATTERN.match(sample_filter):
                last_sample = query.filter(private=False).filter(md5=sample_filter).first()
            if last_sample:
                sample_candidates = query.filter(create_date__gte=last_sample.create_date) \
                    .prefetch_related('tags', 'source').order_by('create_date')[:1500]

                found_last_sample = False
                for sample_candidate in sample_candidates:
                    if found_last_sample:
                        samples.append(sample_candidate)

                    if sample_candidate.sha2 == sample_filter \
                            or sample_candidate.sha1 == sample_filter \
                            or sample_candidate.md5 == sample_filter:
                        found_last_sample = True

        if not samples:
            try:
                sample_timestamp = float(sample_filter)
                create_date = time.timestamp_to_datetime(sample_timestamp)
                samples = query.filter(create_date__gte=create_date).prefetch_related('tags', 'source') \
                              .order_by('-create_date')[:1000]
            except ValueError:
                return Response({'details': 'Invalid argument {}'.format(sample_filter)},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(SimpleSampleSerializer(samples, many=True).data)


class SampleDetail(APIView):
    queryset = Sample.objects.all()

    def get(self, request, sha2, format=None):
        sample = get_sample(sha2, request.user)
        return Response(FullSampleSerializer(sample).data)


class SampleDownload(APIView):
    queryset = Sample.objects.all()
    authentication_classes = (JWTAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, sample_format, sha2):
        if not request.user.profile.in_download_quota():
            return Response({'details': 'Download Quota exceeded'}, status=status.HTTP_403_FORBIDDEN)

        sample = get_sample(sha2, request.user)
        try:
            sample_path = SampleStore().get_sample_path(sample.sha2)
        except SampleNotFoundException:
            raise Http404

        AccessStatistic.increment_download(request.user)

        try:
            trid_result = AnalyzerResult.objects.get(analyzer__identifier='trid', sample=sample)
            ending = trid_result.result_data.get("ending", "")

        except AnalyzerResult.DoesNotExist:
            ending = ""

        if sample_format == 'zip':
            return self.get_sample_as_encrypted_zip(sample, sample_path, ending)

        elif sample_format == 'raw':
            return self.get_sample_as_raw_data(sample, sample_path, ending)

        else:
            return Response({'details': 'Invalid data format {}'.format(sample_format)},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_sample_as_encrypted_zip(self, sample, sample_path, ending):
        # Copy sample to /tmp because pyminizip cannot rename the file after compression
        tmp_sample_path = os.path.join(tempfile.gettempdir(), sample.sha2 + ending)
        shutil.copyfile(sample_path, tmp_sample_path)

        with tempfile.NamedTemporaryFile() as tmp_zip_file:
            try:
                pyminizip.compress(tmp_sample_path, None, tmp_zip_file.name, SAMPLE_ZIP_PASSWORD, 0)
            except OSError:
                raise Http404

            response = StreamingHttpResponse(
                open(tmp_zip_file.name, 'rb'),
                content_type='application/zip'
            )
            response['Content-Disposition'] = "attachment; filename={}.zip".format(sample.sha2)
            response['Content-Length'] = os.stat(tmp_zip_file.name).st_size

            os.remove(tmp_sample_path)

            return response

    def get_sample_as_raw_data(self, sample, sample_path, ending):
        try:
            response = StreamingHttpResponse(
                open(sample_path, 'rb'),
                content_type='application/octet-stream'
            )
        except FileNotFoundError:
            raise Http404

        response['Content-Disposition'] = "attachment; filename={}{}".format(sample.sha2, ending)
        response['Content-Length'] = os.stat(sample_path).st_size

        return response


class SampleUpload(APIView):
    queryset = Sample.objects.all()

    authentication_classes = (JWTAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        if not request.user.profile.in_upload_quota():
            return Response({'details': 'Upload Quota exceeded'}, status=status.HTTP_403_FORBIDDEN)

        sample_binary = request.FILES['file']
        if sample_binary.size > MAX_SAMPLE_SIZE:
            return Response({'details': "File size limit exceeded"}, status=status.HTTP_400_BAD_REQUEST)

        private = request.POST.get('private', False) in ('true', 'True', True, 1) \
                  and 'ps' in request.user.profile.service_plan.get_compressed_capabilities()

        try:
            sample, file_info = sample_utils.create(sample_binary, request.user, private, sample_binary.name, True)
            AccessStatistic.increment_upload(request.user)

            if 'tags' in request.POST:
                for tags in request.POST.getlist('tags'):
                    for t in tags.split(','):
                        if t.strip():
                            sample_utils.add_tag(sample, t, request.user, True)

            if 'source' in request.POST and not sample.source:
                sample_utils.add_source(sample, request.POST['source'], request.user, True)

            return Response({'details': 'OK', 'sha2': file_info.sha2}, status=status.HTTP_201_CREATED)

        except sample_utils.UnwantedSampleFormatException as e:
            return Response({'details': '{}'.format(e)}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class SampleStats(APIView):
    queryset = Sample.objects.all()

    def get(self, request, format=None):
        total_samples = self.queryset.count()
        return Response({'count': total_samples})


class TagList(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@api_view(['POST'])
@authentication_classes((JWTAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def add_tag(request, tag_name, sha2):
    sample = get_sample(sha2, request.user)

    if sample.uploader != request.user:
        return Response({'details': 'Nice try...'}, status=status.HTTP_403_FORBIDDEN)

    tag_name = tag_name.strip().lower()
    sample_utils.add_tag(sample, tag_name, request.user, True)

    return Response({'details': 'OK', 'tag': tag_name, 'sha2': sha2})


@api_view(['POST'])
@authentication_classes((JWTAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def remove_tag(request, tag_name, sha2):
    sample = get_sample(sha2, request.user)

    if sample.uploader != request.user:
        return Response({'details': 'Nice try...'}, status=status.HTTP_403_FORBIDDEN)

    try:
        tag_to_remove = Tag.objects.get(name=tag_name)
    except Tag.DoesNotExist:
        raise Http404

    sample.tags.remove(tag_to_remove)
    LogAction.add_log(request.user, 'remove', tag_to_remove, sample)
    return Response({'details': 'OK', 'tag': tag_name, 'sha2': sha2})


def get_sample(sha2, user):
    try:
        if user.id:
            return Sample.objects.get(Q(sha2=sha2.lower()) & (Q(private=False) | Q(uploader=user)))
        else:
            return Sample.objects.get(sha2=sha2.lower(), private=False)
    except Sample.DoesNotExist:
        raise Http404


class ProfileView(APIView):
    queryset = User.objects.all()

    authentication_classes = (JWTAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        return Response(ProfileSerializer(user).data)


class TokenReset(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)

        return Response(ProfileSerializer(request.user).data)
