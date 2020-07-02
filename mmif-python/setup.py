from typing import Union

import setuptools
import os
from os.path import join as pjoin
# TODO (krim @ 7/2/20): how can we install this (pip install gitpython) for devs before running setup.py
import git
import shutil
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


def get_matching_gittag(repo: git.Repo, version: str):
    vmaj, vmin, vpat = version.split('.')
    return sorted([tag for tag in repo.tags if f'{vmaj}.{vmin}.' in tag.name], key=lambda x: int(x.name.split('.')[-1]))[-1]


def get_file_contents_at_tag(repo: git.Repo, tag: git.Tag, filepath: str) -> bytes:
    blob = tag.commit.tree[filepath]
    blobcontents = blob.data_stream
    return blobcontents.read()


def write_res_file(res_dir: str, res_name: str, res_data: Union[bytes, str]):
    open_ops = 'wb' if type(res_data) == bytes else 'w'
    res_file = open(pjoin(res_dir, res_name), open_ops)
    res_file.write(res_data)
    res_file.close()


# TODO (krim @ 6/30/20): this string value should be read from existing source (e.g. `VERSION` file)
# however, as SDK version is only partially bound to the MMIF "VERSION", need to come up with a separate source
version = '0.1.0'
generate_subpack(mmif.__name__, mmif._ver_pkg, f'__version__ = "{version}"')
# making resources into a python package so than `pkg_resources` can access resource files
res_dir = generate_subpack(mmif.__name__, mmif._res_pkg)

# assuming build only happens inside the `mmif` git repository
# read git repository
cwds = os.getcwd().split(os.sep)
while not os.path.exists('/'+pjoin(*cwds, '.git')):
    cwds.pop()
gitrepo = git.Repo('/'+pjoin(*cwds))
gittag = get_matching_gittag(gitrepo, version)

# and write resource files
write_res_file(res_dir, mmif._schema_res_name, get_file_contents_at_tag(gitrepo, gittag, mmif._schema_res_oriname))
write_res_file(res_dir, mmif._schema_vocab_name, get_file_contents_at_tag(gitrepo, gittag, mmif._schema_vocab_oriname))

with open('README.md') as readme:
    long_desc = readme.read()

with open('requirements.txt') as requirements:
    requires = requirements.readlines()


setuptools.setup(
    name="mmif-python", 
    version=version,
    author="Brandeis Lab for Linguistics and Computation", 
    author_email="admin@clams.ai",
    description="Python implementation of MultiMedia Interchange Format specification. (https://mmif.clams.ai)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://mmif.clams.ai",
    packages=setuptools.find_packages(),
    install_requires=requires,
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov', 
            'gitpython'
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
