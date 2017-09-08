# -*- coding: utf-8 -*-

"""
***************************************************************************
    OTF QGIS Project
    ---------------------
    Date                 : June 2016
    Copyright            : (C) 2016 by Etienne Trimaille
    Email                : etienne at kartoza dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import tempfile

from os import remove
from json import loads
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)
from .tools import generate_legend


class LayerDefinition(QgsServerFilter):

    """Class to create a QLR file, or a project."""

    def __init__(self, server_iface):
        super(LayerDefinition, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def responseComplete(self):
        """Create a QLR file.

        Example :
        SERVICE=LAYERDEFINITIONS&
        LAYERS=[
           {
             'type': 'raster',
             'display':'layer name 1'
             'driver':'wms'
             'crs': 'EPSG:4326'
             'format': 'image/png'
             'styles': ''
             'layers': 'layer 1'
             'url': 'http://wms-end-point'
           },
        ]

        Parameters to load the layer in QGIS are the first 3 ones:
        Param type: It's the layer type: 'raster' or 'vector'.
        Param display: The name of the layer in the legend.
        Param driver: The driver to use in QGIS: wms, ogr, wfs, ...

        Parameters if it's a WMS call:
        Param layers: Name of layers to add in the WMS call for instance

        Be careful, the LAYER variable need is a JSON string HTML encoded.

        This will return the QLR as an XML string.
        """
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        if params.get('SERVICE', '').upper() == 'LAYERDEFINITIONS':
            request.clearHeaders()
            request.setHeader('Content-type', 'text/plain')
            request.clearBody()

            layers = params.get('LAYERS')
            if not layers:
                request.appendBody('LAYERS parameter is missing.\n')
                return

            try:
                layers = loads(layers)
            except Exception as e:
                QgsMessageLog.logMessage(str(e))

            final_layers = []
            for layer in layers:
                query_string = ''
                for key in layer.keys():
                    query_string += key + '=' + layer[key] + '&'

                if layer['type'] == 'vector':
                    qgis_layer = QgsVectorLayer(
                        query_string, layer['display'], layer['driver'])
                else:
                    qgis_layer = QgsRasterLayer(
                        query_string, layer['display'], layer['driver'])

                if not qgis_layer.isValid():
                    request.appendBody(
                        'One layer is invalid: %s.\n' % query_string)
                    return

                QgsMapLayerRegistry.instance().addMapLayer(qgis_layer)
                final_layers.append(qgis_layer)

            qlr = final_layers[0].asLayerDefinition(final_layers).toString()

            request.appendBody(qlr)

        elif params.get('SERVICE', '').upper() == 'PROJECTDEFINITIONS':

            request.clearHeaders()
            request.setHeader('Content-type', 'text/plain')
            request.clearBody()

            layers = params.get('LAYERS')
            if not layers:
                request.appendBody('LAYERS parameter is missing.\n')
                return

            try:
                layers = loads(layers)
            except Exception as e:
                QgsMessageLog.logMessage(str(e))

            final_layers = []
            for layer in layers:
                query_string = ''
                for key in layer.keys():
                    query_string += key + '=' + layer[key] + '&'

                if layer['type'] == 'vector':
                    qgis_layer = QgsVectorLayer(
                        query_string, layer['display'], layer['driver'])
                else:
                    qgis_layer = QgsRasterLayer(
                        query_string, layer['display'], layer['driver'])

                if not qgis_layer.isValid():
                    request.appendBody(
                        'One layer is invalid: %s.\n' % query_string)
                    return

                QgsMapLayerRegistry.instance().addMapLayer(qgis_layer)

            project_path = tempfile.NamedTemporaryFile(
                suffix='.qgs', delete=False)
            project_path.close()
            project_path = project_path.name
            project = QgsProject.instance()
            project.setFileName(project_path)

            project.write()
            project.clear()

            generate_legend(final_layers, project_path)

            with open(project_path, 'r') as qgis_project:
                xml_data = qgis_project.read()
                request.appendBody(xml_data)

            remove(project_path)
