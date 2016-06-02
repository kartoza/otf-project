# -*- coding: utf-8 -*-

"""
***************************************************************************
    QGIS Server Plugin Filters: say hello test filter, just logs calls and
    prints HelloServer! on plain text response
    ---------------------
    Date                 : October 2014
    Copyright            : (C) 2014-2015 by Alessandro Pasotti
    Email                : apasotti at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import xml.etree.ElementTree as ET
from os.path import exists, splitext, basename, isfile
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)


def generate_legend(layers, project):
    xml_string = '<legend updateDrawingOrder="true"> \n'
    for layer in layers:
        xml_string += '<legendlayer drawingOrder="-1" ' \
                      'open="true" checked="Qt::Checked" ' \
                      'name="%s" showFeatureCount="0"> \n' \
                      '<filegroup open="true" hidden="false"> \n' \
                      '<legendlayerfile isInOverview="0" ' \
                      'layerid="%s" visible="1"/> \n' \
                      '</filegroup>\n</legendlayer>\n' \
                      % (layer.name(), layer.id())
    xml_string += '</legend>\n'
    xml_legend = ET.fromstring(xml_string)
    document = ET.parse(project)
    xml_root = document.getroot()
    xml_root.append(xml_legend)
    document.write(project)


class MapComposition(QgsServerFilter):

    def __init__(self, server_iface):
        super(MapComposition, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def responseComplete(self):
        QgsMessageLog.logMessage('MapComposition.responseComplete')
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()
        if params.get('SERVICE', '').upper() == 'MAPCOMPOSITION':
            request.clearHeaders()
            request.setHeader('Content-type', 'text/plain')
            request.clearBody()

            project_path = params.get('PROJECT')
            if not project_path:
                request.appendBody('PROJECT is missing.\n')
                return

            if exists(project_path):
                msg = 'PROJECT is already existing : %s \n' % project_path
                request.appendBody(msg)
                return

            layers_parameters = params.get('LAYERS')
            if not layers_parameters:
                request.appendBody('LAYERS is missing.\n')
                return

            layers = layers_parameters.split(';')
            for layer in layers:
                if not exists(layer):
                    request.appendBody('layer not found : %s.\n' % layer)
                    return

            QgsMessageLog.logMessage('Setting up project to %s' % project_path)
            project = QgsProject.instance()
            project.setFileName(project_path)

            qgis_layers = []
            for layer in layers:
                layer_name = splitext(basename(layer))[0]
                if layer.endswith(('shp', 'geojson')):
                    qgis_layer = QgsVectorLayer(layer, layer_name, 'ogr')

                elif layer.endswith(('asc', 'tiff', 'tif')):
                    qgis_layer = QgsRasterLayer(layer, layer_name)
                else:
                    request.appendBody('Invalid format : %s' % layer)
                    return

                if not qgis_layer.isValid():
                    request.appendBody('Layer is not valid : %s' % layer)
                    return

                qgis_layers.append(qgis_layer)

                # Add layer to the registry
                QgsMapLayerRegistry.instance().addMapLayer(qgis_layer)

            project.write()

            if not exists(project_path) and not isfile(project_path):
                request.appendBody(project.error())
                return

            generate_legend(qgis_layers, project_path)

            request.appendBody('OK')
