import json

from fastapi import HTTPException

from utils.database import execute_query_json
from models.seriescatalog import SeriesCatalog


async def get_series_catalog() -> list[SeriesCatalog]:
    query = "select top 5000 * from series.catalogs"
    result = await execute_query_json(query)
    dict = json.loads(result)
    if not dict:
        raise HTTPException( status_code=404, detail="Series catalog not found" )

    return [ SeriesCatalog(**item) for item in dict ]