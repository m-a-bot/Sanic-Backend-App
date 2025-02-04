from sanic import Sanic

from app.config import settings
from app.routers.admin_router import admin_user_router
from app.routers.pay_system_router import webhooks_payments_router
from app.routers.user_router import user_router

app = Sanic("SanicBackendApp")
app.config.OAS_URL_PREFIX = "/apidocs"
app.config.SECRET = settings.SECRET_KEY

app.blueprint(user_router)
app.blueprint(admin_user_router)
app.blueprint(webhooks_payments_router)
