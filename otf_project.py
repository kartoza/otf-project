# -*- coding: utf-8 -*-

from qgis.core import QgsMessageLog, QgsLogger
from filters.CreateOrReadProject import CreateOrReadProject

__author__ = 'Etienne Trimaille'
__date__ = '25/05/2016'


class OtfProjectServer:
    """Test plugin for QGIS server
    this plugin loads all filters from the 'filters' directory and logs
    errors"""

    def __init__(self, server_iface):
        QgsMessageLog.logMessage(
            'SUCCESS - OTF Project init', 'plugin', QgsMessageLog.INFO)

        filters = [CreateOrReadProject]
        for i, f in enumerate(filters):
            name = f.__name__
            try:
                server_iface.registerFilter(f(server_iface), i)
                QgsMessageLog.logMessage('OTF Project - loading %s' % name)
            except Exception, e:
                QgsMessageLog.logMessage(
                    'OTF Project - Error loading %s : %s' % (name, e))
