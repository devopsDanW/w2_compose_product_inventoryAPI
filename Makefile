.PHONY: build security

CATALOGUE_IMAGE ?= catalogue-web
INVENTORY_IMAGE ?= inventory-api
TAG ?= latest

build:
	docker build -t $(CATALOGUE_IMAGE):$(TAG) catalogue-web/
	docker build -t $(INVENTORY_IMAGE):$(TAG) inventory-api/

security: build
	./security_gate.sh



