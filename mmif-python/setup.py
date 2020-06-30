import setuptools
import os

with open('README.md') as readme:
    long_desc = readme.read()

with open('requirements.txt') as requirements:
    requires = requirements.readlines()

# TODO (krim @ 6/30/20): this string value should be read from existing source (e.g. `VERSION` file)
# however, as SDK version is only partially bound to the MMIF "VERSION", need to come up with a separate source
version = '0.1.0'
with open(os.path.join('mmif', 'version', '__init__.py'), 'w') as version_file:
    version_file.write(f'__version__ = "{version}"')

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
