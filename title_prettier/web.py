import os
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from titles import IncompleteRequestError, URLRetrievalError, get_pretty_title

app = FastAPI(
    title="Title Normalizer",
    description="An API to normalize titles.",
    version="0.0.1",
    license_info={
        "name": "MIT",
        "url": "https://github.com/capjamesg/title-normalizer/blob/main/LICENSE",
    },
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if os.environ.get("SITE_ENV") == "local":
    origins = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
@limiter.limit("10/minute")
async def get_title(
    request: Request, url: str = None, title: str = None
) -> Union[str, dict]:
    """
    Retrieve a prettified title given a URL or a title.
    """
    try:
        return {"title": get_pretty_title(url=url, title=title)}
    except URLRetrievalError:
        raise HTTPException(status_code=500, detail="Failed to retrieve URL")
    except IncompleteRequestError:
        raise HTTPException(
            status_code=400, detail="Either title or URL must be provided"
        )
