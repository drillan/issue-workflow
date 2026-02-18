USER_UID := $(shell id -u)
USER_GID := $(shell id -g)
GH_TOKEN := $(shell gh auth token 2>/dev/null)
export USER_UID USER_GID GH_TOKEN

.PHONY: docker-build docker-dev docker-test docker-quality

docker-build:  ## Dockerイメージをビルド
	docker compose build

docker-dev:  ## 対話的な開発環境に入る
	docker compose run --rm dev

docker-test:  ## テストを実行
	docker compose run --rm test

docker-quality:  ## 品質チェックを実行（ruff + mypy）
	docker compose run --rm quality
