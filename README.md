# service-template
Template repository to easily create microservices

## How to generate a new microservice
1. Click on the "Use this template" button on the top right of the repository
2. Fill in the repository name and description
3. Click on "Create repository"
4. Clone the repository
5. Create a virtual environment and activate it
6. Install poetry with `pip install poetry`
7. Install the dependencies with `poetry install`
8. Run `make all` to generate code regarding Docker, CI/CD and gRPC
9. Commit & push changes

## Common ports
There are no ports exposed to the host machine by default.
All services are exposed via Traefik, a reverse proxy.

One can use subdomains, such as `api.localhost`, to access the services.

| Service    | Port  | Subdomain | Available |
|------------|-------|-----------|-----------|
| gRPC       | 50051 | N/A       | No        |
| FastAPI    | 8000  | api       | Yes       |
| PostgreSQL | 5432  | postgres  | Dev only  |
| MongoDB    | 27017 | mongo     | Dev only  |
