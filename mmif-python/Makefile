comma := ,
empty := 
space := $(empty) $(empty)
macro = $(word 1,$(subst .,$(space),$(1)))
micro = $(word 2,$(subst .,$(space),$(1)))
patch = $(word 3,$(subst .,$(space),$(1)))
patchinc = $(call macro,$(1)).$(call micro,$(1)).$$(($(call patch,$(1))+1))
dev = $(word 2,$(subst -dev,$(space),$(1)))
devinc = $(call macro,$(1)).$(call micro,$(1)).$(call patch,$(1)).dev$$(($(call dev,$(1))+1))
devadd = $(call macro,$(1)).$(call micro,$(1)).$(call patch,$(1)).dev1

.PHONY: devver clean VERSION.dev

devver: clean VERSION.dev
	cat VERSION

VERSION.dev: devver := $(shell curl -s -X GET 'http://morbius.cs-i.brandeis.edu:8081/service/rest/v1/search?name=mmif-python' | jq '. | .items[].version' -r | sort | tail -n 1)
VERSION.dev:
ifeq ($(findstring .dev,$(devver)),)
	@echo $(call devadd,$(devver)) > VERSION
else
	@echo $(call devinc,$(devver)) > VERSION
endif

version: VERSION
	cat VERSION

VERSION: version := $(shell git tag | grep py- | cut -d'-' -f 2 | sort -r | head -n 1)
VERSION:
	@(read -p "Current version is ${version}, please enter a new version (default: increase *patch* level by 1): " new_ver; \
	[ -z $$new_ver ] && echo $(call patchinc,$(version)) || echo $$new_ver) > VERSION;

clean: 
	@rm -rf VERSION VERSION.dev build dist mmif_python.egg-info
