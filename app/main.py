from fastapi import FastAPI
from app.database import initialize_async_db
from app.dependencies import get_settings
from app.routers import qr_code, oauth, user_routes
from app.services.qr_service import create_directory
from app.utils.common import setup_logging

# This function sets up logging based on the configuration specified in your logging configuration file.
setup_logging()

# Retrieve settings
settings = get_settings()

# Ensure that the directory for storing QR codes exists when the application starts.
# If it doesn't exist, it will be created.
create_directory(settings.qr_directory)

# Create an instance of the FastAPI application.
app = FastAPI(
    title="Event Management",
    description="A FastAPI application for creating, listing available codes, and deleting QR codes. "
                "It also supports OAuth for secure access.",
    version="0.0.1",
    redoc_url=None,
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)
settings = get_settings()
@app.on_event("startup")
def startup_event():
    initialize_async_db(settings.database_url)
# Include the routers for your application.
app.include_router(qr_code.router)  # QR code management routes
app.include_router(oauth.router)  # OAuth authentication routes
# app.include_router(events.router)
app.include_router(user_routes.router)
