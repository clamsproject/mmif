"""

Script to collect MMIF specifications and generate source files for
publication as a github-page. Generated source files are located under
`docs/VERSION` directory where the actual version is taken from the `VERSION`
file in the project root.

When you use the default output directory and merge changes into the master
branch then the site at http://mmif.clams.ai/VERSION will be automatically
created or updated.

"""
import argparse
import json
import os
import shutil
import subprocess
import urllib.error
import warnings
from os.path import join as pjoin
from string import Template
from typing import Union, Dict, Optional, Set
from urllib import request

INCLUDE_CONTEXT = False


def copy(src_dir: str, dst_dir: str, include_fnames: Set = {}, exclude_fnames: Set = {}, templating: Dict = {}) -> None:
    for r, ds, fs in os.walk(src_dir):
        r = r[len(src_dir)+1:]
        for f in fs:
            if f.startswith('.') or r in exclude_fnames or f in exclude_fnames:
                continue
            elif not include_fnames or f in include_fnames:
                os.makedirs(pjoin(dst_dir, r), exist_ok=True)
                if templating and (f.endswith('.json') or f.endswith('.md')):
                    with open(pjoin(src_dir, r, f), 'r') as in_f, open(pjoin(dst_dir, r, f), 'w') as out_f:
                        tmpl_to_compile = Template(in_f.read())
                        compiled = tmpl_to_compile.safe_substitute(templating)
                        out_f.write(compiled)
                else:
                    shutil.copy(pjoin(src_dir, r, f), pjoin(dst_dir, r))


def check_version_exists(version: str):
    try:
        res = request.urlopen('https://api.github.com/repos/clamsproject/mmif/git/refs/tags')
        body = json.loads(res.read())
        tags = [os.path.basename(tag['ref']) for tag in body]
        if version in tags:
            raise RuntimeError(f"{version} already exists, can't overwrite an exising version.")
    except urllib.error.URLError:
        warnings.warn(f"Cannot connect to the remote repository.\n"
                      f"Now using local git tags to check version conflict.",
                      category=RuntimeWarning)
        proc = subprocess.run('git tag'.split(), cwd=os.path.abspath(os.path.dirname(__file__)), capture_output=True)
        if version in proc.stdout.decode('ascii').split('\n'):
            raise RuntimeError(f"{version} already exists, can't overwrite an exising version.")


def build(dirname, args):

    version = open(pjoin(dirname, 'VERSION')).read().strip()
    check_version_exists(version)
    out_dir = pjoin(dirname, args.testdir, version) if args.testdir else pjoin(dirname, 'docs', version)
    jekyll_conf_file = pjoin(dirname, 'docs', '_config.yml')
    spec_src_dir = pjoin(dirname, 'specifications')
    schema_src_dir = pjoin(dirname, 'schema')
    context_src_dir = pjoin(dirname, 'context')
    schema_out_dir = pjoin(out_dir, 'schema')
    shutil.rmtree(out_dir, ignore_errors=True)

    print("\n>>> Creating directory structure in '%s'" % out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("\n>>> Building specification in '%s'" % out_dir)
    build_spec(spec_src_dir, out_dir, version)

    print("\n>>> Building json schema in '%s'" % out_dir)
    build_schema(schema_src_dir, schema_out_dir, version)

    if INCLUDE_CONTEXT:
        # TODO: this is actually broken
        print("\n>>> Building json-ld context in '%s'" % out_dir)
        build_context(context_src_dir, out_dir, version)

    if args.testdir is None:
        print("\n>>> Updating jekyll configuration in '%s'" % jekyll_conf_file)
        update_jekyll_config(jekyll_conf_file, version)


def build_spec(src, dst, mmif_version):
    version_dict = {'VERSION': mmif_version}
    copy(src, dst, exclude_fnames={'next.md', 'notes', 'samples/others', 'samples/everything/scripts'}, templating=version_dict)


def build_schema(src, dst, version):
    copy(src, dst, include_fnames=['lif.json', 'mmif.json'])


def build_context(src, dst, version):
    copy(src, dst, exclude_fnames=['example.json'])


def update_jekyll_config(infname, version):
    outfname = infname + '.new'
    with open(infname) as config_f, \
            open(outfname, 'w') as out_f:
        new_version_line = f"    - {version}: '{version}'\n"
        lines = config_f.readlines()
        for i, line in enumerate(lines):
            out_f.write(line)
            if line == '  VERSIONS:\n':
                if lines[i+1] != new_version_line:
                    out_f.write(new_version_line)
    shutil.move(outfname, infname)


if __name__ == '__main__':

    dirname = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', dest="testdir", nargs="?", default=None, const='testbuild',
                        help='build version in test output directory')
    args = parser.parse_args()
    print(args)
    build(dirname, args)
