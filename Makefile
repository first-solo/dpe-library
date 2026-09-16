IMAGE := dpe-library
RUN := docker run --rm -v "$(CURDIR)":/work -w /work $(IMAGE)

.PHONY: help image build check fetch updates updates-write shell clean

help:
	@echo "make build          regenerate README.md, site/index.json, and local/ private view"
	@echo "make check          validate the catalog and confirm tracked output is current"
	@echo "make fetch          download PDFs into local/pdfs/ (gitignored)"
	@echo "make updates        check every entry against its upstream source"
	@echo "make updates-write  same, and write new hashes and last_checked into the catalog"
	@echo "make shell          drop into the container"

image:
	@docker image inspect $(IMAGE) >/dev/null 2>&1 || docker build -q -t $(IMAGE) .

build: image
	$(RUN) python scripts/build.py

check: image
	$(RUN) python scripts/build.py --check

fetch: image
	$(RUN) python scripts/fetch.py

updates: image
	$(RUN) python scripts/check_updates.py

updates-write: image
	$(RUN) python scripts/check_updates.py --write
	$(MAKE) build

shell: image
	docker run --rm -it -v "$(CURDIR)":/work -w /work $(IMAGE) bash

clean:
	rm -rf local/ site/index.json
