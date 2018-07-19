# Create a QGIS project on the fly on the server

* Supported raster formats : asc, tif, tiff
* Supported vector formats : shp, geojson

**This project is still in development, the API may change.**

## Map composition service:
* This service will create a QGIS project using one or many layers existing on the file system.
* Parameters : 
  * SERVICE=MAPCOMPOSITION, compulsory
  * PROJECT, compulsory, path where the project will be written on the file system.
  * FILES, compulsory, it's a list of files on the filesystem, separated by a semicolon.
  * NAMES, compulsory, it's a list of names, separated by a semicolon. It will be used for the legend. Items in this list should match layers in the FILES list.
  * OVERWRITE, optional, false by default. Boolean if we can overwrite the existing PROJECT above. Values can be '1', 'YES', 'TRUE', 'yes', 'true'.
  * REMOVEQML, optional, false by default. Boolean if we can remove the QML. The style is already in the QGS file. Values can be '1', 'YES', 'TRUE', 'yes', 'true'.
  * BASEMAP, optional, None by default. it's a list of string comprised of a tile url and its service name, separated by a semicolon.


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