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


class CreateOrReadProjectFilter(QgsServerFilter):

    def __init__(self, server_iface):
        super(CreateOrReadProjectFilter, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def requestReady(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        map_file = params.get('MAP')

        if not map_file.endswith('qgs'):

            project = splitext(map_file)[0] + '.qgs'
            file_name = splitext(basename(map_file))[0]

            if not exists(project) and not isfile(project):
                QgsMessageLog.logMessage('Setting up project to %s' % project)
                qgis_project = QgsProject.instance()
                qgis_project.setFileName(project)
                QgsMessageLog.logMessage(
                    'Project instance %s' % qgis_project.fileName())

                if map_file.endswith(('shp', 'geojson')):
                    layer = QgsVectorLayer(map_file, file_name, 'ogr')
                elif map_file.endswith(('asc', 'tiff', 'tif')):
                    layer = QgsRasterLayer(map_file, 'layer')
                else:
                    QgsMessageLog.logMessage('Invalid format : %s' % map_file)
                    return

                QgsMessageLog.logMessage(
                    'Layer is valid : %s' % layer.isValid())

                # Add layer to the registry
                QgsMapLayerRegistry.instance().addMapLayer(layer)
                qgis_project.write()

                if not exists(project) and not isfile(project):
                    QgsMessageLog.logMessage(qgis_project.error())
                    return

                # QGIS do not put the legend node because we are on a server.
                # We need to add manually.
                xml_string = '<legend updateDrawingOrder="true"> \n' \
                             '<legendlayer drawingOrder="-1" open="true" ' \
                             'checked="Qt::Checked" name="%s"' \
                             ' showFeatureCount="0"> \n' \
                             '<filegroup open="true" hidden="false"> \n' \
                             '<legendlayerfile isInOverview="0" ' \
                             'layerid="%s" visible="1"/> \n' \
                             '</filegroup>\n</legendlayer>\n' \
                             '</legend>\n' % (file_name, layer.id())
                xml_legend = ET.fromstring(xml_string)

                document = ET.parse(project)
                xml_root = document.getroot()
                xml_root.append(xml_legend)
                document.write(project)

            del params['MAP']
            request.setParameter('MAP', project)

        else:
            QgsMessageLog.logMessage('QGIS Project existing.')
