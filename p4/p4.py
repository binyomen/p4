import argparse
import distutils.dir_util
import os
import re
import subprocess
import tempfile

import p4

def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Preprocess a Processing source file.')
    parser.add_argument('source_dir', metavar='source_dir', type=str, help='the directory of the source files')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = copy_source(args.source_dir, temp_dir)
        preprocess_source(package_dir)
        subprocess.call(["processing-java", "--sketch=" + package_dir, "--run"])


def copy_source(src, dest):
    # copy the user-produced source
    package_name = os.path.basename(os.path.normpath(os.path.abspath(src)))
    package_dir = os.path.join(dest, package_name)
    distutils.dir_util.copy_tree(src, package_dir)

    # copy the p4 libraries
    distutils.dir_util.copy_tree(p4.INC_DIR, package_dir)

    return package_dir


def preprocess_source(source_dir):
    for filename in os.listdir(source_dir):
        if filename.endswith(".pde"):
            with open(os.path.join(source_dir, filename), 'r+') as f:
                new_lines = []
                for line in f:
                    new_line = line
                    new_line = preprocess_hash_comments(new_line)
                    new_lines.append(new_line)
                f.seek(0)
                for line in new_lines:
                    f.write(line)
                f.truncate()


def preprocess_hash_comments(line):
    return re.sub('//##', '', line)
