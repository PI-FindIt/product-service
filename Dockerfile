FROM python:3.13-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV ENV development

WORKDIR /product-service

RUN pip install --no-cache poetry

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project false && poetry env use python && poetry install --with dev

EXPOSE 8000
CMD [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]
