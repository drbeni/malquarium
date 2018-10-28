import re

SHA256_PATTERN = re.compile('^[a-f0-9]{64}$')
SHA1_PATTERN = re.compile('^[a-f0-9]{40}$')
MD5_PATTERN = re.compile('^[a-f0-9]{32}$')
SSDEEP_PATTERN = re.compile('^\d+:[^:]+:[^:]+$')
