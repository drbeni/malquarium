import json
import os
import re

import magic
from oletools import oleobj
from oletools.common.clsid import KNOWN_CLSIDS
from oletools.olevba import FileOpenError
from oletools.olevba import VBA_Parser
from oletools.rtfobj import RtfObjParser
from oletools.thirdparty import olefile

# Copied from oledir.py
STORAGE_NAMES = {
    olefile.STGTY_EMPTY: 'Empty',
    olefile.STGTY_STORAGE: 'Storage',
    olefile.STGTY_STREAM: 'Stream',
    olefile.STGTY_LOCKBYTES: 'ILockBytes',
    olefile.STGTY_PROPERTY: 'IPropertyStorage',
    olefile.STGTY_ROOT: 'Root',
}


# Copied from oledir.py
def sid_display(sid):
    if sid == olefile.NOSTREAM:
        return '-'  # None
    else:
        return sid


# Copied from oledir.py
def clsid_display(clsid):
    if clsid in KNOWN_CLSIDS:
        clsid += '\n%s' % KNOWN_CLSIDS[clsid]
    color = 'yellow'
    if 'CVE' in clsid:
        color = 'red'
    return (clsid, color)


# Copied from rtfobj.py
re_executable_extensions = re.compile(
    r"(?i)\.(EXE|COM|PIF|GADGET|MSI|MSP|MSC|VBS|VBE|VB|JSE|JS|WSF|WSC|WSH|WS|BAT|CMD|DLL|SCR|HTA|CPL|CLASS|JAR|PS1XML|PS1|PS2XML|PS2|PSC1|PSC2|SCF|LNK|INF|REG)\b")


# With a lot of code from oledir.py
def get_directory_entries(ole):
    directory_entries = []

    for id in range(len(ole.direntries)):
        d = ole.direntries[id]
        if d is None:
            # this direntry is not part of the tree: either unused or an orphan
            d = ole._load_direntry(id)  # ole.direntries[id]
            if d.entry_type == olefile.STGTY_EMPTY:
                status = 'unused'
            else:
                status = 'ORPHAN'
        else:
            status = '<Used>'
        if d.name.startswith('\x00'):
            # this may happen with unused entries, the name may be filled with zeroes
            name = ''
        else:
            # handle non-printable chars using repr(), remove quotes:
            name = repr(d.name)[1:-1]
        entry_type = STORAGE_NAMES.get(d.entry_type, 'Unknown')

        directory_entries.append({
            "id": id,
            "status": status,
            "type": entry_type,
            "name": name,
            "size": d.size
        })

    return directory_entries


# With a lot of code from rtfobj.py
def get_rtf_objects():
    with open('/sample', 'rb') as f:
        data = f.read()

        rtfp = RtfObjParser(data)
        rtfp.parse()

        out_data = []
        tags = []
        cve_regex = re.compile(' CVE-(\d{4}-\d+)')

        for rtfobj in rtfp.objects:
            if rtfobj.is_ole:
                tags.append('ole')

                ole_column = {'format_id': rtfobj.format_id}
                if rtfobj.format_id == oleobj.OleObject.TYPE_EMBEDDED:
                    ole_column['format_type'] = 'embedded'
                elif rtfobj.format_id == oleobj.OleObject.TYPE_LINKED:
                    ole_column['format_type'] = 'linked'
                else:
                    ole_column['format_type'] = 'unknown'
                ole_column['class_name'] = rtfobj.class_name
                # if the object is linked and not embedded, data_size=None:
                if rtfobj.oledata_size is None:
                    ole_column['data_size'] = -1
                else:
                    ole_column['data_size'] = rtfobj.oledata_size
                if rtfobj.is_package:
                    ole_column['package'] = {}
                    ole_column['package']['filename'] = rtfobj.filename
                    ole_column['package']['source_path'] = rtfobj.src_path
                    ole_column['package']['temp_path'] = rtfobj.temp_path
                    # check if the file extension is executable:
                    _, ext = os.path.splitext(rtfobj.filename)
                    if re_executable_extensions.match(ext):
                        ole_column['package']['executable'] = True
                # else:
                #     pkg_column = 'Not an OLE Package'
                if rtfobj.clsid is not None:
                    ole_column['CLSID'] = rtfobj.clsid
                    ole_column['CLSID_desc'] = rtfobj.clsid_desc

                    for match in cve_regex.findall(rtfobj.clsid_desc.upper()):
                        tags.append('cve-{}'.format(match))

                # Detect OLE2Link exploit
                # http://www.kb.cert.org/vuls/id/921560
                if rtfobj.class_name == b'OLE2Link':
                    ole_column[
                        'exploits'] = 'Possibly an exploit for the OLE2Link vulnerability (VU#921560, CVE-2017-0199)'
                    tags.append('cve-2017-0199')
            else:
                ole_column = {'error': 'Not a well-formed OLE object'}

            out_data.append({
                'id': rtfp.objects.index(rtfobj),
                'index': rtfobj.start,
                'ole_object': ole_column
            })

        return out_data, tags


