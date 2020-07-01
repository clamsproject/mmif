import setuptools
import os
from os.path import join as pjoin
import shutil
import mmif  # this imports `mmif` directory as a sibling, not `mmif` site-package


def do_not_edit_warning(dirname):
    with open(pjoin(dirname, 'do-not-edit.txt'), 'w') as warning:
        warning.write("Contents of this directory is automatically generated and should not be manually edited.\n")
        warning.write("Any manual changes will be wiped at next build time.\n")


def generate_module(pack_name, mod_name, init_contents=""):
    mod_dir = pjoin(pack_name, mod_name)
    shutil.rmtree(mod_dir, ignore_errors=True)
    os.makedirs(mod_dir, exist_ok=True)
    do_not_edit_warning(mod_dir)
    mod_init = open(pjoin(mod_dir, '__init__.py'), 'w')
    mod_init.write(init_contents)
    mod_init.close()
    return mod_dir

# TODO (krim @ 6/30/20): this string value should be read from existing source (e.g. `VERSION` file)
# however, as SDK version is only partially bound to the MMIF "VERSION", need to come up with a separate source
version = '0.1.0'
generate_module(mmif.__name__, mmif._ver_pkg, f'__version__ = "{version}"')
# making resources into a python package so than `pkg_resources` can access resource files
res_dir = generate_module(mmif.__name__, mmif._res_pkg)

# TODO (krim @ 7/1/20): must be a better way to grasp these outside files...
schema_filename = pjoin(os.path.dirname(os.path.abspath(__file__)), '..', 'schema', 'mmif.json')
shutil.copy(schema_filename, pjoin(res_dir, mmif._schema_res_name))

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
    url="https://github.com/clamsproject/mmif-python",
    packages=setuptools.find_packages() ,
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
