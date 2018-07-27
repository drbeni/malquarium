import json
import re
import subprocess

from json.decoder import JSONDecodeError

EXECUTABLE = "/usr/bin/exiftool"


def main():
    output = subprocess.check_output([EXECUTABLE, '-G', '-j', '-n', '/sample'])
    output = output.decode('utf-8')

    try:
        json_data = json.loads(output, encoding='utf-8')[0]
    except JSONDecodeError:
        print('{}')
        return

    result = {}
    for key in json_data:
        if not (key in ('SourceFile', 'ExifTool:ExifToolVersion') or key.startswith("File:")):
            # special treatment for things like
            # "FlashPix:Tag_PID_GUID": "{\u00008\u00003\u00003\u00002\u00007\u00005\u0000C\u00001\u0000-\u0000A
            # \u0000D\u00000\u0000D\u0000-\u00001\u00001\u0000D\u00005\u0000-\u00008\u0000C\u0000B\u00008\u0000-
            # \u00005\u00002\u00005\u00004\u00000\u00000\u0000E\u0000C\u00007\u00004\u00003\u00009\u0000}\u0000
            # \u0000\u0000",

            if type(json_data[key]) == str and '\u0000' in json_data[key]:
                alpha_numeric_dash = re.compile(r'[^0-9a-zA-Z-]+')
                result[key] = alpha_numeric_dash.sub('', ''.join([s for s in json_data[key] if s != '\x00']))
            else:
                result[key] = json_data[key]

    print(json.dumps(result))


if __name__ == '__main__':
    main()
