import json
import subprocess

EXECUTABLE = '/trid'


def main():
    data = []

    output = subprocess.check_output([
        EXECUTABLE,
        '/sample'
    ])
    output = output.decode('utf-8')
    for line in output.split("\n"):
        line = line.strip()
        if line and line[0].isdecimal():
            result_parts = line.split(" ")
            data.append(
                {
                    "match": result_parts[0].strip(),
                    "ending": result_parts[1].strip()[1:-1],
                    "format": " ".join(result_parts[2:-1])
                }
            )

    print(json.dumps(data))


if __name__ == '__main__':
    main()
