"""
Main FastAPI application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .core.config import settings
from .core.database import Base, engine, get_db
from .services.domain_service import DomainInitializer
from .routes import auth, interviews, domains

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Platform API",
    description="Full-stack AI-powered interview platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db = next(get_db())
    try:
        DomainInitializer.initialize_domains(db)
    except Exception as e:
        print(f"Error initializing domains: {e}")
    finally:
        db.close()


# Include routers
app.include_router(auth.router)
app.include_router(interviews.router)
app.include_router(domains.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Root endpoint
@app.get("/")
async def root():
    """API root"""
    return {
        "message": "Welcome to AI Interview Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.environment == "development"
    )
