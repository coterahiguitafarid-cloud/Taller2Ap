from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect


ACCESS_TOKEN_COOKIE = "access_token"
TOKEN_ISSUER = "t1-pyapif"
ACCESS_TOKEN_SECONDS = 30 * 60


def create_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.pk),
        "iat": now,
        "exp": now + timedelta(seconds=ACCESS_TOKEN_SECONDS),
        "iss": TOKEN_ISSUER,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def get_access_token(request):
    authorization = request.headers.get("Authorization", "")
    if authorization:
        scheme, separator, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and separator and token:
            return token
        return None
    return request.COOKIES.get(ACCESS_TOKEN_COOKIE)


def get_token_user(request):
    token = get_access_token(request)
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            issuer=TOKEN_ISSUER,
            options={"require": ["sub", "exp", "iat", "iss", "type"]},
        )
    except jwt.InvalidTokenError:
        return None

    if payload["type"] != "access":
        return None

    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=payload["sub"], is_active=True)
    except (user_model.DoesNotExist, ValueError, TypeError):
        return None
    return user


def set_access_token_cookie(response, token):
    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        token,
        max_age=ACCESS_TOKEN_SECONDS,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
    return response


def jwt_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        user = get_token_user(request)
        if user is None:
            return redirect("login")
        request.jwt_user = user
        return view(request, *args, **kwargs)

    return wrapped
