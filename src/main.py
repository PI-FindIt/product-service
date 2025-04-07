from contextlib import asynccontextmanager
from typing import AsyncGenerator

import strawberry
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter

from src.config.session import init_postgres_db
from src.graphql import Mutation, Query
from src.models import Product, Category


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_postgres_db()
    yield


schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    types=[Product, Category],
    extensions=[OpenTelemetryExtension],
    enable_federation_2=True,
)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Product Service", lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "pong"}


resource = Resource(attributes={SERVICE_NAME: "product-service"})
tracer = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint="apm-server:8200",
    insecure=True,
)
tracer.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer)

FastAPIInstrumentor.instrument_app(app)
