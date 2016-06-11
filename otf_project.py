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

from qgis.core import QgsMessageLog, QgsLogger
# from filters.create_project import CreateProject
from filters.map_composition import MapComposition

__author__ = 'Etienne Trimaille'
__date__ = '25/05/2016'


class OtfProjectServer:
    """Test plugin for QGIS server
    this plugin loads all filters from the 'filters' directory and logs
    errors"""

    def __init__(self, server_iface):
        QgsMessageLog.logMessage(
            'SUCCESS - OTF Project init', 'plugin', QgsMessageLog.INFO)

        filters = [MapComposition]
        for i, f in enumerate(filters):
            name = f.__name__
            try:
                server_iface.registerFilter(f(server_iface), i)
                QgsMessageLog.logMessage('OTF Project - loading %s' % name)
            except Exception, e:
                QgsMessageLog.logMessage(
                    'OTF Project - Error loading %s : %s' % (name, e))
