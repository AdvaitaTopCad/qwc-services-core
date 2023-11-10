import json

from qwc_services_core.models.services_permissions import ServicesPermissions

FILE_CONTENT = """
{
  "users": [
    {
      "name": "admin",
      "groups": [],
      "roles": [
        "admin"
      ]
    },
    {
      "name": "demo",
      "groups": [],
      "roles": [
        "demo"
      ]
    }
  ],
  "groups": [],
  "roles": [
    {
      "role": "public",
      "permissions": {
        "wms_services": [
          {
            "name": "qwc_demo",
            "layers": [
              {
                "name": "qwc_demo"
              },
              {
                "name": "edit_demo"
              },
              {
                "name": "edit_points",
                "attributes": [
                  "id",
                  "name",
                  "description",
                  "num",
                  "value",
                  "type",
                  "amount",
                  "validated",
                  "datetime",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "edit_lines",
                "attributes": [
                  "id",
                  "name",
                  "description",
                  "num",
                  "value",
                  "type",
                  "amount",
                  "validated",
                  "datetime",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "edit_polygons",
                "attributes": [
                  "id",
                  "name",
                  "description",
                  "num",
                  "value",
                  "type",
                  "amount",
                  "validated",
                  "datetime",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "geographic_lines",
                "attributes": [
                  "ogc_fid",
                  "scalerank",
                  "name",
                  "name_long",
                  "abbrev",
                  "note",
                  "featurecla",
                  "min_zoom",
                  "wikidataid",
                  "name_ar",
                  "name_bn",
                  "name_de",
                  "name_en",
                  "name_es",
                  "name_fr",
                  "name_el",
                  "name_hi",
                  "name_hu",
                  "name_id",
                  "name_it",
                  "name_ja",
                  "name_ko",
                  "name_nl",
                  "name_pl",
                  "name_pt",
                  "name_ru",
                  "name_sv",
                  "name_tr",
                  "name_vi",
                  "name_zh",
                  "wdid_score",
                  "ne_id",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "country_names",
                "attributes": [
                  "ogc_fid",
                  "scalerank",
                  "labelrank",
                  "z_postal",
                  "z_abbrev",
                  "z_name",
                  "z_admin",
                  "featurecla",
                  "sovereignt",
                  "sov_a3",
                  "adm0_dif",
                  "level",
                  "type",
                  "admin",
                  "adm0_a3",
                  "geou_dif",
                  "name",
                  "abbrev",
                  "postal",
                  "name_forma",
                  "terr_",
                  "name_sort",
                  "map_color",
                  "pop_est",
                  "gdp_md_est",
                  "fips_10_",
                  "iso_a2",
                  "iso_a3",
                  "iso_n3",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "states_provinces",
                "attributes": [
                  "featurecla",
                  "name",
                  "adm0_a3",
                  "adm0_name",
                  "sov_a3",
                  "name_l",
                  "name_r",
                  "name_alt_l",
                  "name_alt_r",
                  "name_loc_l",
                  "name_loc_r",
                  "name_len_l",
                  "name_len_r",
                  "note",
                  "type",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "countries",
                "attributes": [
                  "featurecla",
                  "sovereignt",
                  "sov_a3",
                  "adm0_dif",
                  "level",
                  "type",
                  "admin",
                  "adm0_a3",
                  "geou_dif",
                  "geounit",
                  "gu_a3",
                  "su_dif",
                  "subunit",
                  "su_a3",
                  "brk_diff",
                  "name",
                  "name_long",
                  "brk_a3",
                  "brk_name",
                  "brk_group",
                  "abbrev",
                  "postal",
                  "formal_en",
                  "formal_fr",
                  "name_ciawf",
                  "note_adm0",
                  "note_brk",
                  "name_sort",
                  "name_alt",
                  "pop_est",
                  "pop_rank",
                  "gdp_md_est",
                  "pop_year",
                  "lastcensus",
                  "gdp_year",
                  "economy",
                  "income_grp",
                  "wikipedia",
                  "fips_10_",
                  "iso_a2",
                  "iso_a3",
                  "iso_a3_eh",
                  "iso_n3",
                  "un_a3",
                  "wb_a2",
                  "wb_a3",
                  "woe_id",
                  "woe_id_eh",
                  "woe_note",
                  "adm0_a3_is",
                  "adm0_a3_us",
                  "adm0_a3_un",
                  "adm0_a3_wb",
                  "continent",
                  "region_un",
                  "subregion",
                  "region_wb",
                  "name_len",
                  "long_len",
                  "abbrev_len",
                  "tiny",
                  "homepart",
                  "ne_id",
                  "wikidataid",
                  "name_ar",
                  "name_bn",
                  "name_de",
                  "name_en",
                  "name_es",
                  "name_fr",
                  "name_el",
                  "name_hi",
                  "name_hu",
                  "name_id",
                  "name_it",
                  "name_ja",
                  "name_ko",
                  "name_nl",
                  "name_pl",
                  "name_pt",
                  "name_ru",
                  "name_sv",
                  "name_tr",
                  "name_vi",
                  "name_zh",
                  "geometry",
                  "maptip"
                ]
              },
              {
                "name": "bluemarble_bg"
              },
              {
                "name": "osm_bg"
              }
            ],
            "print_templates": [
              "A4 Landscape"
            ]
          }
        ],
        "wfs_services": [],
        "background_layers": [
          "mapnik",
          "bluemarble"
        ],
        "data_datasets": [
          {
            "name": "qwc_demo.edit_lines",
            "attributes": [
              "name",
              "description",
              "num",
              "value",
              "type",
              "amount",
              "validated",
              "datetime"
            ],
            "writable": true,
            "creatable": true,
            "readable": true,
            "updatable": true,
            "deletable": true
          },
          {
            "name": "qwc_demo.edit_points",
            "attributes": [
              "name",
              "description",
              "num",
              "value",
              "type",
              "amount",
              "validated",
              "datetime"
            ],
            "writable": true,
            "creatable": true,
            "readable": true,
            "updatable": true,
            "deletable": true
          },
          {
            "name": "qwc_demo.edit_polygons",
            "attributes": [
              "name",
              "description",
              "num",
              "value",
              "type",
              "amount",
              "validated",
              "datetime"
            ],
            "writable": true,
            "creatable": true,
            "readable": true,
            "updatable": true,
            "deletable": true
          }
        ],
        "viewer_tasks": [],
        "theme_info_links": [],
        "plugin_data": [],
        "dataproducts": [
          "qwc_demo"
        ],
        "document_templates": [],
        "print_templates": [],
        "solr_facets": [
          "foreground",
          "ne_10m_admin_0_countries"
        ],
        "external_links": []
      }
    },
    {
      "role": "admin",
      "permissions": {
        "wms_services": [],
        "wfs_services": [],
        "background_layers": [],
        "data_datasets": [],
        "viewer_tasks": [],
        "theme_info_links": [],
        "plugin_data": [],
        "dataproducts": [],
        "document_templates": [],
        "print_templates": [],
        "solr_facets": [],
        "external_links": []
      }
    },
    {
      "role": "demo",
      "permissions": {
        "wms_services": [],
        "wfs_services": [],
        "background_layers": [],
        "data_datasets": [],
        "viewer_tasks": [],
        "theme_info_links": [],
        "plugin_data": [],
        "dataproducts": [],
        "document_templates": [],
        "print_templates": [],
        "solr_facets": [],
        "external_links": []
      }
    }
  ]
}
"""


def test_parsing():
    data = json.loads(FILE_CONTENT)
    result = ServicesPermissions.model_validate(data, strict=True)

    assert len(result.users) == 2
    assert len(result.groups) == 0
    assert len(result.roles) == 3

    assert result.users[0].name == "admin"
    assert result.users[0].roles == ["admin"]
    assert result.users[1].name == "demo"
    assert result.users[1].roles == ["demo"]

    assert result.roles[0].role == "public"
    assert len(result.roles[0].permissions.wms_services) == 1
    assert len(result.roles[0].permissions.wfs_services) == 0
    assert len(result.roles[0].permissions.background_layers) == 2
    assert len(result.roles[0].permissions.data_datasets) == 3
    assert len(result.roles[0].permissions.viewer_tasks) == 0
    assert len(result.roles[0].permissions.theme_info_links) == 0
    assert len(result.roles[0].permissions.plugin_data) == 0
    assert len(result.roles[0].permissions.dataproducts) == 1
    assert len(result.roles[0].permissions.document_templates) == 0
    assert len(result.roles[0].permissions.solr_facets) == 2
