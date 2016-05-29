# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyDocstring,PyPep8Naming
def serverClassFactory(serverIface):
    from otf_project import OtfProjectServer
    return OtfProjectServer(serverIface)

