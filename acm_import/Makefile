CLUSTERGROUP ?= group-one

.PHONY: help
# No need to add a comment here as help is described in common/
help:
	@printf "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)\n"

.PHONY: import
import: ## Imports SPOKECONFIG into HUBCONFIG defined clusters
	ansible-playbook -e clustergroup=$(CLUSTERGROUP) post.yml
