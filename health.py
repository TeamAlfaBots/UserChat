"""
Minimal health-check HTTP server so the bot can run as a Render Web Service
(Render needs an open port) and so UptimeRobot (or similar) can ping it to
prevent the free-tier instance from sleeping.
"""

from aiohttp import web

import config


async def _handle_root(request):
    return web.Response(text="OK - eco userbot is alive")


async def _handle_ping(request):
    return web.json_response({"status": "ok"})


def create_app():
    app = web.Application()
    app.router.add_get("/", _handle_root)
    app.router.add_get("/ping", _handle_ping)
    return app


async def start_health_server():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    return runner
