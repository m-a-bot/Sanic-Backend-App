#!/bin/bash
poetry run ruff check app
poetry run ruff format --check app