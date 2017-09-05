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
from os import remove
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)
from .tools import generate_legend


class MapComposition(QgsServerFilter):

    """Class to create a QGIS Project with one or many layers."""

    def __init__(self, server_iface):
        super(MapComposition, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def responseComplete(self):
        """Create a QGIS Project.

        Example :
        SERVICE=MAPCOMPOSITION&
        PROJECT=/destination/project.qgs&
        FILES=/path/1.shp;/path/2.shp;/path/3.asc&
        NAMES=Layer 1;Layer 2;Layer 3&
        REMOVEQML=true&
        OVERWRITE=true
        """
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        if params.get('SERVICE', '').upper() == 'MAPCOMPOSITION':
            request.clearHeaders()
            request.setHeader('Content-type', 'text/plain')
            request.clearBody()

            project_path = params.get('PROJECT')
            if not project_path:
                request.appendBody('PROJECT parameter is missing.\n')
                return

            overwrite = params.get('OVERWRITE')
            if overwrite:
                if overwrite.upper() in ['1', 'YES', 'TRUE']:
                    overwrite = True
                else:
                    overwrite = False
            else:
                overwrite = False

            remove_qml = params.get('REMOVEQML')
            if remove_qml:
                if remove_qml.upper() in ['1', 'YES', 'TRUE']:
                    remove_qml = True
                else:
                    remove_qml = False
            else:
                remove_qml = False

            if exists(project_path):
                if not overwrite:
                    msg = 'PROJECT is already existing : %s \n' % project_path
                    request.appendBody(msg)
                    return
                else:
                    remove(project_path)

            files_parameters = params.get('FILES')
            if not files_parameters:
                request.appendBody('FILES parameter is missing.\n')
                return

            files = files_parameters.split(';')
            for layer_file in files:
                if not exists(layer_file):
                    request.appendBody('file not found : %s.\n' % layer_file)
                    return

            names_parameters = params.get('NAMES', None)
            if names_parameters:
                names = names_parameters.split(';')
                if len(names) != len(files):
                    request.appendBody(
                        'Not same length between NAMES and FILES')
                    return
            else:
                names = [
                    splitext(basename(layer_file))[0] for layer_file in files]

            QgsMessageLog.logMessage('Setting up project to %s' % project_path)
            project = QgsProject.instance()
            project.setFileName(project_path)

            qml_files = []
            qgis_layers = []
            vector_layers = []
            raster_layer = []

            for layer_name, layer_file in zip(names, files):
                if layer_file.endswith(('shp', 'geojson')):
                    qgis_layer = QgsVectorLayer(layer_file, layer_name, 'ogr')
                    vector_layers.append(qgis_layer.id())

                elif layer_file.endswith(('asc', 'tiff', 'tif')):
                    qgis_layer = QgsRasterLayer(layer_file, layer_name)
                    raster_layer.append(qgis_layer.id())
                else:
                    request.appendBody('Invalid format : %s' % layer_file)
                    return

                if not qgis_layer.isValid():
                    request.appendBody('Layer is not valid : %s' % layer_file)
                    return

                qgis_layers.append(qgis_layer)

                qml_file = splitext(layer_file)[0] + '.qml'
                if exists(qml_file):
                    # Check if there is a QML
                    qml_files.append(qml_file)

                style_manager = qgis_layer.styleManager()
                style_manager.renameStyle('', 'default')

                # Add layer to the registry
                QgsMapLayerRegistry.instance().addMapLayer(qgis_layer)

            if len(vector_layers):
                for layer_file in vector_layers:
                    project.writeEntry(
                        'WFSLayersPrecision', '/%s' % layer_file, 8)
                project.writeEntry('WFSLayers', '/', vector_layers)

            if len(raster_layer):
                project.writeEntry('WCSLayers', '/', raster_layer)

            project.write()
            project.clear()

            if not exists(project_path) and not isfile(project_path):
                request.appendBody(project.error())
                return

            generate_legend(qgis_layers, project_path)

            if remove_qml:
                for qml in qml_files:
                    QgsMessageLog.logMessage(
                        'Removing QML {path}'.format(path=qml))
                    remove(qml)

            request.appendBody('OK')
