#! /usr/bin/env python3
import io
import os
import shutil
import subprocess
from os.path import join as pjoin
from typing import Union

import setuptools.command.build_py
import setuptools.command.develop


name = "mmif-python"
version_fname = "VERSION"
cmdclass = {}

# Used to have `import mmif` that imported `mmif` directory as a sibling, not `mmif` site-package,
# but that created a circular dependency (importing `mmif` requires packages in "requirements.txt")
# so we copy or move relevant package level variables used in the pre-build stage to here
mmif_name = "mmif"
mmif_res_pkg = 'res'
mmif_ver_pkg = 'ver'
mmif_vocabulary_pkg = 'vocabulary'
mmif_schema_res_oriname = 'schema/mmif.json'
mmif_schema_res_name = 'mmif.json'
mmif_vocab_res_oriname = 'vocabulary/clams.vocabulary.yaml'
mmif_vocab_res_name = 'clams.vocabulary.yaml'

try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    print('WARNING: sphinx not available, not building docs')


def do_not_edit_warning(dirname):
    with open(pjoin(dirname, 'do-not-edit.txt'), 'w') as warning:
        warning.write("Contents of this directory is automatically generated and should not be manually edited.\n")
        warning.write("Any manual changes will be wiped at next build time.\n")


def generate_subpack(parpack_name, subpack_name, init_contents=""):
    subpack_dir = pjoin(parpack_name, subpack_name)
    shutil.rmtree(subpack_dir, ignore_errors=True)
    os.makedirs(subpack_dir, exist_ok=True)
    do_not_edit_warning(subpack_dir)
    init_mod = open(pjoin(subpack_dir, '__init__.py'), 'w')
    init_mod.write(init_contents)
    init_mod.close()
    return subpack_dir


def generate_vocab_enum(spec_version, clams_types, source_path) -> str:
    vocab_url = 'http://mmif.clams.ai/%s/vocabulary' % spec_version

    file_out = io.StringIO()
    with open(source_path, 'r') as file_in:
        for line in file_in.readlines():
            file_out.write(line.replace('<VERSION>', spec_version))
        for type_name in clams_types:
            file_out.write(f"    {type_name} = '{vocab_url}/{type_name}'\n")

    string_out = file_out.getvalue()
    file_out.close()
    return string_out


def generate_vocabulary(spec_version, clams_types, source_path):
    """
    :param spec_version:
    :param clams_types: the tree
    :param source_path: the directory of source txt files
    :return:
    """
    types = {
        'thing_types': ['ThingTypesBase', 'ThingType'],
        'annotation_types': ['AnnotationTypesBase', 'AnnotationTypes'],
        'document_types': ['DocumentTypesBase', 'DocumentTypes']
    }
    vocabulary_dir = generate_subpack(
        mmif_name, mmif_vocabulary_pkg,
        '\n'.join(
            f"from .{mod_name} import {class_name}"
            for mod_name, classes in types.items()
            for class_name in classes
        )+'\n'
    )

    type_lists = {
        # extract document types (hacky for now, improve later)
        'document_types': [t for t in clams_types if 'Document' in t],

        # extract annotation types
        'annotation_types': [t for t in clams_types if 'Document' not in t and t != 'Thing'],

        # extract thing type
        'thing_types': clams_types[:1]
    }

    for mod_name, type_list in type_lists.items():
        enum_contents = generate_vocab_enum(spec_version, type_list, os.path.join(source_path, mod_name+'.txt'))
        write_res_file(vocabulary_dir, mod_name+'.py', enum_contents)

    return vocabulary_dir


def get_matching_gittag(version: str):
    vmaj, vmin, vpat = version.split('.')[0:3]
    tags = subprocess.check_output(['git', 'tag']).decode().split('\n')
    # sort and return highest version
    return \
        sorted([tag for tag in tags if f'spec-{vmaj}.{vmin}.' in tag],
               key=lambda x: int(x.split('.')[-1]))[-1]


def get_file_contents_at_tag(tag, filepath: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{tag}:{filepath}'])


def write_res_file(res_dir: str, res_name: str, res_data: Union[bytes, str]):
    open_ops = 'wb' if type(res_data) == bytes else 'w'
    res_file = open(pjoin(res_dir, res_name), open_ops)
    res_file.write(res_data)
    res_file.close()


# note that `VERSION` file will not included in s/bdist - s/bdist should already have `mmif_ver_pkg` properly generated
if os.path.exists(version_fname):
    with open(version_fname, 'r') as version_f:
        version = version_f.read().strip()
else:
    raise ValueError(f"Cannot find {version_fname} file. Use `make version` to generate one.")


def prep_ext_files(setuptools_cmd):
    ori_run = setuptools_cmd.run

    def mod_run(self):
        # assuming build only happens inside the `mmif` git repository
        # also, NOTE that when in `make develop`, it will use resource files in the same branch
        gittag = get_matching_gittag(version) if '.dev' not in version else "HEAD"
        spec_version = gittag.split('-')[-1]
        # making resources into a python package so that `pkg_resources` can access resource files
        res_dir = generate_subpack(mmif_name, mmif_res_pkg)

        # the following will generate a new version value based on VERSION file
        generate_subpack(mmif_name, mmif_ver_pkg, f'__version__ = "{version}"\n__specver__ = "{spec_version}"')

        # and write resource files
        write_res_file(res_dir, mmif_schema_res_name, get_file_contents_at_tag(gittag, mmif_schema_res_oriname))
        write_res_file(res_dir, mmif_vocab_res_name, get_file_contents_at_tag(gittag, mmif_vocab_res_oriname))

        # write vocabulary enum
        import yaml
        yaml_file = io.BytesIO(get_file_contents_at_tag(gittag, mmif_vocab_res_oriname))
        clams_types = [t['name'] for t in list(yaml.safe_load_all(yaml_file.read()))]
        generate_vocabulary(spec_version, clams_types, 'vocabulary_files')

        ori_run(self)

    setuptools_cmd.run = mod_run
    return setuptools_cmd


@prep_ext_files
class SdistCommand(setuptools.command.sdist.sdist):
    pass


@prep_ext_files
class DevelopCommand(setuptools.command.develop.develop):
    pass


cmdclass['sdist'] = SdistCommand
cmdclass['develop'] = DevelopCommand

with open('README.md') as readme:
    long_desc = readme.read()

with open('requirements.txt') as requirements:
    requires = requirements.readlines()

setuptools.setup(
    name=name,
    version=version,
    author="Brandeis Lab for Linguistics and Computation",
    author_email="admin@clams.ai",
    description="Python implementation of MultiMedia Interchange Format specification. (https://mmif.clams.ai)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://mmif.clams.ai",
    packages=setuptools.find_packages(),
    cmdclass=cmdclass,
    # this is for *building*, building (build, bdist_*) doesn't get along with MANIFEST.in
    # so using this param explicitly is much safer implementation
    package_data={
        'mmif': [f'{mmif_res_pkg}/*', f'{mmif_ver_pkg}/*', f'{mmif_vocabulary_pkg}/*'],
    },
    install_requires=requires,
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
            'pytype',
            'sphinx'
        ]
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers ',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    command_options={
        'build_sphinx': {
            #  'source_dir': ('setup.py', 'doc'), 
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            #  'release': ('setup.py', release),
            'build_dir': ('setup.py', '_build'),
            'builder': ('setup.py', 'html'),
            }
        }
)
