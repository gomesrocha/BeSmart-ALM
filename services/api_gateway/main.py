"""API Gateway - Main entry point for Bsmart-ALM platform."""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.shared.config import settings
from services.shared.database import init_db
from services.shared.middleware import TenantMiddleware

# Import routers
from services.identity.router import router as auth_router
from services.identity.role_router import router as role_router
from services.identity.token_router import router as token_router
from services.identity.user_router import router as user_router
from services.identity.tenant_router import router as tenant_router
from services.identity.audit_router import router as audit_router
from services.project.router import router as project_router
from services.project.document_router import router as document_router
from services.work_item.router import router as work_item_router
from services.requirements.router import router as requirements_router
from services.specification.router import router as specification_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Bsmart-ALM API Gateway...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down Bsmart-ALM API Gateway...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-first Application Lifecycle Management platform with MPS.BR compliance",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Tenant Middleware for multi-tenant isolation
# This middleware extracts tenant_id from JWT and injects it into request.state
app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(token_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(tenant_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(work_item_router, prefix="/api/v1")
app.include_router(requirements_router, prefix="/api/v1")
app.include_router(specification_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/info")
async def api_info() -> dict[str, Any]:
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-first ALM platform",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Any, exc: Any) -> JSONResponse:
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "path": str(request.url),
            }
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Any, exc: Any) -> JSONResponse:
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.api_gateway.main:app",
        host="0.0.0.0",
        port=8086,
        reload=settings.debug,
    )
