# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SGBTools
                                 A QGIS plugin
 Ferramentas SGB
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-10-30
        copyright            : (C) 2024 by Carlos Eduardo Mota
        email                : carlos.mota@sgb.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Carlos Eduardo Mota'
__date__ = '2024-10-30'
__copyright__ = '(C) 2024 by Carlos Eduardo Mota'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingOutputBoolean,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem,
                       QgsLayerMetadata,
                       QgsAbstractMetadataBase,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterMultipleLayers)
from owslib import iso, etree
#owslib is spitting a lot of future change warnings those will be ignored
#for now
import warnings
warnings.filterwarnings('ignore', module='owslib')

def createSpatialExtent(
        bbox_rect:QgsRectangle,
        bbox_crs:QgsCoordinateReferenceSystem)->QgsLayerMetadata.Extent:
    spatial_extent = QgsLayerMetadata.SpatialExtent()
    spatial_extent.bounds.setXMinimum(bbox_rect.xMinimum())
    spatial_extent.bounds.setYMinimum(bbox_rect.yMinimum())
    spatial_extent.bounds.setXMaximum(bbox_rect.xMaximum())
    spatial_extent.bounds.setYMaximum(bbox_rect.yMaximum())
    spatial_extent.extentCrs = bbox_crs

    md_extent = QgsLayerMetadata.Extent()
    md_extent.setSpatialExtents([spatial_extent])
    return md_extent


class ImportISOMetadataAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm takes an .xml ISO-19115 metadata file and apply to the
    QGIS layer metadata for each selected layer.
    """

    INPUTMAPLAYERLIST = 'INPUTMAPLAYERLIST'
    INPUTXML = 'INPUTXML'
    OUTPUT = 'OUTPUT'

    COPYEXTENT = 'COPYEXTENT'
    COPYTYPE = 'COPYTYPE'

    category_dict = {
        'biota': 'Biota',
        'boundaries': 'Boundaries',
        'climatologyMeteorologyAtmosphere': 'Climatology Meteorology Atmosphere',
        'economy': 'Economy',
        'elevation': 'Elevation',
        'environment': 'Environment',
        'farming': 'Farming',
        'geoscientificInformation': 'Geoscientific Information',
        'health': 'Health',
        'imageryBaseMapsEarthCover': 'Imagery Base Maps Earth Cover',
        'inlandWaters': 'Inland Waters',
        'intelligenceMilitary': 'Intelligence Military',
        'location': 'Location',
        'oceans': 'Oceans',
        'planningCadastre': 'Planning Cadastre',
        'society': 'Society',
        'structure': 'Structure',
        'transportation': 'Transportation',
        'utilitiesCommunication': 'Utilities Communication'
    }

    crs_dict = {
        'WGS84':'EPSG:4326',
        'SIRGAS2000':'EPSG:4674',
        'SAD1969':'EPSG:4618',
        'CORREGOALEGRE':'EPSG:4225'
    }

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        layerlist_parameter = QgsProcessingParameterMultipleLayers(
                self.INPUTMAPLAYERLIST,
                self.tr('Layers to import metadata to')
            )
        layerlist_parameter.setMinimumNumberInputs(1)
        self.addParameter(layerlist_parameter)

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUTXML,
                self.tr('Input .xml file')
            )
        )

        self.addOutput(
            QgsProcessingOutputBoolean(
                self.OUTPUT,
                self.tr('Return code')
            )
        )

        extent_parameter = QgsProcessingParameterBoolean(
                self.COPYEXTENT,
                self.tr('Get extent from metadata file'),
                defaultValue=False,
            )
        extent_parameter.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(extent_parameter)

        type_parameter = QgsProcessingParameterBoolean(
                self.COPYTYPE,
                self.tr('Get data type from metadata file'),
                defaultValue=False,
            )
        type_parameter.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(type_parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        xml_file = self.parameterAsFile(parameters, self.INPUTXML, context)
        file_metadata = iso.MD_Metadata(etree.etree.parse(xml_file))
        identification = file_metadata.identification
        props_dict={}
        for prop in dir(identification):
            if prop.startswith('_'):
                continue
            props_dict[prop]=identification.__getattribute__(prop)
        
        for layer in self.parameterAsLayerList(parameters,
                                               self.INPUTMAPLAYERLIST,context):
            #layer = self.parameterAsLayer(parameters, self.INPUTMAPLAYER, context)
            metadata = layer.metadata()

            #Identifier
            metadata.setIdentifier(file_metadata.identifier)

            #Title
            metadata.setTitle(props_dict['title'])

            #Abstract
            metadata.setAbstract(props_dict['abstract'])
            
            #Topic Category
            metadata.setCategories([self.category_dict[category]
                                    for category in props_dict['topiccategory']])
            
            #Bounding box
            #spatial extent and temporal extent are defined together
            #For now ignoring temporal extent
            if self.parameterAsBool(parameters,self.COPYEXTENT,context):
                xml_bbox = props_dict['bbox']
                bbox_rect = QgsRectangle(float(xml_bbox.minx),
                                        float(xml_bbox.miny),
                                        float(xml_bbox.maxx),
                                        float(xml_bbox.maxy))
                bbox_crs = QgsCoordinateReferenceSystem(
                    self.crs_dict[file_metadata.referencesystem.code])
            else:
                bbox_rect = layer.extent()
                bbox_crs = layer.crs()

            md_extent = createSpatialExtent(bbox_rect,bbox_crs)
            metadata.setExtent(md_extent)

            #Contacts
            xml_contact_list = props_dict['contact']
            metadata.setContacts([])
            for contact in xml_contact_list:
                qgis_contact = QgsAbstractMetadataBase.Contact()
                qgis_contact.name = contact.name
                qgis_contact.role = contact.role
                qgis_contact.organization = contact.organization
                qgis_contact.position = contact.position
                qgis_contact.email = contact.email
                qgis_contact.voice = contact.phone
                qgis_contact.fax = contact.fax
                #address not implemented yet; not available in our metadata?

                metadata.addContact(qgis_contact)

            #Creator not implemented on qgis

            #Date not implemented on qgis

            #Type
            if self.parameterAsBool(parameters,self.COPYTYPE,context):
                metadata.setType(props_dict['identtype'])

            #Keywords
            xml_keywords = props_dict['keywords']
            keyword_dict = {}
            for keyword in xml_keywords:
                keyword_vocabulary = keyword['type']
                keywords_list = keyword['keywords']
                if keyword_vocabulary in keyword_dict:
                    keyword_dict[keyword_vocabulary] += keywords_list
                    keyword_dict[keyword_vocabulary] = list(set(
                        keyword_dict[keyword_vocabulary]))
                else:
                    keyword_dict[keyword_vocabulary] = list(set(keywords_list))
            for vocabulary in keyword_dict.keys():
                metadata.addKeywords(vocabulary,keyword_dict[vocabulary])
            
            #Purpose not implemented in qgis

            #Language
            if props_dict['resourcelanguage']:
                metadata.setLanguage(', '.join(props_dict['resourcelanguage']))
            else:
                metadata.setLanguage(', '.join(props_dict['resourcelanguagecode']))

            ## Verify if Licenses, rights and constraints are taking data
            ##from the correct xml paths
            #Licenses
            metadata.setLicenses(props_dict['accessconstraints'])

            #Rights
            metadata.setRights(props_dict['useconstraints'])

            #Other constraints
            metadata.setConstraints([])
            for xml_constraint in props_dict['otherconstraints']:
                qgs_constraint = QgsLayerMetadata.Constraint()
                qgs_constraint.constraint = xml_constraint
                qgs_constraint.type = 'other'
                metadata.addConstraint(qgs_constraint)

            #Links
            metadata.setLinks([])
            for xml_link in file_metadata.distribution.online:
                qgs_link = QgsAbstractMetadataBase.Link()
                qgs_link.description = xml_link.description
                qgs_link.type = xml_link.protocol
                qgs_link.name = xml_link.name
                qgs_link.url = xml_link.url
                qgs_link.format = xml_link.function
                metadata.addLink(qgs_link)

            #Set new metadata
            layer.setMetadata(metadata)

        feedback.setProgress(int(100))
        return {self.OUTPUT: True}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Importar Metadado ISO-19115'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Utils'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportISOMetadataAlgorithm()
