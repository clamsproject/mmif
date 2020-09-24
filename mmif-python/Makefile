# check for dependencies
deps = curl jq git python3 pytype pytest
check_deps := $(foreach dep,$(deps), $(if $(shell which $(dep)),some string,$(error "No $(dep) in PATH!")))

# constants
sdistname = mmif-python
bdistname = mmif_python

# helper functions
e :=
space := $(e) $(e)
## handling version numbers
macro = $(word 1,$(subst .,$(space),$(1)))
micro = $(word 2,$(subst .,$(space),$(1)))
patch = $(word 3,$(subst .,$(space),$(1)))
increase_patch = $(call macro,$(1)).$(call micro,$(1)).$$(($(call patch,$(1))+1))
## handling versioning for dev version
add_dev = $(call macro,$(1)).$(call micro,$(1)).$(call patch,$(1)).dev1
split_dev = $(word 2,$(subst .dev,$(space),$(1)))
increase_dev = $(call macro,$(1)).$(call micro,$(1)).$(call patch,$(1)).dev$$(($(call split_dev,$(1))+1))

.PHONY: all clean test develop testupload upload sdist version devversion

all: VERSION test build

develop: clean devversion test devsdist
	python3 setup.py develop --uninstall
	python3 setup.py develop
	twine upload --repository-url http://morbius.cs-i.brandeis.edu:8081/repository/pypi-develop/ \
		-u clamsuploader -p $$CLAMSUPLOADERPASSWORD dist/$(sdistname)-`cat VERSION`.tar.gz

testupload: distclean version test sdist
	twine upload --repository testpypi -u __token__ -p $$PYPITESTTOKEN dist/$(sdistname)-`cat VERSION`.tar.gz

upload: distclean version test sdist
	twine upload -u __token__ -p $$PYPITOKEN dist/$(sdistname)-`cat VERSION`.tar.gz

sdist: dist/$(sdistname)-*.tar.gz
dist/$(sdistname)-*.tar.gz: VERSION; python3 setup.py sdist
devsdist: dist/$(sdistname)-*.dev*.tar.gz
dist/$(sdistname)-*.dev*.tar.gz: devversion dist/$(sdistname)-*.tar.gz

build: build/lib/mmif

build/lib/mmif:
	python3 setup.py build

# invoking `test` without a VERSION file will generated a dev version - this ensures `make test` runs unmanned
test: devversion build
	pytype mmif/
	python3 -m pytest --doctest-modules --cov=mmif

devversion: VERSION.dev VERSION; cat VERSION
version: VERSION; cat VERSION

VERSION.dev: upstreamver := $(shell curl -s -X GET 'http://morbius.cs-i.brandeis.edu:8081/service/rest/v1/search?name=$(sdistname)' | jq '. | .items[].version' -r | sort | tail -n 1)
VERSION.dev:
	@if [[ $(upstreamver) == *.dev* ]]; then echo $(call increase_dev,$(upstreamver)) ; else echo $(call add_dev,$(call increase_patch, $(upstreamver))); fi > VERSION.dev

VERSION: version := $(shell git tag | grep py- | cut -d'-' -f 2 | sort -r | head -n 1)
VERSION:
	@if [ -e VERSION.dev ] ; \
	then cp VERSION.dev VERSION; \
	else (read -p "Current version is ${version}, please enter a new version (default: increase *patch* level by 1): " new_ver; \
		[ -z $$new_ver ] && echo $(call increase_patch,$(version)) || echo $$new_ver) > VERSION; \
	fi

distclean:
	@rm -rf dist
clean: distclean
	@rm -rf VERSION VERSION.dev build/lib/mmif $(bdistname).egg-info mmif/res mmif/ver mmif/vocabulary \
	.pytest_cache .pytype coverage.xml htmlcov
