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

from os.path import exists, splitext, basename, isfile
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)
from filters.tools import generate_legend


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

            files_parameters = params.get('FILES')
            if not files_parameters:
                request.appendBody('FILES is missing.\n')
                return

            files = files_parameters.split(';')
            for layer in files:
                if not exists(layer):
                    request.appendBody('file not found : %s.\n' % layer)
                    return

            QgsMessageLog.logMessage('Setting up project to %s' % project_path)
            project = QgsProject.instance()
            project.setFileName(project_path)

            qgis_layers = []
            vector_layers = []

            for layer in files:
                layer_name = splitext(basename(layer))[0]
                if layer.endswith(('shp', 'geojson')):
                    qgis_layer = QgsVectorLayer(layer, layer_name, 'ogr')
                    vector_layers.append(qgis_layer.id())

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

            if len(vector_layers):
                for layer in vector_layers:
                    project.writeEntry('WFSLayersPrecision', '/%s' % layer, 8)
                project.writeEntry('WFSLayers', '/', vector_layers)

            project.write()

            if not exists(project_path) and not isfile(project_path):
                request.appendBody(project.error())
                return

            generate_legend(qgis_layers, project_path)

            request.appendBody('OK')
