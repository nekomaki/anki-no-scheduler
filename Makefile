# Makefile

.PHONY: build test clean

DIST_DIR := dist
OUTPUT := $(DIST_DIR)/output.ankiaddon

build:
	@echo "Building Anki addon package..."
	mkdir -p $(DIST_DIR)
	rm -f $(OUTPUT)
	cd src && zip -r ../$(OUTPUT) . -x "*.pyc" -x "*/__pycache__" -x "meta.json"

test:
	@echo "Running tests..."
	PYTHONPATH=src pytest

clean:
	@echo "Cleaning up..."
	rm -rf $(DIST_DIR)
