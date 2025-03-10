FROM python:3.13-slim

WORKDIR /service

RUN pip install poetry

COPY ./pyproject.toml .

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

COPY ./alembic.ini .

COPY . .

EXPOSE 8062

CMD ["sh", "-c", "alembic upgrade head && python start.py"]