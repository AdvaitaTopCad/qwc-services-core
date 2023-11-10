"""Hosts the permission models.

To generate the JSON schema run this file with no arguments.
It will print the JSON schema to the standard output.

`ServicesPermissions` is the top level model for QWC Services permissions.
It can be used to parse and validate permissions JSON files.
"""
from typing import List

from pydantic import BaseModel, ConfigDict, Field
from pydantic.json_schema import GenerateJsonSchema

SCHEMA_ID = (
    "https://github.com/qwc-services/qwc-services-core/"
    "raw/master/schemas/qwc-services-permissions.json"
)


class User(BaseModel):
    name: str = Field(
        description="User name",
    )
    groups: List[str] = Field(
        title="Group memberships",
    )
    roles: List[str] = Field(default_factory=list, title="Role memberships")


class Group(BaseModel):
    name: str = Field(
        description="Group name",
    )
    roles: List[str] = Field(title="Role memberships")


class WmsLayer(BaseModel):
    name: str = Field(
        description="WMS layer name",
    )
    attributes: List[str] = Field(
        default_factory=list,
    )
    info_template: bool = Field(
        default=False,
    )


class WmsService(BaseModel):
    model_config = ConfigDict(
        title="WMS permission",
    )

    name: str = Field(
        description="WMS service name",
    )
    layers: List[WmsLayer] = Field(
        description="Flat list of permitted layers and group layers",
    )
    print_templates: List[str] = Field(
        default_factory=list,
        description="List of print templates",
    )


class WfsLayer(BaseModel):
    name: str = Field(
        description="WFS layer name",
    )
    attributes: List[str] = Field(
        default_factory=list,
    )


class WfsService(BaseModel):
    model_config = ConfigDict(
        title="WFS permission",
    )
    name: str = Field(
        description="WFS service name",
    )
    layers: List[WfsLayer] = Field(
        description="List of permitted layers",
    )


class Dataset(BaseModel):
    model_config = ConfigDict(
        title="Dataset permissions",
    )
    name: str = Field(
        description="Dataset name",
    )
    attributes: List[str] = Field()
    writable: bool = False
    creatable: bool = False
    readable: bool = True
    updatable: bool = False
    deletable: bool = False


class PluginData(BaseModel):
    model_config = ConfigDict(
        title="Plugin permissions",
    )
    name: str = Field(
        description="Plugin name",
    )
    resources: List[str] = Field(
        description="Plugin specific resources",
    )


class Permissions(BaseModel):
    wms_services: List[WmsService] = Field(
        title="WMS services",
        description=(
            "Permitted WMS services and layers for all QWC services using "
            "WMS requests (i.e. OGC, FeatureInfo, Legend, Print service)."
        ),
    )
    wfs_services: List[WmsService] = Field(
        title="WFS services",
        description=("Permitted WFS services and layers for OGC service."),
    )
    background_layers: List[str] = Field(title="Background layers")
    data_datasets: List[Dataset] = Field(
        title="Data service datasets", description="Permitted datasets for Data service"
    )
    viewer_tasks: List[str] = Field(
        default_factory=list,
        title="Viewer tasks",
    )
    theme_info_links: List[str] = Field(
        default_factory=list,
        title="Theme info links",
    )
    plugin_data: List[PluginData] = Field(
        default_factory=list,
        title="Plugin data",
        description="Permitted resources for custom Map viewer plugins",
    )
    dataproducts: List[str] = Field(
        default_factory=list,
        title="Data-product service datasets",
    )
    document_templates: List[str] = Field(
        default_factory=list,
        title="Document service templates",
    )
    search_providers: List[str] = Field(
        default_factory=list,
        title="Search providers",
    )
    solr_facets: List[str] = Field(
        default_factory=list,
        title="Solr search facets",
    )


class Role(BaseModel):
    role: str = Field(
        description="Role name",
    )
    permissions: Permissions = Field(
        title="Permissions for role",
    )


class ServicesPermissions(BaseModel):
    """QWC Services Permissions."""

    model_config = ConfigDict(
        title="QWC Services Permissions",
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
            ServicesPermissions.model_json_schema(
                schema_generator=Generator,
            ),
            indent=2,
        )
    )
