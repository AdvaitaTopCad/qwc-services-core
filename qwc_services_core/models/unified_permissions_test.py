import json

from qwc_services_core.models.unified_permissions import UnifiedServicesPermissions

FILE_CONTENT = """
{
    "users": [
        {
            "name": "user1",
            "groups": ["group1"],
            "roles": ["role1"]
        }
    ],
    "groups": [
        {
            "name": "group1",
            "roles": ["role1"]
        }
    ],
    "roles": [],
    "wms_name": "wms1",
    "wfs_name": "wfs1",
    "dataproducts": [
        {
            "name": "layer1",
            "attributes": ["attr1", "attr2"]
        },
        {
            "name": "group_layer1",
            "sublayers": ["layer2", "layer3"]
        }
    ],
    "common_resources": ["resource1"]
}
"""


def test_parse():
    # TODO: find a real file in the wild.
    data = json.loads(FILE_CONTENT)
    result = UnifiedServicesPermissions.model_validate(data, strict=True)

    assert len(result.users) == 1
    assert len(result.groups) == 1
    assert len(result.roles) == 0
