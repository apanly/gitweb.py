import os
import hashlib
import time
import ldap
import web
from web import form
from auth import RequireRegistrationException

render = web.template.render(
    'templates/',
    base='main',
    globals={'time':time, 'session':web.config.session})

login_form = form.Form(
    form.Textbox("username", description="Username or Email"),
    form.Password("password", description="Password"),
    form.Button("submit", type="submit", description="Sign in"),
    validators = [])

class login:
    def POST(self):
        f = login_form()
        if not f.validates():
            raise web.seeother('/')

        authOptions = [am for am in web.config.auth.methods if am.can_handle_user(f.d.username)]
        if len(authOptions) == 0:
            raise web.internalerror("No appropriate login method available")

        for ao in authOptions:
            if ao.can_handle_user(f.d.username) == False:
                continue

            try:
                success, res = ao.login(f.d.username, f.d.password, web.config)
                if success == True:
                    web.config.session.loggedin = True
                    web.config.session.userid = res['userid']
                    web.config.session.userfullname = res['userfullname']
                    web.config.session.userrights = res['rights']
                    raise web.seeother("/")
            except RequireRegistrationException, info:
                web.config.session.showIdentifierRegistration = True
                web.config.session.userid = info.username
                web.config.session.userfullname = info.userfullname
                web.config.session.userrights = "member"
                raise web.seeother('/register')

        raise web.seeother("/")

class logout:
    def GET(self):
        web.config.session.loggedin = False
        if 'userid' in web.config.session:
            del web.config.session.userid
        if 'userfullname' in web.config.session:
            del web.config.session.userfullname
        raise web.seeother('/')

