from backend.apps import yara_scanner
from backend.models import Sample, Tag, Source, LogAction, Analyzer, AnalyzerResult
from backend.utils import time as time_utils
from backend.utils.analyzer import run_analyzer
from backend.utils.sample_store import SampleStore
from malquarium.settings import BLACKLISTED_MAGIC_STRINGS


def add_tag(sample, tag_name, user, log=True):
    tag_name = tag_name.lower().strip().strip('#').replace(' ', '_').replace('/', '_')
    if tag_name == 'none':
        return
    if tag_name.startswith('upx_'):
        tag_name = 'upx'
    elif tag_name.startswith('fsg_'):
        tag_name = 'fsg'
    elif tag_name.startswith('execryptor_'):
        tag_name = 'execryptor'
    elif tag_name.startswith('asprotect_'):
        tag_name = 'asprotect'
    elif tag_name.startswith('nspack_'):
        tag_name = 'nspack'
    elif tag_name.startswith('safedisc_'):
        tag_name = 'safedisc'
    elif tag_name.startswith('petite_'):
        tag_name = 'petite'
    elif tag_name.startswith('mew_'):
        tag_name = 'mew'
    elif tag_name.startswith('morphine_'):
        tag_name = 'morphine'
    elif tag_name.startswith('pex_'):
        tag_name = 'pex'
    elif tag_name.startswith('pecompact_'):
        tag_name = 'pecompact'
    elif tag_name.startswith('armadillo_'):
        tag_name = 'armadillo'
    elif tag_name.startswith('upolyx_'):
        tag_name = 'upolyx'
    elif tag_name.startswith('aspack_'):
        tag_name = 'aspack'
    elif tag_name.startswith('polyene_'):
        tag_name = 'polyene'
    elif tag_name.startswith('fasm_'):
        tag_name = 'fasm'
    elif tag_name.startswith('molebox_'):
        tag_name = 'molebox'
    elif tag_name.startswith('ascrypt_'):
        tag_name = 'ascrypt'
    elif tag_name.startswith('upack_'):
        tag_name = 'upack'
    elif tag_name.startswith("yoda's_protector_"):
        tag_name = 'yodas_protector'

    tag, created = Tag.objects.get_or_create(name=tag_name.strip())
    sample.tags.add(tag)
    sample.save()

    if log:
        LogAction.add_log(user, 'add', tag, sample)


def add_source(sample, source_name, user, log=True):
    try:
        source = Source.objects.get(name__iexact=source_name)
    except Source.DoesNotExist:
        source = Source.objects.create(name=source_name)
    sample.source = source
    sample.save()

    if log:
        LogAction.add_log(user, 'add', source, sample)


def create(sample_binary, user, private, original_filename, log=True, url=None):
    sample_store = SampleStore()
    file_info = sample_store.handle_uploaded_file(sample_binary)

    if Sample.objects.filter(sha2=file_info.sha2).exists():
        sample = Sample.objects.get(sha2=file_info.sha2)
        sample_store.remove_file_from_cache(file_info.sha2)

    else:
        magic_string = sample_store.calculate_magic(file_info.sha2)

        for blacklisted_string in BLACKLISTED_MAGIC_STRINGS:
            if blacklisted_string in magic_string:
                raise UnwantedSampleFormatException(
                    'Samples with format {} are not wanted on virus.exchange'.format(magic_string))

        sample_size = sample_binary.size if hasattr(sample_binary, 'size') else len(sample_binary.getvalue())

        sample = Sample.objects.create(
            sha2=file_info.sha2,
            sha1=file_info.sha1,
            md5=file_info.md5,
            original_filename=original_filename if original_filename else file_info.sha2,
            size=sample_size,
            ssdeep=file_info.ssdeep,
            uploader=user,
            magic=magic_string,
            create_date=time_utils.get_datetime_now(),
            private=private,
            url=url,
        )

        sample_mime = sample_store.calculate_mime(file_info.sha2)
        for analyzer in Analyzer.objects.filter(enabled=True):
            mime_matched = True

            if analyzer.mime_whitelist:
                mime_matched = False
                for whitelisted_mime in analyzer.mime_whitelist:
                    if whitelisted_mime in sample_mime:
                        mime_matched = True
                        break

            if mime_matched and analyzer.mime_blacklist:
                for blacklisted_mime in analyzer.mime_blacklist:
                    if blacklisted_mime in sample_mime:
                        mime_matched = False
                        break

            if mime_matched:
                print("Running analyzer {} on sample {}".format(analyzer.name, file_info.sha2))
                analyzer_result_data = run_analyzer(analyzer, sample_store.get_outer_sample_path(file_info.sha2))
                if analyzer_result_data:
                    AnalyzerResult.objects.create(
                        analyzer=analyzer,
                        sample=sample,
                        result_data=analyzer_result_data
                    )

                    if 'tags' in analyzer_result_data:
                        for t in analyzer_result_data['tags']:
                            add_tag(sample, t, user, log)

        for t in yara_scanner.scan(sample_store.get_sample_path(file_info.sha2)):
            add_tag(sample, t, user, log)

        sample.save()

    return sample, file_info


class UnwantedSampleFormatException(Exception):
    pass
