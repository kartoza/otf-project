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
from os.path import splitext, exists, isfile, basename
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


class CreateProject(QgsServerFilter):

    def __init__(self, server_iface):
        super(CreateProject, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def requestReady(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        map_file = params.get('MAP')
        layer_name = params.get('LAYERS')
        if layer_name is None:
            layer_name = params.get('LAYER')

        if params.get('SERVICE', '').upper() in ['WMS', 'WCS', 'WFS']:
            if not map_file.endswith('qgs'):

                project = splitext(map_file)[0] + '.qgs'
                file_name = splitext(basename(map_file))[0]
                if layer_name is None:
                    layer_name = file_name

                if not exists(project) and not isfile(project):
                    QgsMessageLog.logMessage(
                        'Setting up project to %s' % project)
                    qgis_project = QgsProject.instance()
                    qgis_project.setFileName(project)
                    QgsMessageLog.logMessage(
                        'Project instance %s' % qgis_project.fileName())

                    if map_file.endswith(('shp', 'geojson')):
                        layer = QgsVectorLayer(map_file, layer_name, 'ogr')

                        layer_id = layer.id()
                        # We need to enable WFS, adapted from the QGIS repo :
                        # https://github.com/qgis/QGIS/blob/master/src/app/
                        # qgsprojectproperties.cpp#L1109
                        qgis_project.writeEntry(
                            'WFSLayersPrecision', '/%s' % layer_id, 8)
                        qgis_project.writeEntry('WFSLayers', '/', [layer_id])

                    elif map_file.endswith(('asc', 'tiff', 'tif')):
                        layer = QgsRasterLayer(map_file, layer_name)
                    else:
                        QgsMessageLog.logMessage(
                            'Invalid format : %s' % map_file)
                        return

                    QgsMessageLog.logMessage(
                        'Layer is valid : %s' % layer.isValid())

                    # Add layer to the registry
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    qgis_project.write()

                    if not exists(project) and not isfile(project):
                        QgsMessageLog.logMessage(qgis_project.error())
                        return

                    layers = [layer]
                    # QGIS don't put the legend because we are on a server.
                    # We need to add manually.
                    generate_legend(layers, project)

                del params['MAP']
                request.setParameter('MAP', project)

            else:
                QgsMessageLog.logMessage('QGIS Project existing.')
