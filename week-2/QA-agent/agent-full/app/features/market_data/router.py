from fastapi import APIRouter, HTTPException, Depends

from app.core.engine import get_engine
from etl.read import read
from app.deps import get_current_user
from app.features.auth.models import User

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["data"])

ALLOWED_ASSETS = {"gold", "dxy", "silver", "oil", "sp500"}


@router.get("/{asset}")
def get_asset_data(
    asset: str,
    rows: int = 30,
    user: User = Depends(get_current_user),
):
    if asset not in ALLOWED_ASSETS:
        logger.warning("Unknown asset:%s.", asset)
        raise HTTPException(
            status_code=400,
            detail=f"Unknown asset '{asset}'. Allowed: {sorted(ALLOWED_ASSETS)}",
        )

    engine = get_engine()
    df = read(engine, table_name=f"ohlcv_{asset}")
    if df.empty:
        logger.warning("Yahoo finance returned no data.")
        raise HTTPException(status_code=404, detail=f"No data for '{asset}'")

    df_out = df.tail(rows).reset_index()
    df_out["date"] = df_out["date"].dt.strftime("%Y-%m-%d")
    return df_out.to_dict(orient="records")
