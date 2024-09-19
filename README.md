# VectorAPI

[![License](https://img.shields.io/github/license/grafana/vectorapi)](LICENSE)
[![Build Status](https://drone.grafana.net/api/badges/grafana/vectorapi/status.svg)](https://drone.grafana.net/grafana/vectorapi)
[![Docker](https://img.shields.io/docker/v/grafana/vectorapi?logo=docker)](https://hub.docker.com/r/grafana/vectorapi/tags)
[![API Docs](https://img.shields.io/badge/docs-api-blue)](https://grafana.github.io/vectorapi/)

VectorAPI is a service for managing vector collections and performing vector similarity queries using a PostgreSQL vector database with the `pgvector` extension. Utilizes `fastapi` for the HTTP API, `pgvector` and SQLAlchemy for the vector database side and relies on `pytorch` for computing embeddings.

## Getting started


### New database

You can bring up a postgres database (`ankane/pgvector`) and vectorapi instance using docker compose:

```sh
docker compose up --build
```


### Adding a vector to a collection

1. Create a collection

```sh
curl -X POST "http://localhost:8889/v1/collections/create" \
    -H "Content-Type: application/json" \
    -d '{"collection_name":"my_collection", "dimension":384}'
```

2. Add a vector to the collection

```sh
curl -X POST "http://localhost:8889/v1/collections/my_collection/upsert" \
    -H "Content-Type: application/json" \
    -d '{"id":"abc2", "metadata":{"key":"value"}, "input":"ビーチを散歩するのが好きなんだ。"}'
```

### Vector search

```sh
curl -X POST "http://localhost:8889/v1/collections/my_collection/search" \
    -H "Content-Type: application/json" \
    -d '{"input":"ビーチで歩く"}'
```
