ruff_fix:
	uv run ruff format . && uv run ruff check --fix . && uv run ruff check --fix --select I .
ruff_check:
	uv run ruff check . && uv run ruff check --select I . && uv run ruff format --check .
test:
	docker compose -f docker-compose.yml run --rm app-test
	docker compose -f docker-compose.yml --profile test down --volumes
start_dev:
	docker compose -f docker-compose.yml --profile dev up -d --build
	docker container exec app-dev alembic upgrade heads
remove_dev:
	docker compose -f docker-compose.yml --profile dev down -v
start_local_db:
	docker compose -f docker-compose.yml up -d postgres-dev
stop_local_db:
	docker compose -f docker-compose.yml down postgres-dev
remove_local_db:
	docker compose -f docker-compose.yml down -v postgres-dev
migrate:
	uv run alembic upgrade heads