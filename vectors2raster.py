# -*- coding: utf-8 -*-
"""
/***************************************************************************
 vectors2raster
                                 A QGIS plugin
 Rasterize and Overlay analysis that not affected by NODATA settings

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-27
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Kwanhyun, Kim
        email                : popyj01012@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

import PyQt5
from PyQt5 import QtWidgets


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .vectors2raster_dialog import vectors2rasterDialog
import os.path
#from qgis.core import QgsMapLayerProxyModel, QgsVectorLayer, QgsMapLayer
import glob, os, processing
from qgis.core import *
import sys


class vectors2raster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'vectors2raster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'& Overlay Analysis: vectors2raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('vectors2raster', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/vectors2raster/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Overlay Analysis: vectors2raster'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'& Overlay Analysis: vectors2raster'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = vectors2rasterDialog()

        #로드된 레이어 불러오기
        mc = QgsProject.instance().mapLayers().values()
        map_layers_str = []
        #불러온 레이어중 벡터 레이어만 리스트에 추가
        for lyr in mc:
            print(type(lyr))
            if lyr.type() == QgsMapLayer.VectorLayer:
                map_layers_str.append(str(lyr.name()))
        self.dlg.mComboBox.addItems(map_layers_str)

        #run, cancel 버튼 이벤트 추가
        self.dlg.runButton.clicked.connect(self.setValues)
        self.dlg.closeButton.clicked.connect(self.closeDlg)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()


        #result 쪽 내용은  runButton-> setValues로 다 빠졌는데 비우면 에러가 나서 일단 코드는 남겨놓음
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            layerName = self.dlg.mComboBox.checkedItems()
            squareLength = self.dlg.spbRasterPixelSize.value()


            if self.dlg.radioButton_add.isChecked():
                style = "add"
            elif self.dlg.radioButton_mean.isChecked():
                style = "mean"
            elif self.dlg.radioButton_max.isChecked():
                style = "max"
            elif self.dlg.radioButton_min.isChecked():
                style = "min"

            #self.pyqgisTest(layerName, style, squareLength)

            pass

    #초기 변수 세팅
    def setValues(self):
        print("setValues called")
        #입력받은 벡터 레이어 리스트
        layerName = []
        #래스터 레이어 분석 방식
        style = ""
        #분석할 값을 가져올 필드명
        calcField = ""
        #래스터 픽셀 사이즈
        squareLength = ''
        #저장경로 없으면 불러오기만
        savePath = ""
        #저장경로 입력된 경우엔 경로로 저장
        if self.dlg.outputFileWidget.filePath() is not "":
            savePath = self.dlg.outputFileWidget.filePath()
        elif self.dlg.outputFileWidget.filePath() is "":
            savePath = "TEMPORARY_OUTPUT"
        layerName = self.dlg.mComboBox.checkedItems()
        calcField = self.dlg.lineEdit.text()
        squareLength = self.dlg.spbRasterPixelSize.value()

        if self.dlg.radioButton_add.isChecked():
            style = "add"
        elif self.dlg.radioButton_mean.isChecked():
            style = "mean"
        elif self.dlg.radioButton_max.isChecked():
            style = "max"
        elif self.dlg.radioButton_min.isChecked():
            style = "min"


        if calcField is "":
            blankDialog = QtWidgets.QMessageBox()
            blankDialog.setText('input field name!')
            #blankDialog.exec_()
            #sys.exit(blankDialog.exec_())
            blankDialog.exec_()
            self.dlg.progressBar.setValue(0)
            return
        self.pyqgisTest(layerName, calcField, style, squareLength, savePath)

    #pyqgis로 짠 내용
    def pyqgisTest(self, layerName, calcField, style, squareLength, savePath):
        print("pyqgisTest called")
        #분석 중간 산출물 저장용
        reprojectList = []
        rasterizeList= []
        layerList = []
        param = {}
        typeCalc = ''
        #프로그레스바 값 변경
        self.dlg.progressBar.setValue(0)

        #래스터 분석시 범위 지정용 빈 벡터 레이어 제작
        mergedExtent = QgsVectorLayer("Polygon?crs=EPSG:3857", "Polygons", "memory").extent()

        #체크된 레이어 이름으로 레이어 선택 후, 분석 결과 정확도를 위해 좌표계 통일
        for layer in layerName:
            layer1 = QgsProject.instance().mapLayersByName(layer)
            layerList += layer1
            result = processing.run('native:reprojectlayer', {
                'INPUT': layer1[0],
                'TARGET_CRS': 'EPSG:3857',
                'OUTPUT': 'memory:'+layer1[0].name()+'_reprojected'})['OUTPUT']
            #재투영된 산출물의 범위를 중첩
            mergedExtent.combineExtentWith(result.extent())
            reprojectList.append(result)

        self.dlg.progressBar.setValue(25)

        print("재투영 완료")
        #재투영된 산출물들 래스터화
        typeCheck = [2,4]
        for layer in reprojectList:
            field_index = layer.fields().indexFromName(calcField)
            if field_index == -1:
                blankDialog = QtWidgets.QMessageBox()
                blankDialog.setText('One or more layer has no field ""' + calcField + '""!')
                blankDialog.exec_()
                self.dlg.progressBar.setValue(0)
                return
            elif int(layer.fields().field(calcField).type()) not in typeCheck:
                blankDialog = QtWidgets.QMessageBox()
                blankDialog.setText('field type must be int!')
                blankDialog.exec_()
                self.dlg.progressBar.setValue(0)
                return
            else:
                print("rasterize 실행")
                rasterizeResult = processing.run("gdal:rasterize", {
                'INPUT': layer,  # already vector layer
                'FIELD': calcField,
                'UNITS': 1,  # Georeferenced units
                'WIDTH': squareLength,
                'HEIGHT': squareLength,
                'EXTENT': mergedExtent,
                'NODATA': None,
                'OPTIONS': '',
                'DATA_TYPE': 5,  # Float32
                'INIT': None,
                'INVERT': False,
                'EXTRA': '-tap',
                'OUTPUT': 'TEMPORARY_OUTPUT'})
                rasterizeList.append(rasterizeResult)
            print("필드 확인 완료")
        self.dlg.progressBar.setValue(50)


        #래스터 계산기에 입력할 계산식 case별 정리. gdal raster calculator은 입력 레이어가 6개 까지라 1~6개 케이스를 모두 작성함
        match style:
            case 'add':
                if len(rasterizeList) == 1:
                    typeCalc='A'
                elif len(rasterizeList) == 2:
                    typeCalc='A+B'
                elif len(rasterizeList) == 3:
                    typeCalc='A+B+C'
                elif len(rasterizeList) == 4:
                    typeCalc='A+B+C+D'
                elif len(rasterizeList) == 5:
                    typeCalc='A+B+C+D+E'
                elif len(rasterizeList) == 6:
                    #색깔 왜이러지
                    typeCalc='A+B+C+D+E+F'
            case 'mean':
                if len(rasterizeList) == 1:
                    typeCalc='A'
                elif len(rasterizeList) == 2:
                    typeCalc='(A+B)/2'
                elif len(rasterizeList) == 3:
                    typeCalc='(A+B+C)/3'
                elif len(rasterizeList) == 4:
                    typeCalc='(A+B+C+D)/4'
                elif len(rasterizeList) == 5:
                    typeCalc='(A+B+C+D+E)/5'
                elif len(rasterizeList) == 6:
                    typeCalc='(A+B+C+D+E+F)/6'
            case 'max':
                if len(rasterizeList) == 1:
                    typeCalc='A'
                elif len(rasterizeList) == 2:
                    typeCalc='maximum(A,B)'
                elif len(rasterizeList) == 3:
                    typeCalc='maximum(maximum(A,B),C)'
                elif len(rasterizeList) == 4:
                    typeCalc='maximum(maximum(maximum(A,B),C),D)'
                elif len(rasterizeList) == 5:
                    typeCalc='maximum(maximum(maximum(maximum(A,B),C),D),E)'
                elif len(rasterizeList) == 6:
                    typeCalc='maximum(maximum(maximum(maximum(maximum(A,B),C),D),E),F)'
            case 'min':
                if len(rasterizeList) == 1:
                    typeCalc='A'
                elif len(rasterizeList) == 2:
                    typeCalc='minimum((((A==0)*1000)+A),(((B==0)*1000)+B))-(((minimum((((A==0)*1000)+A),(((B==0)*1000)+B)))==1000)*1000)'
                elif len(rasterizeList) == 3:
                    typeCalc='minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C))-(((minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)))==1000)*1000)'
                elif len(rasterizeList) == 4:
                    typeCalc='minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D))-(((minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D)))==1000)*1000)'
                elif len(rasterizeList) == 5:
                    typeCalc='minimum(minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D)),(((E==0)*1000)+E))-(((minimum(minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D)),(((E==0)*1000)+E)))==1000)*1000)'
                elif len(rasterizeList) == 6:
                    typeCalc='minimum(minimum(minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D)),(((E==0)*1000)+E)),(((F==0)*1000)+F))-(((minimum(minimum(minimum(minimum(minimum((((A==0)*1000)+A),(((B==0)*1000)+B)),(((C==0)*1000)+C)),(((D==0)*1000)+D)),(((E==0)*1000)+E)),(((F==0)*1000)+F)))==1000)*1000)'

        self.dlg.progressBar.setValue(75)

        #입력된 래스터 수에 따라서 래스터 계산기 입력 파라미터 case로 정리
        match len(rasterizeList):
            case 1:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : None,
                'INPUT_C' : None,
                'INPUT_D' : None,
                'INPUT_E' : None,
                'INPUT_F' : None,
                'BAND_A' : 1,
                'BAND_B' : None,
                'BAND_C' : None,
                'BAND_D' : None,
                'BAND_E' : None,
                'BAND_F' : None,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }
            case 2:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : list(rasterizeList[1].values())[0],
                'INPUT_C' : None,
                'INPUT_D' : None,
                'INPUT_E' : None,
                'INPUT_F' : None,
                'BAND_A' : 1,
                'BAND_B' : 1,
                'BAND_C' : None,
                'BAND_D' : None,
                'BAND_E' : None,
                'BAND_F' : None,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }
            case 3:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : list(rasterizeList[1].values())[0],
                'INPUT_C' : list(rasterizeList[2].values())[0],
                'INPUT_D' : None,
                'INPUT_E' : None,
                'INPUT_F' : None,
                'BAND_A' : 1,
                'BAND_B' : 1,
                'BAND_C' : 1,
                'BAND_D' : None,
                'BAND_E' : None,
                'BAND_F' : None,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }
            case 4:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : list(rasterizeList[1].values())[0],
                'INPUT_C' : list(rasterizeList[2].values())[0],
                'INPUT_D' : list(rasterizeList[3].values())[0],
                'INPUT_E' : None,
                'INPUT_F' : None,
                'BAND_A' : 1,
                'BAND_B' : 1,
                'BAND_C' : 1,
                'BAND_D' : 1,
                'BAND_E' : None,
                'BAND_F' : None,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }
            case 5:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : list(rasterizeList[1].values())[0],
                'INPUT_C' : list(rasterizeList[2].values())[0],
                'INPUT_D' : list(rasterizeList[3].values())[0],
                'INPUT_E' : list(rasterizeList[4].values())[0],
                'INPUT_F' : None,
                'BAND_A' : 1,
                'BAND_B' : 1,
                'BAND_C' : 1,
                'BAND_D' : 1,
                'BAND_E' : 1,
                'BAND_F' : None,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }
            case 6:
                param = {
                'INPUT_A' : list(rasterizeList[0].values())[0],
                'INPUT_B' : list(rasterizeList[1].values())[0],
                'INPUT_C' : list(rasterizeList[2].values())[0],
                'INPUT_D' : list(rasterizeList[3].values())[0],
                'INPUT_E' : list(rasterizeList[4].values())[0],
                'INPUT_F' : list(rasterizeList[5].values())[0],
                'BAND_A' : 1,
                'BAND_B' : 1,
                'BAND_C' : 1,
                'BAND_D' : 1,
                'BAND_E' : 1,
                'BAND_F' : 1,
                'EXTENT_OPT' : 0,
                'EXTRA' : '',
                'FORMULA' : typeCalc,
                'NO_DATA' : None,
                'OPTIONS' : '',
                'OUTPUT' : savePath,
                'PROJWIN' : mergedExtent,
                'RTYPE' : 1 }

        #래스터계산기 실행
        processing.runAndLoadResults('gdal:rastercalculator', param)
        print("래스터계산기 실행 완료")
        self.dlg.progressBar.setValue(100)

        #실행 완료 메시지박스 출력
        blankDialog = QtWidgets.QMessageBox()
        blankDialog.setText('Done!')
        blankDialog.exec_()

    #툴 close시 입력값 초기화
    def closeDlg(self):
        self.dlg.mComboBox.clear()
        self.dlg.lineEdit.clear()
        self.dlg.radioButton_add.setChecked(True)
        self.dlg.outputFileWidget.setFilePath(None)
        self.dlg.progressBar.setValue(0)
        self.dlg.spbRasterPixelSize.setValue(50)

        self.dlg.runButton.disconnect()
        self.dlg.closeButton.disconnect()

        self.dlg.close()
