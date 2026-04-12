dev:
    uv run --with . grid

install:
    uv pip install -e .

build:
    python -m build --check

test:
    uv run pytest

lint:
    uv run ruff check

fmt:
    uv run ruff format

clean:
    rm -rf dist/ .pytest_cache/ __pycache__/ .ruff_cache/

docker-build:
    docker build -t grid-test .

docker-run command="test":
    docker run --rm grid-test just {{command}}
