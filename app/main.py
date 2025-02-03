from sanic import Sanic

from app.config import settings
from app.routers.user_router import user_router

app = Sanic("SanicBackendApp")
app.config.OAS_URL_PREFIX = "/apidocs"
app.config.SECRET = settings.SECRET_KEY

app.blueprint(user_router)
