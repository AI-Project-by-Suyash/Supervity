import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.database import engine, SessionLocal
from app.models.base import Base
from app.seed.seed_data import seed_database
from app.api import routes_exceptions, routes_resolution, routes_audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables & seed if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.exception import ExceptionRecord
        if db.query(ExceptionRecord).count() == 0:
            seed_database(db, reset=False)
    finally:
        db.close()
    yield

app = FastAPI(
    title='Exception Resolution Workbench',
    version='1.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Mount static files & templates
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
templates_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')

if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')

templates = Jinja2Templates(directory=templates_dir if os.path.exists(templates_dir) else '.')

# Include API Routers
app.include_router(routes_exceptions.router, prefix='/api', tags=['Exceptions'])
app.include_router(routes_resolution.router, prefix='/api', tags=['Resolution & AI'])
app.include_router(routes_audit.router, prefix='/api', tags=['Audit'])

@app.get('/health', tags=['Health'])
@app.get('/api/health', tags=['Health'])
async def health_check():
    return {
        'status': 'healthy',
        'app': 'Exception Resolution Workbench',
        'version': '1.0.0'
    }

@app.get('/', response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/api/seed/reset', tags=['Seed'])
async def reset_seed_data():
    count = seed_database(reset=True)
    return {'status': 'success', 'message': f'Reset and seeded {count} exceptions.'}

