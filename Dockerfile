FROM python:3.13-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VIRTUALENVS_CREATE false
ENV POETRY_VIRTUALENVS_IN_PROJECT false
ENV ENV development

WORKDIR /product-service

RUN apk add --no-cache patch
RUN pip install --no-cache poetry

COPY poetry.lock pyproject.toml patches/ ./
RUN poetry install --with dev

WORKDIR /usr/local/lib/python3.13/site-packages
RUN patch -p1 < /product-service/strawberry-sqlalchemy.patch

WORKDIR /product-service
EXPOSE 8000
CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]