def get_metadata(ole):
    out_data = {'SummaryInformation': {}, 'DocumentSummaryInformation': {}}
    metadata = ole.get_metadata()
    tags = []

    for prop in metadata.SUMMARY_ATTRIBS:
        try:
            out_data['SummaryInformation'][prop] = str(getattr(metadata, prop))
        except:
            out_data['SummaryInformation'][prop] = repr(getattr(metadata, prop))

    for prop in metadata.DOCSUM_ATTRIBS:
        try:
            out_data['DocumentSummaryInformation'][prop] = str(getattr(metadata, prop))
        except:
            out_data['DocumentSummaryInformation'][prop] = repr(getattr(metadata, prop))

    if out_data['SummaryInformation']['creating_application'] == 'Microsoft Office Word':
        tags.append('doc')

    return out_data, tags


def get_macros():
    extracted_macros = []
    macro_analysis = []
    tags = []

    try:
        vbaparser = VBA_Parser('/sample')
        vbaparser.detect_vba_macros()

        for (filename, stream_path, vba_filename, vba_code) in vbaparser.extract_macros():
            extracted_macros.append({
                "stream_path": stream_path,
                "vba_filename": vba_filename,
                "vba_code": vba_code
            })

        try:
            for kw_type, keyword, description in vbaparser.analyze_macros():
                macro_analysis.append({
                    "kw_type": kw_type,
                    "keyword": keyword,
                    "description": description
                })

                if keyword == 'Shell':
                    tags.append('run-file')
        except TypeError:
            pass

        macro_suspicious_categories = {
            "nb_macros": vbaparser.nb_macros,
            "nb_autoexec": vbaparser.nb_autoexec,
            "nb_suspicious": vbaparser.nb_suspicious,
            "nb_iocs": vbaparser.nb_iocs,
            "nb_hexstrings": vbaparser.nb_hexstrings,
            "nb_base64strings": vbaparser.nb_base64strings,
            "nb_dridexstrings": vbaparser.nb_dridexstrings,
            "nb_vbastrings": vbaparser.nb_vbastrings,
        }

        if vbaparser.nb_macros:
            tags.append('macros')

        if vbaparser.nb_hexstrings or vbaparser.nb_base64strings:
            tags.append('obfuscated')

    except FileOpenError:
        return None, tags

    return {
               "extracted_macros": extracted_macros,
               "macro_analysis": macro_analysis,
               "macro_suspicious_categories": macro_suspicious_categories
           }, tags


def file_is_relevant():
    mime = magic.Magic(mime=True)
    try:
        mime_type = mime.from_file('/sample')

        if 'text/rtf' in mime_type or 'application/vnd' in mime_type or 'application/ms' in mime_type:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def main():
    if not file_is_relevant():
        print("{}")
        return

    rtf_objects, tags = get_rtf_objects()
    macros, new_tags = get_macros()
    tags += new_tags

    try:
        ole = olefile.OleFileIO('/sample')
        metadata, new_tags = get_metadata(ole)
        tags += new_tags

        result = {
            "directory_entries": get_directory_entries(ole),
            "metadata": metadata,
            "rtf_objects": rtf_objects,
            "macros": macros,
            "tags": tags,
        }


    except IOError:
        # Not a OLE file
        result = {
            "rtf_objects": rtf_objects,
            "macros": macros,
            "tags": tags
        }

    for key in result:
        if result[key]:
            print(json.dumps(result))
            return

    print("{}")


if __name__ == '__main__':
    main()
