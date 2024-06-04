GIT_VERSION ?= 2.40.1

##@ Container build tasks
.PHONY: help
help: ## This help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^(\s|[a-zA-Z_0-9-])+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: build
build: ## Build the container locally
	@echo "Building the git container"
	buildah bud --format docker -f Containerfile -t gitsubtree-container:$(GIT_VERSION) --build-arg GIT_VERSION=$(GIT_VERSION)

.PHONY: upload
upload: build ## Builds and then uploads the container to quay.io/hybridcloudpatterns/gitsubtree-container:latest
	@echo "Uploading the container to quay.io/hybridcloudpatterns/gitsubtree-container $(GIT_VERSION)"
	buildah push localhost/gitsubtree-container:$(GIT_VERSION) quay.io/hybridcloudpatterns/gitsubtree-container:$(GIT_VERSION)

.PHONY: run
run: ## Run the local container
	podman run -it --rm --net=host localhost/gitsubtree-container:$(GIT_VERSION)

.PHONY: super-linter
super-linter: ## Runs super linter locally
	podman run -e RUN_LOCAL=true -e USE_FIND_ALGORITHM=true	\
					-e VALIDATE_DOCKERFILE_HADOLINT=true \
					$(DISABLE_LINTERS) \
					-v $(PWD):/tmp/lint:rw,z \
					-w /tmp/lint \
					ghcr.io/super-linter/super-linter:slim-v6
