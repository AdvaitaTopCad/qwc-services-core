"""Authentication helper functions
"""
import os
import re
from typing import Any, Dict, List, Optional, Union

from flask import Flask, request
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

from .jwt import jwt_manager

# Accept user name passed in Basic Auth header
# (password has to checked before!)
ALLOW_BASIC_AUTH_USER = os.environ.get("ALLOW_BASIC_AUTH_USER", "False").lower() in (
    "t",
    "true",
)


def auth_manager(app: Flask, api=None) -> JWTManager:
    """Authentication setup for Flask app"""
    # Setup the Flask-JWT-Extended extension
    return jwt_manager(app, api)


def optional_auth(fn) -> Any:
    """Authentication view decorator"""
    return jwt_required(optional=True)(fn)


def get_identity() -> Any:
    """Get identity (username oder dict with username and groups)"""
    return get_jwt_identity()


def get_username(identity: Union[None, str, Dict[str, str]]) -> Optional[str]:
    """
    Get the username from the identity object.

    Args:
        identity: The identity object. Can be a string or a dict with a
        `username` key.
    """
    if identity:
        if isinstance(identity, dict):
            username = identity.get("username")
        else:
            # identity is username
            username = identity
    else:
        username = None
    return username


def get_groups(identity) -> List[str]:
    """
    Get user groups.

    Args:
        identity: The identity object.

    Returns:
        A list of group names.
    """
    groups = []
    if identity:
        if isinstance(identity, dict):
            groups = identity.get("groups", [])
            group = identity.get("group")
            if group:
                groups.append(group)
    return groups


def get_auth_user() -> str:
    """Get identity or optional pre-authenticated basic auth user"""
    identity = get_identity()
    if not identity and ALLOW_BASIC_AUTH_USER:
        auth = request.authorization
        if auth:
            # We don't check password, already authenticated!
            identity = auth.username
    return identity


class GroupNameMapper:
    """
    Group name mapping with regular expressions

    Example
    -------

    >>> mapper = GroupNameMapper('ship_crew~crew#gis.role.(.*)~\\1')
    >>> print(mapper.mapped_group('ship_crew'))
    >>> print(mapper.mapped_group('gis.role.admin'))
    >>> print(mapper.mapped_group('gis.role.user.group1'))
    >>> print(mapper.mapped_group('gis.none'))
    """

    def __init__(self, default: str = ""):
        group_mappings: str = os.environ.get("GROUP_MAPPINGS", default)

        def collect(mapping: str):
            regex, *replacement = mapping.split("~", 1)
            return (re.compile(regex), replacement[0] if replacement else "")

        self.group_mappings = (
            list(map(collect, group_mappings.split("#"))) if group_mappings else []
        )

    def mapped_group(self, group: Union[str, List[str]]) -> str:
        """
        Maps group names to internal name using regular expressions.

        Args:
            group: The group name or list of group names (LDAP servers my
            return a group as list object).

        Returns:
            A string with known group names replaced by internal names.
        """
        if isinstance(group, list):
            group = " ".join(group)
        for regex, replacement in self.group_mappings:
            if regex.match(group):
                return regex.sub(replacement, group)
        return group
