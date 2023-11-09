"""Sqlalchemy ORM models for ConfigDB queries."""
from typing import Any, Dict, List, Optional, cast

from flask_login import UserMixin
from sqlalchemy import Engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, backref, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from qwc_services_core.database import DatabaseEngine


class ConfigModels:
    """Provide SQLAlchemy ORM models for ConfigDB queries.

    Note:
        The class relies on an existing database schema from which it
        derives the models.

    Attributes:
        engine: The SQLAlchemy engine used to communicate with this database.
        base: Base class for ORM models.
        user_model: User model for flask_login.
        custom_models: Extra models that are only used by the ``model()``
            method, when the requested name is not found among the automap models.
    """

    engine: Engine
    custom_models: Dict[str, str]
    base: Any
    user_model: DeclarativeMeta

    def __init__(
        self,
        db_engine: DatabaseEngine,
        conn_str: Optional[str] = None,
        extra_tables: List[str] = [],
    ):
        """Constructor.

        We create a database engine from the given connection string or
        from the ``CONFIGDB_URL`` environment variable if no connection string
        is given. If a previous connection to the same database exists, we
        reuse that connection.

        Args:
            db_engine: The connection pool to use.
            conn_str: DB connection string for SQLAlchemy engine.
            extra_tables: List of extra tables to include in the model.
        """
        if conn_str:
            self.engine = db_engine.db_engine(conn_str)
        else:
            self.engine = db_engine.config_db()

        # init models
        self.base = None
        self.custom_models = {}
        self.init_models(extra_tables)

    def session(self) -> Session:
        """Create a new session."""
        return Session(self.engine)

    def model(self, name: str) -> DeclarativeMeta:
        """Get SQLAlchemy model.

        Args:
            name: The name of the table to get the model for.
        """
        # get automap model or custom model
        if name == "users":
            return self.user_model
        else:
            return cast(
                DeclarativeMeta,
                self.base.classes.get(name) or self.custom_models.get(name),
            )

    def init_models(self, extra_tables: List[str]):
        """Setup SQLAlchemy ORM models.

        Args:
            extra_tables: List of extra tables to include in the model. This list
                is appended to the default list of tables that is then
                used to filter the tables from the database schema.
        """
        TABLES = [
            "users",
            "user_infos",
            "groups",
            "roles",
            "groups_users",
            "users_roles",
            "groups_roles",
            "resources",
            "resource_types",
            "permissions",
            "registrable_groups",
            "registration_requests",
            "last_update",
        ] + extra_tables

        def table_selector(table_name, meta_data):
            return table_name in TABLES

        metadata = MetaData()
        metadata.reflect(self.engine, schema="qwc_config", only=table_selector)
        Base: Any = automap_base(metadata=metadata)

        # setup user model for flask_login
        class User(UserMixin, Base):
            __tablename__ = "users"
            __table_args__ = {"schema": "qwc_config"}

            def set_password(self, password):
                self.password_hash = generate_password_hash(password)

            def check_password(self, password):
                return check_password_hash(self.password_hash, password)

        Base.prepare()

        self.base = Base
        self.user_model = cast(DeclarativeMeta, User)

        UserInfo = Base.classes.user_infos
        Group = Base.classes.groups
        Role = Base.classes.roles

        # single user info per user
        User.user_info = relationship(
            UserInfo,
            uselist=False,
            back_populates="user",
            overlaps="user_infos_collection",
        )

        # sorted user groups
        User.sorted_groups = relationship(
            Group,
            secondary="qwc_config.groups_users",
            order_by=Group.name,
            # avoid duplicate group DELETE on User delete
            viewonly=True,
        )
        # sorted user roles
        User.sorted_roles = relationship(
            Role,
            secondary="qwc_config.users_roles",
            order_by=Role.name,
            # avoid duplicate role DELETE on User delete
            viewonly=True,
        )

        Group.users_collection = relationship(
            User,
            secondary="qwc_config.groups_users",
            overlaps="groups_collection,user_collection",
        )

        # sorted group users
        Group.sorted_users = relationship(
            User,
            secondary="qwc_config.groups_users",
            order_by=User.name,
            # avoid duplicate user DELETE on Group delete
            viewonly=True,
        )
        # sorted group roles
        Group.sorted_roles = relationship(
            Role,
            secondary="qwc_config.groups_roles",
            order_by=Role.name,
            # avoid duplicate role DELETE on Group delete
            viewonly=True,
        )

        Role.users_collection = relationship(
            User,
            secondary="qwc_config.users_roles",
            overlaps="roles_collection,user_collection",
        )

        # sorted role users
        Role.sorted_users = relationship(
            User,
            secondary="qwc_config.users_roles",
            order_by=User.name,
            # avoid duplicate user DELETE on Role delete
            viewonly=True,
        )
        # sorted roles groups
        Role.sorted_groups = relationship(
            Group,
            secondary="qwc_config.groups_roles",
            order_by=Group.name,
            # avoid duplicate group DELETE on Role delete
            viewonly=True,
        )

        # sorted resource children and parent
        Resource = Base.classes.resources
        Resource.children = relationship(
            Resource,
            foreign_keys=[Resource.parent_id],
            order_by=Resource.name,
            backref=backref(
                "parent",
                remote_side=[Resource.id],
                overlaps="resources,resources_collection",
            ),
            overlaps="resources,resources_collection",
        )

        # resource type
        ResourceType = Base.classes.resource_types
        Resource.resource_type = relationship(
            ResourceType, overlaps="resource_types,resources_collection"
        )

        # permission role and resource with singular attribute names
        Permission = Base.classes.permissions
        Permission.role = relationship(Role, overlaps="permissions_collection,roles")
        Permission.resource = relationship(
            Resource, overlaps="permissions_collection,resources"
        )

        # group for registrable group with singular attribute name
        RegistrableGroup = Base.classes.registrable_groups
        RegistrableGroup.group = relationship(
            Group, overlaps="groups,registrable_groups_collection"
        )

        # user and registrable group for registration request with
        # singular attribute names
        RegistrationRequest = Base.classes.registration_requests
        RegistrationRequest.user = relationship(User, overlaps="registration_requests")
        RegistrationRequest.registrable_group = relationship(
            RegistrableGroup,
            overlaps="registrable_groups,registration_requests_collection",
        )

        # user registration requests
        User.registration_requests = relationship(
            RegistrationRequest,
            # destroy registration requests on user delete
            cascade="save-update, merge, delete",
        )
