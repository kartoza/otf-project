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


from os.path import splitext, exists, isfile
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)


class HelloFilter(QgsServerFilter):

    def __init__(self, server_iface):
        super(HelloFilter, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def requestReady(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        map_file = params.get('MAP')

        if not map_file.endswith('qgs'):

            basename, _ = splitext(map_file)
            project = basename + '.qgs'

            if True:
                QgsMessageLog.logMessage('Setting up project to %s' % project)
                QgsProject.instance().setFileName(project)
                QgsMessageLog.logMessage(
                    'Project instance %s' % QgsProject.instance().fileName())

                if map_file.endswith(('shp', 'geojson')):
                    layer = QgsVectorLayer(map_file, 'layer', 'ogr')
                elif map_file.endswith(('asc', 'tiff', 'tif')):
                    layer = QgsRasterLayer(map_file, 'layer')
                else:
                    QgsMessageLog.logMessage('Invalid format : %s' % map_file)
                    return

                QgsMessageLog.logMessage(
                    'Layer is valid : %s' % layer.isValid())

                # Add layer to the registry
                QgsMapLayerRegistry.instance().addMapLayer(layer)
                QgsProject.instance().write()

                if not exists(project) and not isfile(project):
                    QgsMessageLog.logMessage(QgsProject.instance().error())
                    return

            del params['MAP']
            request.setParameter('MAP', project)

        else:
            QgsMessageLog.logMessage('QGIS Project existing.')
