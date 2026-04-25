"""FastAPI dependency for user identity — no Firebase required.

Reads user_id from the X-User-ID header.
In production you would validate a JWT here; for this build
the caller is trusted to pass their UID in the header.

Usage in any router:
    from app.auth.dependencies import get_current_user

    @router.get("/protected")
    async def route(user: dict = Depends(get_current_user)):
        user_id = user["uid"]
"""

from fastapi import Header, HTTPException, status


async def get_current_user(
    x_user_id: str = Header(
        ...,
        alias="X-User-ID",
        description="The authenticated user's unique ID.",
    ),
) -> dict:
    """Return a user dict from the X-User-ID header.

    Raises 400 if the header is empty or missing.
    """
    uid = x_user_id.strip()
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-ID header must not be empty.",
        )
    return {"uid": uid}
