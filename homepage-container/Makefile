HUGO_VERSION ?= 0.133.1
NAME ?= homepage-container
TAG ?= latest
CONTAINER ?= $(NAME):$(TAG)
REGISTRY ?= localhost
UPLOADREGISTRY ?= quay.io/validatedpatterns

TESTCOMMAND := "set -e; echo '* Hugo version: '; hugo version ;"

##@ Container build tasks
.PHONY: help
help: ## This help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^(\s|[a-zA-Z_0-9-])+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: build
build: manifest podman-build test ## Build the container locally (all arches) and print installed test

.PHONY: amd64
amd64: manifest podman-build-amd64 test-amd64 ## Build and test the container on amd64

.PHONY: arm64
arm64: manifest podman-build-amd64 test-amd64 ## Build and test the container on amd64

.PHONY: manifest
manifest: ## creates the buildah manifest for multi-arch images
	# The rm is needed due to bug https://www.github.com/containers/podman/issues/19757
	buildah manifest rm "${REGISTRY}/${CONTAINER}" || /bin/true
	buildah manifest create "${REGISTRY}/${CONTAINER}"

.PHONY: podman-build
podman-build: podman-build-amd64 podman-build-arm64 ## Build both amd64 and arm64

.PHONY: podman-build-amd64
podman-build-amd64: ## build the container in amd64
	@echo "Building the utility container amd64"
	buildah bud --arch=amd64 --build-arg TARGETARCH=amd64 --build-arg ALTTARGETARCH=x86_64 \
		--build-arg HUGO_VERSION=$(HUGO_VERSION) --format docker \
		-f Containerfile -t "${CONTAINER}-amd64"
	buildah manifest add --arch=amd64 "${REGISTRY}/${CONTAINER}" "${REGISTRY}/${CONTAINER}-amd64"

.PHONY: podman-build-arm64
podman-build-arm64: ## build the container in arm64
	@echo "Building the utility container arm64"
	buildah bud --arch=arm64 --build-arg TARGETARCH=arm64 --build-arg ALTTARGETARCH=aarch64 \
		--build-arg HUGO_VERSION=$(HUGO_VERSION) --format docker \
		-f Containerfile -t "${CONTAINER}-arm64"
	buildah manifest add --arch=arm64 "${REGISTRY}/${CONTAINER}" "${REGISTRY}/${CONTAINER}-arm64"

.PHONY: test
test: test-amd64 test-arm64 ## Tests the container for all the required bits both arm64 and amd64

.PHONY: test-amd64
test-amd64: ## Prints the test of most tools inside the container amd64
	@echo "** Testing linux/amd64"
	@podman run --arch=amd64 --rm -it --net=host --entrypoint /bin/bash "${REGISTRY}/${CONTAINER}-amd64" -c $(TESTCOMMAND)

.PHONY: test-arm64
test-arm64: ## Prints the test of most tools inside the container arm64
	@echo "** Testing linux/arm64"
	@podman run --arch=arm64 --rm -it --net=host --entrypoint /bin/bash "${REGISTRY}/${CONTAINER}-arm64" -c $(TESTCOMMAND)

.PHONY: upload
upload: ## Uploads the container to quay.io/validatedpatterns/homepage-container:latest
	@echo "Uploading the ${REGISTRY}/${CONTAINER} container to ${UPLOADREGISTRY}/${CONTAINER}"
	buildah manifest push --all "${REGISTRY}/${CONTAINER}" "docker://${UPLOADREGISTRY}/${CONTAINER}"

.PHONY: run
run: ## Run the local container
	podman run -it --rm --net=host $(REGISTRY)/$(CONTAINER)

.PHONY: super-linter
super-linter: ## Runs super linter locally
	podman run -e RUN_LOCAL=true -e USE_FIND_ALGORITHM=true	\
					-e VALIDATE_DOCKERFILE_HADOLINT=true \
					$(DISABLE_LINTERS) \
					-v $(PWD):/tmp/lint:rw,z \
					-w /tmp/lint \
					ghcr.io/super-linter/super-linter:slim-v7
