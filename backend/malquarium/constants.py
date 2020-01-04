import re

SHA256_PATTERN = re.compile('^[a-f0-9]{64}$')
SHA1_PATTERN = re.compile('^[a-f0-9]{40}$')
MD5_PATTERN = re.compile('^[a-f0-9]{32}$')
SSDEEP_PATTERN = re.compile('^\d+:[^:]+:[^:]+$')
EMAIL_PATTERN = re.compile(
    "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
