from aiohttp import web

from aiohttp_jinja2 import template
from aiohttp_session import new_session, get_session
from aiohttp_csrf import csrf_protect, generate_token

from db import user_checked
from py_settings import log, logger

from config import FORM_FIELD_NAME

from web_decorators import check_del_error, check_cookies


# Handler for /login - show the login.html page with the help of jinja templates, csrf protection enabled
@log
@csrf_protect
@template('login/login.html')
@check_del_error
async def get_login(request, error):
    token = await generate_token(request)
    return {'field_name': FORM_FIELD_NAME, 'token': token, 'error': error}


# Handler for /register - show the register.html page with the help of jinja templates, csrf protection enabled
@log
@csrf_protect
@template('login/register.html')
@check_del_error
async def get_register(request, error):
    token = await generate_token(request)
    return {'field_name': FORM_FIELD_NAME, 'token': token, 'error': error}


# Post /login method to check if user entered satisfying username&password to register or login
@log
@csrf_protect
@check_del_error
async def post_login(request):
    # If user's inputs are satisfying DB -> redirect to chat
    # If user's inputs are NOT satisfying DB -> return bad response
    form = await request.post()
    session = await get_session(request)

    pool = request.app['pool']
    username, pwd = form.get('username'), form.get('password')

    # If user wants to be logged-in automatically
    if form.get('remember'):
        session['remember_me'] = True
        print('User WANTS to save his cookies')

    # Otherwise do not check user's cookies on login
    else:
        session['remember_me'] = False
        print('User does NOT want to be logged-in automatically')

    # Request came from registration page
    if form.get('password-repeat'):

        # Check if username's absence in db:
        if await user_checked(pool, username, pwd):
            print(f'User {username} has been added to database')
            session['user_id'] = (username, pwd)
            raise web.HTTPFound('/chat')

        session['error'] = True
        return web.HTTPFound('/register')

    # Request came from login page
    else:

        # Check user's presence in db
        if await user_checked(pool, username, pwd, register=False):
            print(f'User {username} has been passed login section')
            session['user_id'] = (username, pwd)
            raise web.HTTPFound('/chat')

        # If login & password pair do not match or user with such login does not exist
        session['error'] = True
        return web.HTTPFound('/login')


# Post method to logout - delete all user's cookies and redirect him/her to /login page
@log
@check_del_error
async def post_logout(request):
    session = await get_session(request)
    print(f'User {session["user_id"]} has been deleted from session storage')
    del session['user_id']
    del session['remember_me']

    raise web.HTTPFound('/login', text='Successful logout')


# Actually, inacessible method for normal humans
@log
@check_del_error
async def get_logout(request, error):
    raise web.HTTPFound('/login', text='Login first')


# !!!TODO!!!:
# Method to recover a password
@log
@check_del_error
async def post_recover(request):
    # recover user password by its user recovery link in the database `pwd_reset_token`
    pass
