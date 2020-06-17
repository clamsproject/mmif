import setuptools

with open('README.md') as readme:
    long_desc = readme.read()

setuptools.setup(
    name="mmif-python", 
    version="0.0.1",
    author="Brandeis Lab for Linguistics and Computation", 
    author_email="admin@clams.ai",
    description="Python implementation of MultiMedia Interchange Format specification. (https://mmif.clams.ai)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/clamsproject/mmif-python",
    packages=setuptools.find_packages() ,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers ',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        ],
)
