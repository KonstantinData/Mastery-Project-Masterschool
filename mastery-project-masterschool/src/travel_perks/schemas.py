"""Schema definitions for cleaned and aggregated data.

Schemas are expressed using Pydantic models which provide both runtime
validation and well‑defined type hints for developers. By specifying
strict types and constraints, we minimise the risk of downstream
errors due to malformed data and provide a clear contract between
pipeline stages.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, validator


class UserFeatures(BaseModel):
    """Aggregated features for a single user.

    After the raw TravelTide data is cleaned and aggregated, each
    distinct user will have one row in the feature table described
    by this model. The features are intentionally simple and avoid
    personally identifying information, focusing only on behavioural
    signals such as booking counts and discount usage. PII should never
    be included in logs or outputs【952685827302670†L49-L58】.
    """

    user_id: int = Field(..., description="Unique identifier for the user")
    total_sessions: int = Field(..., ge=0, description="Number of sessions for the user")
    total_bookings: int = Field(..., ge=0, description="Total number of flight/hotel bookings")
    total_nights: int = Field(..., ge=0, description="Total nights stayed across all hotels")
    avg_discount_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Average discount rate (0–1) across bookings"
    )
    cluster_id: Optional[int] = Field(None, description="Cluster index assigned during segmentation")
    perk: Optional[str] = Field(None, description="Perk assigned based on cluster")

    @validator("avg_discount_rate", pre=True)
    def _coerce_discount(cls, v: float) -> float:  # noqa: D417
        # Notes:
        #   Pydantic validators can return transformed values for fields.
        #   When computing the average discount rate we may encounter
        #   floating NaN (``v != v`` is a common NaN check). This
        #   validator replaces NaN with 0.0 to ensure the value
        #   respects the declared ``ge=0.0`` constraint. If the value
        #   is not NaN it is converted to a float.
        return 0.0 if v != v else float(v)