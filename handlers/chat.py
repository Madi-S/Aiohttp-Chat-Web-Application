from aiohttp_jinja2 import template
from aiohttp import web


@template('chat.html')
async def get_chat(request):
    pass


async def post_chat(request):
    pass


async def handle_all(request):
    raise web.HTTPFound('/chat')