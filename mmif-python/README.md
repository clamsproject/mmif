# MMIF for python 

**NOTE** that this project is in pre-alpha and being actively developed. Nothing is guaranteed to reliably work for the moment and developer need to be very careful when using APIs implemented here. Please use [the issue track](../../issues) to report bugs and malfunctions.

## MultiMedia Interchange Format
[MMIF](htts://mmif.clams.ai) is a JSON-LD based data format designed for transfer annotation data between computational analysis applications in [CLAMS project](https://www.clams.ai). 

## Installation: 
Package `mmif-python` is distributed via the official pypi. Users are supposed to pip-install to get latest release. 
```
pip install mmif-python
```
This will install a packge `mmif` to local python. 

## For SDK developers 
There is [`Makefile`](Makefile) that can be used to test, build and publish this SDK package. Two primary targets are defined for 
* `develop` - test, build, and install packages locally in [development mode](https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode). In doing so, a development version is automatically generated and used. 
  * This target will try to upload a source distribution of the dev version to our private pypi. 
  * Also note that while building, it will copy some MMIF specification files from the `HEAD` commit and include them in the built artifact. This is intended for testing purpose. 
* `publish` - test, build, and publish [a source distribution](https://python-packaging-tutorial.readthedocs.io/en/latest/uploading_pypi.html#source-distribution) to the official pypi. 
  * In doing so, it `make` will ask the user for a new version number. 
  * Unlike `develop` target, this process will copy MMIF specification files from the latest matching git tag. See [versioning](https://github.com/clamsproject/mmif/blob/master/specifications/index.md#versioning) section of the MMIF specification for more details. 

## APIs

TBD
