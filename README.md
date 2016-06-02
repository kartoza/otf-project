# Create a QGIS project on the fly on the server

* Supported raster formats : asc, tif, tiff
* Supported vector formats : shp, geojson

## WMS and WFS :
* For the MAP parameter, if we use a qgs file, the request will be forwarded to QGIS Server. However, if the MAP parameter is one of the supported formats, the plugin will create the project on the fly and then the request will be forwarded to QGIS Server.

* Vector example :
`http://localhost:81/qgis?MAP=/path/to/shapefile.shp&SERVICE=WMS&REQUEST=GetCapabilities`
This request will create a WMS/WFS project /path/to/shapefile.qgs

* Raster example :
`http://localhost:81/qgis?MAP=/path/to/raster.asc&SERVICE=WMS&REQUEST=GetCapabilities`
This request will create a WMS project /path/to/raster.qgs

## Map composition :
* This service will create a map composition using multiple layers.
* Parameters : 
  * SERVICE=MAPCOMPOSITION
  * PROJECT where the project will be written. The file shouldn't exist.
  * LAYERS is a list of file, separated by a semicolon
* For the answer you should get `OK` or you will get the error message.

* Example :
`http://localhost:81/qgis?SERVICE=MAPCOMPOSITION&PROJECT=/path/to/project.qgs&LAYERS=/path/to/shape.shp;/path/to/raster.tif`

* This service will trigger the project creation. Then you can use the normal WMS/WFS service.

## Todo
* Add WCS
* Add tests