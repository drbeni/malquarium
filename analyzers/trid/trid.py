import json
import subprocess

EXECUTABLE = '/trid'

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
    data = []
    tag = None
    best_ending_match = None

    output = subprocess.check_output([
        EXECUTABLE,
        '/sample'
    ])
    output = output.decode('utf-8')
    first_match_found = False

    for line in output.split("\n"):
        line = line.strip()
        if line and line[0].isdecimal():
            result_parts = line.split(" ")

            match = result_parts[0].strip()
            ending = result_parts[1].strip()[1:-1]
            format_description = " ".join(result_parts[2:-1])

            if not first_match_found:
                best_ending_match = ending.lower().split('/')[0]

                if ending in ENDING_TAG_MAP:
                    tag = ENDING_TAG_MAP[ending]
                first_match_found = True

            data.append(
                {
                    "match": match,
                    "ending": ending,
                    "format": format_description
                }
            )

    output = {
        "data": data,
        "ending": best_ending_match
    }

    if tag is not None:
        output["tags"] = [tag]

    print(json.dumps(output))


if __name__ == '__main__':
    main()
