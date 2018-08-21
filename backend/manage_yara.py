#!/usr/bin/env python3
import os
import sys
import yara

YARA_RULES_PATH = 'tools/yara'
YARA_SAVE_PATH = 'backend/utils/yara_scanner'
USAGE = 'manage_yara.py <generate|compile>'


def compile():
    for yarb in os.listdir(YARA_SAVE_PATH):
        if yarb.endswith('yarb'):
            os.remove(os.path.join(YARA_SAVE_PATH, yarb))

    for yara_file in os.listdir(YARA_RULES_PATH):
        yara_file_path = os.path.join(YARA_RULES_PATH, yara_file)
        if os.path.isfile(yara_file_path) and yara_file.endswith('.yar'):
            print("Compiling {}".format(os.path.join(YARA_SAVE_PATH, yara_file.rstrip('yar') + 'yarb')))
            rules = yara.compile(yara_file_path)
            rules.save(os.path.join(YARA_SAVE_PATH, yara_file.rstrip('yar') + 'yarb'))


def generate_index():
    for rules_dir in os.listdir(YARA_RULES_PATH):
        dir_path = os.path.join(YARA_RULES_PATH, rules_dir)
        if os.path.isdir(dir_path):
            with open(os.path.join(YARA_RULES_PATH, rules_dir + '_index.yar'), 'w') as f:
                for yara_rule in os.listdir(dir_path):
                    yara_rule_path = os.path.join(dir_path, yara_rule)
                    if os.path.isfile(yara_rule_path):
                        f.write('include ".{}"\n'.format(yara_rule_path.split(YARA_RULES_PATH)[1]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(USAGE)
        exit(1)

    if sys.argv[1].lower().startswith('c'):
        compile()
    elif sys.argv[1].lower().startswith('g'):
        generate_index()
