import os
import yara

from backend.utils.yara_scanner.formatter import format_malice
from malquarium.settings import YARA_COLLECTIONS


class YaraScanner:
    rule_collections = []

    def __init__(self):
        for collection in YARA_COLLECTIONS:
            self.rule_collections.append(
                YaraRuleCollection(
                    os.path.join('backend', 'utils', 'yara_scanner', collection + '.yarb'),
                    format_malice if collection.startswith('malice') else None
                )
            )

    def scan(self, input_file):
        for rule_collection in self.rule_collections:
            for match in rule_collection.scan(input_file):
                yield match.replace(' ', '_').lower()


class YaraRuleCollection:
    def __init__(self, compiled_rules, output_formatter=None, timeout=30):
        try:
            self.rules = yara.load(compiled_rules)
        except Exception as e:
            raise YaraLoadException(e) from e

        self.output_formatter = output_formatter
        self.timeout = timeout

    def scan(self, input_file):
        try:
            for match in self.rules.match(input_file, timeout=self.timeout):
                if self.output_formatter:
                    yield self.output_formatter(match)
                else:
                    yield match.rule

        except TimeoutError as e:
            pass


class YaraLoadException(Exception):
    pass
