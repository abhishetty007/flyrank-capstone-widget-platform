from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.app.api.auth import get_current_user
from backend.app.api.auth import router as auth_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.submissions import router as submissions_router
from backend.app.api.widgets import router as widgets_router
from backend.app.models import User


app = FastAPI(
    title="FlyRank Widget Platform",
    description="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0",
)


MAX_PUBLIC_SUBMISSION_SIZE = 10 * 1024


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_public_submission_size(request, call_next):
    if (
        request.method == "POST"
        and request.url.path == "/public/submissions"
    ):
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                if int(content_length) > MAX_PUBLIC_SUBMISSION_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": "Submission payload is too large."
                        },
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Invalid Content-Length header."
                    },
                )

        body = await request.body()

        if len(body) > MAX_PUBLIC_SUBMISSION_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Submission payload is too large."
                },
            )

        async def receive():
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        request._receive = receive

    return await call_next(request)


app.include_router(auth_router)
app.include_router(widgets_router)
app.include_router(submissions_router)
app.include_router(dashboard_router)


@app.get("/widget/widget.js")
def serve_widget():
    response = FileResponse(
        "widget/widget.js",
        media_type="application/javascript",
    )

    response.headers["Cache-Control"] = (
        "public, max-age=300, must-revalidate"
    )

    response.headers["X-Widget-Version"] = "1"

    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "FlyRank Widget Platform API is running"
    }


@app.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "email": current_user.email,
    }