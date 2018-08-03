# Create a QGIS project on the fly on the server

* Supported raster formats : asc, tif, tiff, geotiff, geotif
* Supported vector formats : shp, geojson

**This project is still in development, the API may change.**

## Map composition service:
* This service will create a QGIS project using one or many layers existing on the file system.
* Parameters : 
  * SERVICE=MAPCOMPOSITION, compulsory
  * PROJECT, compulsory, path where the project will be written on the file system.
  * SOURCES, compulsory, it's a list of layer sources. It can be tile url or QGIS DataSource URI or files on the filesystem, separated by a semicolon.
  	Especially for QGIS DataSource URI, it must be url quoted twice (first the url, second the whole datasource string).
  * FILES, optional, legacy parameter, it's a list of files on the filesystem, separated by a semicolon. It is overriden by SOURCES.
  * NAMES, compulsory, it's a list of names, separated by a semicolon. It will be used for the legend. Items in this list should match layers in the FILES list.
  * OVERWRITE, optional, false by default. Boolean if we can overwrite the existing PROJECT above. Values can be '1', 'YES', 'TRUE', 'yes', 'true'.
  * REMOVEQML, optional, false by default. Boolean if we can remove the QML. The style is already in the QGS file. Values can be '1', 'YES', 'TRUE', 'yes', 'true'.


Layers need to be stored on the server's filesystem. The project will be created at the specified path above, on the server's filesystem too.

* For the answer you should get `OK` or you will get the error message.

* Example :
```
http://localhost:81/qgis?
SERVICE=MAPCOMPOSITION&
PROJECT=/destination/project.qgs&
FILES=/path/1.shp;/path/2.geojson;/path/3.asc&
NAMES=My layer 1;MyLayer 2;Layer 3&
OVERWRITE=true
```

* This URL above will trigger the project creation. Then you can use the normal WMS/WFS service:

```
http://localhost:81/qgis?
SERVICE=WMS&
MAP=/destination/project.qgs&
REQUEST=GetCapabilities
```

* Example of using SOURCES with tile URI:

```
http://localhost:81/qgis?
SERVICE=MAPCOMPOSITION&
PROJECT=/destination/project.qgs&
SOURCES=type%253Dxyz%2526url%253Dhttp%25253A%2F%2Fa.tile.osm.org%2F%25257Bz%25257D%2F%25257Bx%25257D%2F%25257By%25257D.png;/path/1.shp;/path/2.geojson;/path/3.asc&
NAMES=Basemap;My layer 1;MyLayer 2;Layer 3&
OVERWRITE=true
```

In the sample request above, note that the datasource: ```type%253Dxyz%2526url%253Dhttp%25253A%2F%2Fa.tile.osm.org%2F%25257Bz%25257D%2F%25257Bx%25257D%2F%25257By%25257D.png``` were urlquoted twice.
The actual datasource is: ```type=xyz&url=http%3A//a.tile.osm.org/%7Bz%7D/%7Bx%7D/%7By%7D.png```
Note that the actual url is: ```http://a.tile.osm.org/{z}/{x}/{y}.png```

Thus in order to send the request, the url needs to be quoted first before it was inserted into datasource uri (to quote & symbol and = from url).
Then, the datasource needs to be quoted again, because it was sent via GET requests url (to quote & symbol and = from datasource query params).

As an example of sending your datasource of base layer:

Quote your tile url:

```
>>> tile_url = 'http://a.tile.osm.org/{z}/{x}/{y}.png'
>>> from requests.utils import quote
>>> tile_url = quote(tile_url)
```

Then build your data source definition and quote it:

```
>>> definition = {
...   'url': tile_url,
...   'type': 'xyz'
... }
>>> datasource = '&'.join(['{key}={value}'.format(key=key,value=value) for key,value in definition.iteritems()])
'url=http%3A//a.tile.osm.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&type=xyz'
>>> quoted_datasource = quote(datasource)
'url%3Dhttp%253A//a.tile.osm.org/%257Bz%257D/%257Bx%257D/%257By%257D.png%26type%3Dxyz'
```

## Todo
* Add WCS
* Add tests

# Manage styles for a layer

* Parameters, add a new style to a layer:
  * SERVICE=STYLEMANAGER, compulsory
  * REQUEST=AddStyle, compulsory
  * PROJECT=/destination/project.qgs, compulsory, path to the QGIS project
  * LAYER=myLayerName, compulsory, name of the layer
  * QML=/path/to/style.qml, compulsory, path to the QML
  * NAME=name of my style, compulsory, name of the style in the QGIS settings
  * REMOVEQML=true, optional, if we should remove the QML after the process. The QML is already stored in the QGIS project.
* Parameters for removing a style:
  * SERVICE=STYLEMANAGER, compulsory
  * REQUEST=RemoveStyle, compulsory
  * PROJECT=/destination/project.qgs, compulsory, path to the QGIS project
  * LAYER=myLayerName, compulsory, name of the layer
  * NAME=name of my style, compulsory, name of the style in the QGIS settings
* Parameters for getting the QML as XML:
  * SERVICE=STYLEMANAGER, compulsory
  * REQUEST=GetStyle, compulsory
  * PROJECT=/destination/project.qgs, compulsory, path to the QGIS project
  * LAYER=myLayerName, compulsory, name of the layer
  * NAME=name of my style, compulsory, name of the style in the QGIS settings
* Parameters for setting an existing style as default:
  * SERVICE=STYLEMANAGER, compulsory
  * REQUEST=SetDefaultStyle, compulsory
  * PROJECT=/destination/project.qgs, compulsory, path to the QGIS project
  * LAYER=myLayerName, compulsory, name of the layer
  * NAME=name of my style, compulsory, name of the style in the QGIS settings

# Create QGIS Layer Definitions Files or a QGIS project

Create your structure like this and encode it:
```
>>> from json import dumps
>>> from requests.utils import quote
>>> layers = [{
...   'type':'raster',
...   'display':'layer name 1',
...   'driver': 'wms',
...   'crs':'EPSG:4326', 'format':'image/png', 'styles':'', 'layers':'tmpeqfzkt', 'url':'http://staging.geonode.kartoza.com/qgis-server/ogc/tmpeqfzkt'}
...   ]
>>> query_string = quote(layers)
```
* You can add as many layers as you want in the list.
* 'type', 'display', 'driver' are specific for QGIS. Other parameters are specific for the driver to be able to open the layer.

Then make a request with:
```
http://localhost:81/qgis?
SERVICE=LAYERDEFINITIONS&
LAYERS=your_quoted_layers_variable
```

* You will get a XML string for the QLR.

* Same kind of request to get a QGIS Project instead of a QLR. Replace `LAYERDEFINITIONS` in the URL by `PROJECTDEFINITIONS`.

# Development

* The quickest way to use QGIS Server with the command line with docker. No need to relaunch something.
```
docker pull kartoza/qgis-server:LTR
QUERY_STRING="SERVICE=STYLEMANAGER&PROJECT=/usr/src/app/geonode/qgis_layer/small_building.qgs&REQUEST=GetStyle&LAYER=build&NAME=toto" /usr/lib/cgi-bin/qgis_mapserv.fcgi
```
