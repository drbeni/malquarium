import json
import os
import shutil
import subprocess
from json.decoder import JSONDecodeError


def run_analyzer(analyzer, sample_path):
    docker_path = shutil.which('docker', mode=os.F_OK | os.X_OK, path=None)

    output = subprocess.check_output([
        docker_path,
        'run',
        '-v',
        sample_path + ':/sample:ro',
        analyzer.docker_image_name
    ])
    output = output.decode('utf-8')

    try:
        return json.loads(output)
    except JSONDecodeError:
        return {}
