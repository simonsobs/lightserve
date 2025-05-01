"""
Authentication, can use 'none' to get a default user that's allowed
to do everything, or can use 'soauth' to provide a different set of
dependencies.
"""

import functools
import inspect

from fastapi import HTTPException, Request, status
from starlette._utils import is_async_callable

from .settings import settings

AVAILABLE_GRANTS = {
    "lcs:create",
    "lcs:delete",
}


def setup_auth(app):
    if settings.auth_system == "soauth":
        from soauth.toolkit.fastapi import global_setup

        app = global_setup(
            app=app,
            app_base_url=settings.soauth_base_url,
            authentication_base_url=settings.soauth_service_url,
            app_id=settings.soauth_app_id,
            key_pair_type=settings.soauth_key_pair_type,
            public_key=settings.soauth_public_key,
            client_secret=settings.soauth_client_secret,
        )

    return app


def has_required_scope(request: Request, scopes: list[str]) -> bool:
    if settings.auth_system is None:
        return True

    for scope in scopes:
        if scope not in request.auth.scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return True


def requires(scopes: str | list[str]):
    """
    Check whether your user has the required scope.
    """

    def decorator(func):
        scopes_list = [scopes] if isinstance(scopes, str) else list(scopes)

        for scope in scopes_list:
            if scope not in AVAILABLE_GRANTS:
                raise HTTPException(501, "Invalid scope, server error")

        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request":
                break
        else:
            raise Exception(f'No "request" argument on function "{func}"')

        if is_async_callable(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                request = kwargs.get("request", args[idx] if idx < len(args) else None)
                assert isinstance(request, Request)

                if has_required_scope(request, scopes_list):
                    return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                request = kwargs.get("request", args[idx] if idx < len(args) else None)
                assert isinstance(request, Request)

                if has_required_scope(request, scopes_list):
                    return func(*args, **kwargs)

            return sync_wrapper

    return decorator
