dev_tag = auto-tesseract:dev
rel_tag = auto-tesseract

all: build test lint

build: Dockerfile *.py *.txt
	docker build -t $(dev_tag) .

release: build
	docker build -t $(rel_tag) .

lint: build
	docker run --entrypoint mypy $(dev_tag) $(wildcard *.py) $(wildcard tests/*.py)

# Run as root so pytest can write /app/.cache.
test: build $(wildcard tests/*.py)
	docker run --user root --entrypoint pytest $(dev_tag) $(wildcard tests/*.py)

clean:
	@echo "run: docker image prune"
