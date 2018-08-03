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

from .tools import (
    generate_legend,
    validate_source_uri,
    is_file_path,
    layer_from_source)


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
        SOURCES=type=xyz&url=http://tile.osm.org/{z}/{x}/{y}.png?layers=osm;
            /path/1.shp;/path/2.shp;/path/3.asc&
        FILES={Legacy Name for Sources Parameter}
        NAMES=Layer 1;Layer 2;Layer 3&
        REMOVEQML=true&
        OVERWRITE=true&
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

            if exists(project_path) and overwrite:
                # Overwrite means create from scratch again
                remove(project_path)

            sources_parameters = params.get('SOURCES')
            # support legacy params: FILES
            if not sources_parameters:
                sources_parameters = params.get('FILES')

            if not sources_parameters:
                request.appendBody('SOURCES parameter is missing.\n')
                return

            sources = sources_parameters.split(';')
            for layer_source in sources:

                if not validate_source_uri(layer_source):
                    request.appendBody(
                        'invalid parameter: {0}.\n'.format(layer_source))
                    return

                if is_file_path(layer_source):
                    if not exists(layer_source):
                        request.appendBody('file not found : %s.\n' % layer_source)
                        return

            names_parameters = params.get('NAMES', None)
            if names_parameters:
                names = names_parameters.split(';')
                if len(names) != len(sources):
                    request.appendBody(
                        'Not same length between NAMES and SOURCES')
                    return
            else:
                names = [
                    splitext(basename(layer_source))[0]
                    for layer_source in sources]

            QgsMessageLog.logMessage('Setting up project to %s' % project_path)
            project = QgsProject.instance()
            project.setFileName(project_path)
            if exists(project_path) and not overwrite:
                project.read()

            qml_files = []
            qgis_layers = []
            vector_layers = []
            raster_layers = []

            for layer_name, layer_source in zip(names, sources):

                qgis_layer = layer_from_source(layer_source, layer_name)

                if not qgis_layer:
                    request.appendBody('Invalid format : %s' % layer_source)
                    return

                if not qgis_layer.isValid():
                    request.appendBody('Layer is not valid : %s' % layer_source)
                    return

                if isinstance(qgis_layer, QgsRasterLayer):
                    raster_layers.append(qgis_layer.id())
                elif isinstance(qgis_layer, QgsVectorLayer):
                    vector_layers.append(qgis_layer.id())
                else:
                    request.appendBody('Invalid type : {0} - {1}'.format(
                        qgis_layer, type(qgis_layer)))

                qgis_layers.append(qgis_layer)

                qml_file = splitext(layer_source)[0] + '.qml'
                if exists(qml_file):
                    # Check if there is a QML
                    qml_files.append(qml_file)

                style_manager = qgis_layer.styleManager()
                style_manager.renameStyle('', 'default')

            # Add layer to the registry
            if overwrite:
                # Insert all new layers
                QgsMapLayerRegistry.instance().addMapLayers(qgis_layers)
            else:
                # Updating rules
                # 1. Get existing layer by name
                # 2. Compare source, if it is the same, don't update
                # 3. If it is a new name, add it
                # 4. If same name but different source, then update

                map_registry = QgsMapLayerRegistry.instance()

                for new_layer in qgis_layers:
                    # Get existing layer by name
                    current_layer = map_registry.mapLayersByName(
                        new_layer.name())

                    # If it doesn't exists, add new layer
                    if not current_layer:
                        map_registry.addMapLayer(new_layer)
                    # If it is exists, compare source
                    else:
                        current_layer = current_layer[0]

                        # Same source, don't update
                        if current_layer.source() == new_layer.source():
                            if isinstance(new_layer, QgsVectorLayer):
                                vector_layers.remove(new_layer.id())
                                vector_layers.append(current_layer.id())
                            elif isinstance(new_layer, QgsRasterLayer):
                                raster_layers.remove(new_layer.id())
                                raster_layers.append(current_layer.id())

                        # Different source, update
                        else:
                            QgsMessageLog.logMessage('Update {0}'.format(
                                new_layer.name()))
                            if isinstance(new_layer, QgsVectorLayer):
                                project.removeEntry(
                                    'WFSLayersPrecision', '/{0}'.format(
                                        current_layer.id()))

                            map_registry.removeMapLayer(current_layer.id())
                            map_registry.addMapLayer(new_layer)

            if len(vector_layers):
                for layer_source in vector_layers:
                    project.writeEntry(
                        'WFSLayersPrecision', '/%s' % layer_source, 8)
                project.writeEntry('WFSLayers', '/', vector_layers)

            if len(raster_layers):
                project.writeEntry('WCSLayers', '/', raster_layers)

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
