import os
import uvicorn
from app.core.config import settings

if __name__ == '__main__':
    port = int(os.environ.get('PORT', settings.PORT))
    host = os.environ.get('HOST', '0.0.0.0')
    uvicorn.run(
        'app.main:app',
        host=host,
        port=port,
        reload=settings.APP_ENV == 'development'
    )

