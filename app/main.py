from sanic import HTTPResponse, Sanic, text

app = Sanic("TestSanic")


@app.get("/")
async def hello_world() -> HTTPResponse:
    return text("Hello, world.")
