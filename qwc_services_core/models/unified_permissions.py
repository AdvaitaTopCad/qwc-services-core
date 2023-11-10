"""Hosts the "unified" version of the permission models.

To generate the JSON schema run this file with no arguments.
It will print the JSON schema to the standard output.

`UnifiedServicesPermissions` is the top level model for QWC Services permissions.
It can be used to parse and validate permissions JSON files.
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import GenerateJsonSchema

SCHEMA_ID = (
    "https://github.com/qwc-services/qwc-services-core/"
    "raw/master/schemas/qwc-services-unified-permissions.json"
)


class User(BaseModel):
    name: str = Field(
        description="User name",
    )
    groups: Optional[List[str]] = Field(
        title="Group memberships",
    )
    roles: Optional[List[str]] = Field(default=None, title="Role memberships")


class Group(BaseModel):
    name: str = Field(
        description="Group name",
    )
    roles: Optional[List[str]] = Field(title="Role memberships")


class Permissions(BaseModel):
    all_services: Dict[str, Any] = Field(
        description=(
            "Permitted resources for all services (top-level permitted "
            "layers and group layers, datasets with write permissions, "
            "document templates). NOTE: Use resource name as property name "
            "for its permissions."
        ),
        json_schema_extra={
            "additionalProperties": {
                "description": "Resource permissions",
                "type": "object",
                "properties": {
                    "writable": {
                        "description": (
                            "Writable flag for datasets with write permissions",
                        ),
                        "type": "boolean",
                    }
                },
            }
        },
    )

    @field_validator("all_services")
    @classmethod
    def validate_all_services(cls, v: Any) -> Any:
        if isinstance(v, dict):
            errors = {}
            for k, v in v.items():
                if k == "writable":
                    errors[k] = v
            if errors:
                raise ValueError(errors)
        return v


class Role(BaseModel):
    role: str = Field(
        description="Role name",
    )
    permissions: Permissions = Field(
        title="Permissions for role",
    )


class Layer(BaseModel):
    """Single layer."""

    name: str = Field(description="Layer name")
    attributes: List[str] = Field(
        description="List of attributes, excluding 'geometry'"
    )


class GroupLayer(BaseModel):
    """Group layer with sublayers."""

    name: str = Field(description="Group layer name")
    sublayers: List[str] = Field(description="List of sublayer identifiers'")


class UnifiedServicesPermissions(BaseModel):
    """Unified and simplified permissions if resource permissions are identical
    in all QWC Services.
    """

    model_config = ConfigDict(
        title="Unified QWC Services Permissions",
    )

    users: List[User] = Field(
        title="Users",
    )
    groups: List[Group] = Field(
        title="Groups",
    )
    roles: List[Role] = Field(
        title="Roles",
    )
    wms_name: str = Field(description="Name of WMS service and its root layer")
    wfs_name: str = Field(description="WFS service name")
    dataproducts: List[Union[Layer, GroupLayer]] = Field(
        title="Dataproducts",
    )
    common_resources: List[str] = Field(
        description=(
            "Additional resource names with no restrictions (internal print "
            "layers, background layers, print templates, default Solr facets)"
        )
    )


if __name__ == "__main__":
    import json

    class Generator(GenerateJsonSchema):
        schema_dialect = "http://json-schema.org/draft-07/schema#"

        def generate(self, schema, mode="validation"):
            json_schema = super().generate(schema, mode=mode)
            json_schema["$id"] = SCHEMA_ID
            json_schema["$schema"] = self.schema_dialect
            json_schema["properties"]["$schema"] = {
                "title": "JSON Schema",
                "description": "Reference to JSON schema of these permissions",
                "type": "string",
                "format": "uri",
                "default": SCHEMA_ID,
            }
            return json_schema

    print(
        json.dumps(
            UnifiedServicesPermissions.model_json_schema(
                schema_generator=Generator,
            ),
            indent=2,
        )
    )
