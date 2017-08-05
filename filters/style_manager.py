# -*- coding: utf-8 -*-

"""
***************************************************************************
    OTF QGIS Project
    ---------------------
    Date                 : July 2017
    Copyright            : (C) 2017 by Etienne Trimaille
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

from os.path import exists
from os import remove
from qgis.server import QgsServerFilter
from qgis.core import (
    QgsProject,
    QgsMapLayerStyle,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsVectorLayer,
    QgsRasterLayer)
from .tools import generate_legend


class StyleManager(QgsServerFilter):

    """Class to manage styles in a QGIS project."""

    def __init__(self, server_iface):
        super(StyleManager, self).__init__(server_iface)

    # noinspection PyPep8Naming
    def responseComplete(self):
        """Manage styles in a QGIS Project.

        Example :
        SERVICE=STYLEMANAGER&
        REQUEST=AddStyle&
        PROJECT=/destination/project.qgs&
        LAYER=myLayerId&
        QML=/path/to/style.qml&
        NAME=name of my style&
        REMOVEQML=true
        """
        QgsMessageLog.logMessage('StyleManager.responseComplete')
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        if params.get('SERVICE', '').upper() == 'STYLEMANAGER':
            request.clearHeaders()
            request.setHeader('Content-type', 'text/plain')
            request.clearBody()

            # PROJECT
            project_path = params.get('PROJECT')
            if not project_path:
                request.appendBody('PROJECT parameter is missing.\n')
                return
            if not exists(project_path):
                request.appendBody('PROJECT path does not exist.\n')
                return

            # REQUEST
            service = params.get('REQUEST')
            supported_services = [
                'AddStyle', 'RemoveStyle', 'GetStyle', 'SetDefaultStyle']
            if service not in supported_services:
                request.appendBody(
                    'REQUEST parameter is missing. Value must be in '
                    '%s.\n' % ','.join(supported_services))
                return

            # LAYER
            layer = params.get('LAYER')
            if not layer:
                request.appendBody(
                    'LAYER parameter is missing. It must be a layerid.')
                return
            project = QgsProject.instance()
            project.setFileName(project_path)
            result = project.read()
            if not result:
                request.appendBody(
                    'Error while reading the project : %s' % project.error())
                return

            maplayer_registry = QgsMapLayerRegistry.instance()
            qgis_layer = maplayer_registry.mapLayer(layer)
            if not qgis_layer:
                qgis_layer = maplayer_registry.mapLayersByName(layer)
                if len(qgis_layer) > 1:
                    request.appendBody(
                        'Two many layers for the same name. : %s' % layer)
                    return

                elif len(qgis_layer) == 0:
                    request.appendBody(
                        'LAYER value not found : %s' % layer)
                    return

                qgis_layer = qgis_layer[0]

            # NAME
            # Check default name should be `default` to follow GetCapabilities
            # response
            style_manager = qgis_layer.styleManager()
            if '' in style_manager.styles():
                style_manager.renameStyle('', 'default')
                project.write()
                # Make sure properties are saved.
                # So GetCapabilities are working.
                project.clear()

                # Reread project
                project.setFileName(project_path)
                project.read()

            name = params.get('NAME')
            if not name:
                request.appendBody('NAME parameter is missing.\n')
                return

            if service == 'AddStyle':
                return self.add_style(
                    name, params, project, project_path, qgis_layer, request)
            elif service == 'RemoveStyle':
                return self.remove_style(
                    name, project, project_path, qgis_layer, request)
            elif service == 'GetStyle':
                return self.get_style(name, qgis_layer, request)
            elif service == 'SetDefaultStyle':
                return self.set_default_style(
                    name, project, project_path, qgis_layer, request)

    @staticmethod
    def set_default_style(name, project, project_path, qgis_layer, request):
        """Set default style."""
        maplayer_registry = QgsMapLayerRegistry.instance()
        style_manager = qgis_layer.styleManager()
        if name not in style_manager.styles():
            request.appendBody('NAME is NOT an existing style.\n')
            return

        result = style_manager.setCurrentStyle(name)
        if not result:
            request.appendBody('Error while set the default style.\n')
            return

        project.write()
        project.clear()
        # The project has been overridden. We need to regenerate the legend
        # manually.
        qgis_layers = [
            layer for layer in maplayer_registry.mapLayers().itervalues()]
        generate_legend(qgis_layers, project_path)
        request.appendBody('OK')
        return True

    @staticmethod
    def get_style(name, qgis_layer, request):
        """Get the XML of a given style."""
        style_manager = qgis_layer.styleManager()
        if name not in style_manager.styles():
            request.appendBody('NAME is NOT an existing style.\n')
            return

        xml = style_manager.style(name).xmlData()
        request.setHeader('Content-type', 'text/xml')
        request.appendBody(xml)
        return True

    @staticmethod
    def remove_style(name, project, project_path, qgis_layer, request):
        """Remove a style to a layer."""
        maplayer_registry = QgsMapLayerRegistry.instance()
        style_manager = qgis_layer.styleManager()
        if name not in style_manager.styles():
            request.appendBody('NAME is NOT an existing style.\n')
            return

        result = style_manager.removeStyle(name)
        if not result:
            request.appendBody('Error while removing the style.\n')
            return

        project.write()
        project.clear()
        # The project has been overridden. We need to regenerate the legend
        # manually.
        qgis_layers = [
            layer for layer in maplayer_registry.mapLayers().itervalues()]
        generate_legend(qgis_layers, project_path)
        request.appendBody('OK')
        return True

    @staticmethod
    def add_style(name, params, project, project_path, qgis_layer, request):
        """Add a style to a layer in a QGIS project."""
        maplayer_registry = QgsMapLayerRegistry.instance()

        # QML
        qml_path = params.get('QML')
        if not qml_path:
            request.appendBody('QML parameter is missing.\n')
            return
        if not exists(qml_path):
            request.appendBody('QML path does not exist.\n')
            return

        # REMOVE QML
        remove_qml = params.get('REMOVEQML')
        if remove_qml:
            if remove_qml.upper() in ['1', 'YES', 'TRUE']:
                remove_qml = True
            else:
                remove_qml = False
        else:
            remove_qml = False
        style_manager = qgis_layer.styleManager()
        if name in style_manager.styles():
            request.appendBody('NAME is already an existing style.\n')
            return

        # Let's process the QML
        with open(qml_path, 'r') as qml_file:
            data = qml_file.read()
        style = QgsMapLayerStyle(data)
        if not style.isValid():
            request.appendBody('The QML is not valid.\n')
            return
        result = style_manager.addStyle(name, style)
        if not result:
            request.appendBody('Error while adding the style.\n')
            return
        project.write()
        project.clear()
        # The project has been overridden. We need to regenerate the legend
        # manually.
        qgis_layers = [
            layer for layer in maplayer_registry.mapLayers().itervalues()]
        generate_legend(qgis_layers, project_path)
        if remove_qml:
            QgsMessageLog.logMessage(
                'Removing QML {path}'.format(path=qml_path))
            remove(qml_path)
        request.appendBody('OK')
        return True
