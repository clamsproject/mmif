#! /usr/bin/env python3
import os
import shutil
import subprocess
import importlib
import sys
from os.path import join as pjoin
from typing import Union

import setuptools.command.build_py
import setuptools.command.develop

import mmif  # this imports `mmif` directory as a sibling, not `mmif` site-package


def do_not_edit_warning(dirname):
    with open(pjoin(dirname, 'do-not-edit.txt'), 'w') as warning:
        warning.write("Contents of this directory is automatically generated and should not be manually edited.\n")
        warning.write("Any manual changes will be wiped at next build time.\n")


def generate_subpack(pack_name, mod_name, init_contents=""):
    mod_dir = pjoin(pack_name, mod_name)
    shutil.rmtree(mod_dir, ignore_errors=True)
    os.makedirs(mod_dir, exist_ok=True)
    do_not_edit_warning(mod_dir)
    mod_init = open(pjoin(mod_dir, '__init__.py'), 'w')
    mod_init.write(init_contents)
    mod_init.close()
    return mod_dir


def get_matching_gittag(version: str):
    vmaj, vmin, vpat = version.split('.')[0:3]
    tags = subprocess.check_output(['git', 'tag']).decode().split('\n')
    # sort and return highest version
    return \
        sorted([tag for tag in tags if f'{vmaj}.{vmin}.' in tag],
               key=lambda x: int(x.split('.')[-1]))[-1]


def get_file_contents_at_tag(tag, filepath: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{tag}:{filepath}'])


def write_res_file(res_dir: str, res_name: str, res_data: Union[bytes, str]):
    open_ops = 'wb' if type(res_data) == bytes else 'w'
    res_file = open(pjoin(res_dir, res_name), open_ops)
    res_file.write(res_data)
    res_file.close()

def dev_ver(ver, devver=1):
    vmaj, vmac, vpat = map(int, ver.split('.'))
    return '.'.join(map(str, [vmaj, vmac, vpat+1, f'dev{devver}']))

def bump_ver(ver):
    new_ver = input(f"Current version is {ver}, please enter new version (default: increase *patch* level by 1): ")
    if len(new_ver) == 0:
        vmaj, vmac, vpat = map(int, ver.split('.'))
        new_ver = '.'.join(map(str, [vmaj, vmac, vpat+1]))
    return new_ver

# note that `VERSION` file is not included in bdist - bdist should alreay have `mmif._ver_pkg` properly set
with open('VERSION', 'r') as version_f:
    version = version_f.read().strip()
    if 'develop' in sys.argv:
        version = dev_ver(version)
    elif 'bump' in sys.argv:
        version = bump_ver(version)
        sys.argv.remove('bump')
# the above will generate a new __version__ value based on VERSION file
# but as `mmif` package is already imported at the top,
# mmif.__version__ is not updated, so we need to reload the package
generate_subpack(mmif.__name__, mmif._ver_pkg, f'__version__ = "{version}"')
importlib.reload(mmif)

def prep_ext_files(setuptools_cmd):
    ori_run = setuptools_cmd.run

    def mod_run(self):
        # assuming build only happens inside the `mmif` git repository
        gittag = get_matching_gittag(version)
        # making resources into a python package so that `pkg_resources` can access resource files
        res_dir = generate_subpack(mmif.__name__, mmif._res_pkg)
        # and write resource files
        write_res_file(res_dir, mmif._schema_res_name, get_file_contents_at_tag(gittag, mmif._schema_res_oriname))
        write_res_file(res_dir, mmif._vocab_res_name, get_file_contents_at_tag(gittag, mmif._vocab_res_oriname))
        ori_run(self)

    setuptools_cmd.run = mod_run
    return setuptools_cmd


@prep_ext_files
class SdistCommand(setuptools.command.sdist.sdist):
    pass


with open('README.md') as readme:
    long_desc = readme.read()

with open('requirements.txt') as requirements:
    requires = requirements.readlines()

setuptools.setup(
    name="mmif-python",
    version=mmif.__version__,
    author="Brandeis Lab for Linguistics and Computation",
    author_email="admin@clams.ai",
    description="Python implementation of MultiMedia Interchange Format specification. (https://mmif.clams.ai)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://mmif.clams.ai",
    packages=setuptools.find_packages(),
    cmdclass={
        'sdist': SdistCommand,
    },
    install_requires=requires,
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
            'pytype',
        ]
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers ',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
