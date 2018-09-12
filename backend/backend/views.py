import os
import pyminizip
import re
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

from backend.models import Sample, Tag, AccessStatistic, LogAction
from backend.serializers import SimpleSampleSerializer, FullSampleSerializer, ProfileSerializer, TagSerializer
from backend.utils import samples as sample_utils
from backend.utils.sample_store import SampleStore, SampleNotFoundException
from malquarium.settings import MAX_SAMPLE_SIZE, SAMPLE_ZIP_PASSWORD, MIN_SSDEEP_MATCH


class SampleList(APIView):
    queryset = Sample.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    def get(self, request, search_string, format=None):
        AccessStatistic.increment_search(request.user)

        sample_results = None
        search_string = unquote(search_string)
        search_string = search_string.strip().lower()

        # search for hash matches first
        sha256_pattern = re.compile('^[a-f0-9]{64}$')
        sha1_pattern = re.compile('^[a-f0-9]{40}$')
        md5_pattern = re.compile('^[a-f0-9]{32}$')
        ssdeep_pattern = re.compile('^\d+:[^:]+:[^:]+$')

        if request.user.id:
            query = Sample.objects.filter(Q(private=False) | Q(uploader=request.user))
        else:
            query = Sample.objects.filter(private=False)

        if sha256_pattern.match(search_string):
            sample_results = query.filter(sha2=search_string)
        elif sha1_pattern.match(search_string):
            sample_results = query.filter(sha1=search_string)
        elif md5_pattern.match(search_string):
            sample_results = query.filter(Q(md5=search_string) | Q(imphash=search_string))
        elif ssdeep_pattern.match(search_string):
            chunk_length = int(search_string.split(':')[0])
            seven_grams = sample_utils.ssdeep_to_int_ngram(search_string)

            verified_samples = []
            for sample in query.filter(ssdeep_length__in=[chunk_length, chunk_length * 2, chunk_length / 2],
                                       ssdeep_7grams__overlap=seven_grams):
                match = ssdeep.compare(sample.ssdeep, search_string)
                if match >= MIN_SSDEEP_MATCH:
                    verified_samples.append(sample.id)

            sample_results = query.filter(id__in=verified_samples)

        if sample_results is None:
            for word in search_string.split(" "):
                query = query.filter(tags__name__startswith=word)

            sample_results = query.prefetch_related('tags', 'source').order_by('-create_date').distinct()[:500]

        page = self.paginate_queryset(sample_results)
        if page is not None:
            serializer = SimpleSampleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = SimpleSampleSerializer(sample_results, many=True)
            return Response(serializer.data)

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


class LatestSamplesList(ListAPIView):
    queryset = Sample.objects.filter(private=False).prefetch_related('tags', 'source').order_by('-create_date')[:10]
    serializer_class = SimpleSampleSerializer


class SampleDetail(APIView):
    queryset = Sample.objects.all()

    def get(self, request, sha2, format=None):
        sample = get_sample(sha2, request.user)
        return Response(FullSampleSerializer(sample).data)


class SampleDownload(APIView):
    queryset = Sample.objects.all()
    authentication_classes = (JWTAuthentication, TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, sha2):
        if not request.user.profile.in_download_quota():
            return Response({'details': 'Download Quota exceeded'}, status=status.HTTP_403_FORBIDDEN)

        sample = get_sample(sha2, request.user)
        sha2 = sample.sha2
        try:
            sample_path = SampleStore().get_sample_path(sha2)
        except SampleNotFoundException:
            raise Http404

        with tempfile.NamedTemporaryFile() as tmp_zip_file:
            try:
                pyminizip.compress(sample_path, None, tmp_zip_file.name, SAMPLE_ZIP_PASSWORD, 0)
            except OSError:
                raise Http404

            AccessStatistic.increment_download(request.user)

            response = StreamingHttpResponse(
                open(tmp_zip_file.name, 'rb'),
                content_type='application/zip'
            )
            response['Content-Disposition'] = "attachment; filename={}.zip".format(sha2)
            response['Content-Length'] = os.stat(tmp_zip_file.name).st_size

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
