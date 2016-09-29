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

from .base_test import TestServerPlugin
TEST_DATA = '/home/etienne/kartoza_dev/server_plugins/otf-project/test/data/'


class TestCreateProject(TestServerPlugin):

    def test_load_raster(self):

        query_string = {
            'SERVICE': 'WMS',
            'REQUEST': 'GetCapabilities',
            'MAP': 'tsunami_wgs84.tif'
        }

        result = self.request(query_string)
        print result

    def test_map_composition(self):

        files = TEST_DATA + 'buildings.shp;' + TEST_DATA + 'tsunami_wgs84.tif'

        query_string = {
            'SERVICE': 'MAPCOMPOSITION',
            'OVERWRITE': 'true',
            'PROJECT': '/tmp/project.qgs',
            'FILES': files,
            'NAMES': 'toto;titi'
        }
        result = self.request(query_string)
        print result
