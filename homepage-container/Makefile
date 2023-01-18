.PHONY: help
# No need to add a comment here as help is described in common/
help:
	@printf "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)\n"

.PHONY: build
build: ## Build the container locally
	@echo "Building the homepage container"
	buildah bud --format docker -f Containerfile -t homepage-container

.PHONY: upload
upload: build ## Builds and then uploads the container to quay.io/hybridcloudpatterns/homepage-container:latest
	@echo "Uploading the container to quay.io/hybridcloudpatterns/homepage-container latest"
	buildah push localhost/homepage-container:latest quay.io/hybridcloudpatterns/homepage-container:latest
