from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Response, status
from loguru import logger
from pydantic import BaseModel

from vectorapi.const import DEFAULT_EMBEDDING_MODEL
from vectorapi.embedder import get_embedder
from vectorapi.gpt_encoder import gpt_encode
from vectorapi.models import get_highest_score_id
from vectorapi.pgvector.client import StoreClient
from vectorapi.routes.collections import get_collection

router = APIRouter(
    prefix="/collections",
    tags=["points"],
)


class CollectionPointRequest(BaseModel):
    id: str
    input: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    model: str = DEFAULT_EMBEDDING_MODEL


@router.post(
    "/{collection_name}/upsert",
    name="upsert_point",
)
async def upsert_point(
    collection_name: str,
    request: CollectionPointRequest,
    client: StoreClient,
):
    """Create a new collection with the given name and dimension."""
    collection = await get_collection(collection_name, client)

    if request.embedding is None and request.input is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either embedding or input",
        )
    elif request.embedding is None:
        try:
            request.input = gpt_encode(request.input)
            embedder = get_embedder(model_name=request.model)
            request.embedding = embedder.encode(request.input).tolist()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model name {request.model} please use a SentenceTransformer compatible model (e.g. DEFAULT_EMBEDDING_MODEL)",
            ) from e
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error encoding text: {e}",
            )

    logger.debug(f"Upserting point {request.id}")
    try:
        await collection.upsert(request.id, request.embedding, request.metadata)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upserting point: {e}",
        )
    return request


@router.post(
    "/{collection_name}/upsert/not_use_gpt",
    name="not_use_gpt_upsert_point",
)
async def not_use_gpt_upsert_point(
    collection_name: str,
    request: CollectionPointRequest,
    client: StoreClient,
):
    """Create a new collection with the given name and dimension."""
    collection = await get_collection(collection_name, client)

    if request.embedding is None and request.input is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either embedding or input",
        )
    elif request.embedding is None:
        try:
            embedder = get_embedder(model_name=request.model)
            request.embedding = embedder.encode(request.input).tolist()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model name {request.model} please use a SentenceTransformer compatible model (e.g. DEFAULT_EMBEDDING_MODEL)",
            ) from e
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error encoding text: {e}",
            )

    logger.debug(f"Upserting point {request.id}")
    try:
        await collection.upsert(request.id, request.embedding, request.metadata)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upserting point: {e}",
        )
    return request


@router.delete(
    "/{collection_name}/delete/{point_id}",
    name="delete_point",
)
async def delete_point(
    collection_name: str,
    point_id: str,
    client: StoreClient,
):
    """Delete a collection point with the given id."""
    collection = await get_collection(collection_name, client)

    logger.debug(f"Deleting point {point_id}")
    try:
        await collection.delete(point_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting point: {e}",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{collection_name}/get/{point_id}",
    name="get_point",
)
async def get_point(
    collection_name: str,
    point_id: str,
    client: StoreClient,
):
    """Get the collection point matching the given id."""
    collection = await get_collection(collection_name, client)

    logger.debug(f"Getting collection point {point_id}")
    try:
        return await collection.get(point_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting collection point {e}",
        )


class QueryPointRequest(BaseModel):
    query: List[float]
    top_k: int = 10
    filter: Optional[Dict[str, Any]] = None


@router.post(
    "/{collection_name}/query",
    name="query_points",
)
async def query_points(
    collection_name: str,
    request: QueryPointRequest,
    client: StoreClient,
):
    """Query collection with a given embedding query."""
    collection = await get_collection(collection_name, client)

    logger.debug(f"Searching {request.top_k} embeddings for query")
    try:
        points = await collection.query(request.query, request.top_k, request.filter)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching embeddings: {e}",
        )
    return points


class SearchPointRequest(BaseModel):
    input: str
    filter: Optional[Dict[str, Any]] = None
    top_k: int = 10
    model: str = DEFAULT_EMBEDDING_MODEL


@router.post(
    "/{collection_name}/search",
    name="search",
)
async def search(
    collection_name: str,
    request: SearchPointRequest,
    client: StoreClient,
):
    """Search collection with a given text input."""
    collection = await get_collection(collection_name, client)

    try:
        request.input = gpt_encode(request.input)
        embedder = get_embedder(model_name=request.model)
    except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model name {request.model} please use a SentenceTransformer compatible model (e.g. DEFAULT_EMBEDDING_MODEL)",
            ) from e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting embedder: {e}",
        )

    if embedder.dimension != collection.dimension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Embedder dimension {embedder.dimension} does not match collection "
            + f"dimension {collection.dimension}",
        )

    try:
        vector = embedder.encode(request.input)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error encoding text: {e}",
        )

    logger.debug(f"Searching {request.top_k} embeddings for query")
    try:
        points = await collection.query(vector.tolist(), request.top_k, filter_dict=request.filter)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching embeddings: {e}",
        )
    responce_id = get_highest_score_id(points)
    return responce_id
