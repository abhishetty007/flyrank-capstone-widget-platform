from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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