##@ Utilities Common Tasks

.PHONY: help
help: ## This help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^(\s|[a-zA-Z_0-9-])+:.*?##/ { printf "  \033[36m%-35s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: super-linter
super-linter: ## Runs super linter locally
	rm -rf .mypy_cache
	podman run -e RUN_LOCAL=true -e USE_FIND_ALGORITHM=true	\
					-e VALIDATE_ANSIBLE=false \
					-e VALIDATE_BASH=false \
					-e VALIDATE_DOCKERFILE_HADOLINT=false \
					-e VALIDATE_JSCPD=false \
					-e VALIDATE_KUBERNETES_KUBECONFORM=false \
					-e VALIDATE_PYTHON_BLACK=false \
					-e VALIDATE_PYTHON_FLAKE8=false \
					-e VALIDATE_PYTHON_ISORT=false \
					-e VALIDATE_PYTHON_MYPY=false \
					-e VALIDATE_PYTHON_PYLINT=false \
					-e VALIDATE_YAML=false \
					$(DISABLE_LINTERS) \
					-v $(PWD):/tmp/lint:rw,z \
					-w /tmp/lint \
					docker.io/github/super-linter:slim-v5

.PHONY: ansible-lint
ansible-lint: ## run ansible lint on ansible/ folder
	podman run -it -v $(PWD):/workspace:rw,z --workdir /workspace \
		--entrypoint "/usr/local/bin/ansible-lint" quay.io/ansible/creator-ee:latest  "-vvv" "acm_import/"

##### HostedCluster Management tasks
REGISTRY ?= quay.io/hybridcloudpatterns
NAME ?= utility-container
TAG ?= latest
CONTAINER ?= $(NAME):$(TAG)

.PHONY: cluster-status
cluster-status: ## Checks the status of hostedcluster machines
	@echo "Getting status of hosted-cluster nodes"
	podman run --rm --net=host  \
	  --security-opt label=disable \
		-v ${HOME}:/pattern \
		-v ${HOME}:${HOME} \
		-v ${HOME}/.aws:/pattern-home/.aws \
		"${REGISTRY}/${CONTAINER}"  python3 /usr/local/bin/status-instances.py -f ${CLUSTER}

.PHONY: cluster-start
cluster-start: ## Starts the ostedcluster machines
	@echo "Starting hosted-cluster nodes"
	podman run --rm --net=host  \
	  --security-opt label=disable \
		-v ${HOME}:/pattern \
		-v ${HOME}:${HOME} \
		-v ${HOME}/.aws:/pattern-home/.aws \
	  "${REGISTRY}/${CONTAINER}" python3 /usr/local/bin/start-instances.py -f ${CLUSTER}

.PHONY: cluster-stop
cluster-stop: ## Checks the status of hostedcluster machines
	@echo "Stopping hosted-cluster nodes"
	podman run --rm --net=host  \
	  --security-opt label=disable \
		-v ${HOME}:/pattern \
		-v ${HOME}:${HOME} \
		-v ${HOME}/.aws:/pattern-home/.aws \
		"${REGISTRY}/${CONTAINER}" python3 /usr/local/bin/stop-instances.py -f ${CLUSTER}
