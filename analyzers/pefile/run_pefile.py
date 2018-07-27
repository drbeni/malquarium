import json
import re
from datetime import datetime

import pefile
from pefile import PEFormatError


class PEParser:
    is_pe = False
    pe = None
    whitespace_regex = None

    def __init__(self, sample_path):
        try:
            self.pe = pefile.PE(sample_path)
            self.is_pe = True
            self.whitespace_regex = re.compile(r'\s+|\x00')
        except PEFormatError:
            pass

    def get_summary_infos(self):
        if self.is_pe:
            data = {
                'Header': {
                    **self.get_target_machine(),
                    **self.get_compilation_timestamp(),
                    **self.get_entry_point(),
                    **self.get_contained_sections()
                },
                'Sections': self.get_sections(),
                'Imports': self.get_imports(),
                'Imphash': self.get_imphash(),
                'DebugArtifacts': self.get_debug_info()
            }

            return data
        return None

    def get_imphash(self):
        return self.pe.get_imphash()

    def get_target_machine(self):
        if self.pe.FILE_HEADER.Machine == 0x014c:
            target_machine = 'x86'
        elif self.pe.FILE_HEADER.Machine == 0x0200:
            target_machine = 'Intel Itanium'
        elif self.pe.FILE_HEADER.Machine == 0x8664:
            target_machine = 'x64'
        else:
            target_machine = 'unknown'
        return {'TargetMachine': target_machine}

    def get_compilation_timestamp(self):
        compilation_timestamp = self.pe.FILE_HEADER.TimeDateStamp
        date_format = '%Y-%m-%d %H:%M:%S'
        return {'CompilationTimestamp': datetime.fromtimestamp(compilation_timestamp).strftime(date_format)}

    def get_entry_point(self):
        return {'EntryPoint': self.pe.NT_HEADERS.OPTIONAL_HEADER.AddressOfEntryPoint}

    def get_contained_sections(self):
        return {'ContainedSections': self.pe.FILE_HEADER.NumberOfSections}

    def get_sections(self):
        sections = []
        for section in self.pe.sections:
            sections.append({
                'Name': self.whitespace_regex.sub('', section.Name.decode(errors='replace')),
                'VirtualAddress': section.VirtualAddress,
                'VirtualSize': section.Misc_VirtualSize,
                'RawSize': section.SizeOfRawData,
                'Entropy': section.get_entropy(),
                'MD5': section.get_hash_md5(),
                'SHA2': section.get_hash_sha256()
            })
        return sections

    def get_imports(self):
        imports = []
        if hasattr(self.pe, 'DIRECTORY_ENTRY_IMPORT'):
            for dll in self.pe.DIRECTORY_ENTRY_IMPORT:
                import_data = {
                    'Name': self.whitespace_regex.sub('', dll.dll.decode(errors='replace')),
                    'Imports': []
                }
                for imported_function in dll.imports:
                    if imported_function.name is not None:
                        name = self.whitespace_regex.sub('', imported_function.name.decode(errors='replace'))
                    else:
                        name = '<UNDEFINED>'
                    import_data['Imports'].append(
                        {
                            'Address': imported_function.address,
                            'Name': name
                        }
                    )
                imports.append(import_data)

        return imports

    def get_debug_info(self):
        debug_info = []
        if hasattr(self.pe, 'DIRECTORY_ENTRY_DEBUG'):
            for debug_data in self.pe.DIRECTORY_ENTRY_DEBUG:
                if debug_data.entry and hasattr(debug_data.entry, 'Signature_Data1'):
                    guid = hex(debug_data.entry.Signature_Data1)[2:]
                    guid += '-' + hex(debug_data.entry.Signature_Data2)[2:]
                    guid += '-' + hex(debug_data.entry.Signature_Data3)[2:]
                    guid += '-' + hex(debug_data.entry.Signature_Data4)[2:]
                    guid += '-' + hex(debug_data.entry.Signature_Data5)[2:]
                    guid += hex(debug_data.entry.Signature_Data6)[2:]

                    debug_info.append(
                        {
                            "PDB": self.whitespace_regex.sub('', debug_data.entry.PdbFileName.decode(errors='replace')),
                            "GUID": guid
                        }
                    )
        return debug_info


if __name__ == '__main__':
    pe_parser = PEParser('/sample')
    data = pe_parser.get_summary_infos()
    print(json.dumps(data))
