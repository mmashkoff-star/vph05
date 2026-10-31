from app.routes.admin import router as admin_router
from app.routes.behaviors import router as behaviors_router
from app.routes.leads import router as leads_router

__all__ = ["leads_router", "behaviors_router", "admin_router"]
