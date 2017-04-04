# Create a QGIS project on the fly on the server

* Supported raster formats : asc, tif, tiff
* Supported vector formats : shp, geojson

**This project is still in development, the API may change.**

## Map composition service:
* This service will create a QGIS project using one or many layers existing on the file system.
* Parameters : 
  * SERVICE=MAPCOMPOSITION
  * PROJECT, path where the project will be written on the file system.
  * OVERWRITE, optional, false by default. Boolean if we can overwrite the existing PROJECT above. Values can be '1', 'YES', 'TRUE', 'yes', 'true'.
  * FILES is a list of files on the filesystem, separated by a semicolon.
  * NAMES is a list of names, separated by a semicolon. It will be used for the legend. Items in this list should match layers in the FILES list.

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

* This service will trigger the project creation. Then you can use the normal WMS/WFS service:

```
http://localhost:81/qgis?
SERVICE=WMS&
MAP=/destination/project.qgs&
REQUEST=GetCapabilities
```

## WMS and WFS services:

**This service is disabled by default. You need to enable it in otf_project.py.**
I prefer you to use the MAPCOMPOSITION service to create the project first.

* For the MAP parameter, if we use a qgs file, the request will be forwarded to QGIS Server. However, if the MAP parameter is one of the supported formats, the plugin will create the project on the fly and then the request will be forwarded to QGIS Server.

* Vector example :
`http://localhost:81/qgis?MAP=/path/to/shapefile.shp&SERVICE=WMS&REQUEST=GetCapabilities`
This request will create a WMS/WFS project /path/to/shapefile.qgs

* Raster example :
`http://localhost:81/qgis?MAP=/path/to/raster.asc&SERVICE=WMS&REQUEST=GetCapabilities`
This request will create a WMS project /path/to/raster.qgs


## Todo
* Add WCS
* Add tests