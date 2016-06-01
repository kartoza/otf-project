# -*- coding: utf-8 -*-

from qgis.core import QgsMessageLog, QgsLogger

__author__ = 'Etienne Trimaille'
__date__ = '25/05/2016'


class OtfProjectServer:
    """Test plugin for QGIS server
    this plugin loads all filters from the 'filters' directory and logs
    errors"""

    def __init__(self, server_iface):
        # Save reference to the QGIS server interface
        self.server_iface = server_iface
        import filters
        priority = 1

        QgsMessageLog.logMessage(
            'SUCCESS - OTF Project init', 'plugin', QgsMessageLog.INFO)

        for filter_name in filters.local_modules:
            QgsLogger.debug('OTF Project - loading filter %s' % filter_name)

            try:
                server_iface.registerFilter(
                    getattr(filters, filter_name)(server_iface),
                    priority * 100)
                priority += 1
            except Exception, e:
                QgsLogger.debug(
                    'OTF Project - Error loading filter %s : %s'
                    % (filter_name, e))
