POETRY_VERSION:=1.8.3

DOCKER_REGISTRY:=ghcr.io/jr200
IMAGE_NAME:=vault-actions
IMAGE_TAG:=latest

VAULT_TOKEN ?= ""

debug: docker-build
	docker run --rm -it --entrypoint bash ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

env:
	echo VAULT_TOKEN=`vault print token` > .env

run: docker-build
	docker run --rm ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

docker-build:
	docker build \
		-f docker/Dockerfile \
		-t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
		--build-arg POETRY_VERSION=${POETRY_VERSION} \
		.

chart:
	kubectl create namespace bstest || echo OK
	helm -n bstest uninstall bs || echo OK
	helm -n bstest install bs charts/vault-actions --set config.vault.token=$(VAULT_TOKEN)