{
    "name": "Grafana",
    "version": "15.0.1.0.1",
    "author": "Daniel Kasprow",
    "license": "LGPL-3",
    "category": "Website",
    "depends": ["website" , "sale_management", "account", "website_sale"],
    "data": ["templates/main.xml"],
    "assets": {"web.assets_common": [
        "/grafana/static/src/js/website_manager_with_statistics.js",
        "/grafana/static/src/css/styles.css"
    ]},
    "demo": [],
    "installable": True,
    "application": True,
    "sequence": -100,
}
