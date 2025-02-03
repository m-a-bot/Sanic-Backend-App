FROM --platform=linux/amd64 python:3.12-alpine3.20

ENV PYTHONPATH=/src

WORKDIR /src
COPY app /src/app

COPY ["./pyproject.toml", "./poetry.lock", "./alembic.ini", ".env", "/src/"]

ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "sanic", "app.main:app", "--host=0.0.0.0"]