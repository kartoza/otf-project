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

import unittest
import commands

QGIS_SERVER = '/usr/local/qgis_stable/bin/qgis_mapserv.fcgi'
TEST_DATA = '/home/etienne/kartoza_dev/server_plugins/otf-project/test/data/'


class TestServerPlugin(unittest.TestCase):

    def request(self, query_string):

        self.string = "QUERY_STRING='"
        for param, value in query_string.iteritems():
            if param == 'MAP':
                value = TEST_DATA + value
            self.string += param + '=' + value + '&'
        self.string += "'"

        command = self.string + ' ' + QGIS_SERVER
        _, output = commands.getstatusoutput(command)

        return output
