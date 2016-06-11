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
import xml.etree.ElementTree as ET


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
