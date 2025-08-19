#-*-coding: UTF-8-*-
#########################################################################
#  Author: Junjun Guo
#  E-mail: jjguo2@bjtu.edu.cn/guojj_ce@163.com
#  Environment: Successfully executed in python 3.13
#########################################################################
import os
import math
import shutil

import h5py
import ctypes
import fnmatch
import ezdxf  #ezdxf is a Python package to create new DXF files and read/modify/write existing DXF files
import openseespy.opensees as ops
from decimal import Decimal, getcontext
user32=ctypes.windll.user32
os.environ["QT_API"] = "pyside6"
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QColorDialog, QMenu, QToolBar, QFileDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QFrame, QStatusBar, QComboBox, QSplitter, QGroupBox,
                               QSpacerItem, QSizePolicy, QMessageBox, QRadioButton, QTableWidget, QHeaderView,
                               QTableWidgetItem, QTabWidget, QApplication, QButtonGroup,QStackedWidget,QFormLayout,
                               QToolTip,QTextEdit)
from PySide6.QtGui import (QIcon,QPalette,QColor,QFont,QAction,QPixmap,QKeySequence,QClipboard)
from PySide6.QtCore import (QDir, Qt, QMimeData, QTimer,Slot)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import collections
from itertools import chain
matplotlib.use('Agg')
from matplotlib.backends.backend_qtagg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import numpy as np
import pygmsh
########################################################################################################################
########################################################################################################################
class Auxiliary_sectMCAnalyses(QtWidgets.QMainWindow):
    """"""
    def __init__(self,lisenceDataList):
        """"""
        super(Auxiliary_sectMCAnalyses, self).__init__()
        self.timer=QTimer()
        self.screenSize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.displayFont = QFont()  # button font setting
        self.displayFont.setFamily("Consolas")
        self.displayFont.setPointSize(12)
        self.redColor = "background-color: #ffaa7f"  # button color setting
        self.blueColor = "background-color: #b8f9ff"
        self.currentWorkPath=None ###---current working directory
        self.sectionDXFPath=None
        self.sectionDXFName=None
        self.mcResultGroupName=None
        self.indexValue=0
        self.fiberRespIndexValue=0
        self.fiberRespIndexValueCircle=0
        self.fiberMesh_figureSize=None
        ###############
        self.statusBarSetting()
        self.ui()
        ##############

    def statusBarSetting(self):
        """---statusbar setting---"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.author = QLabel("Author:Junjun Guo,Penghui Zhang,Chao Chen")
        self.email = QLabel("Email:jjguo2@bjtu.edu.cn/guojj_ce@163.com")
        self.displayLabel = QLabel("")
        # self.license = QLabel("Subscription is active until, " + str(self.licenseDay) + "/"
        #                       + str(self.licenseMonth) + "/" + str(self.licenseYear))
        self.statusBar.addPermanentWidget(self.author, stretch=1)
        self.statusBar.addPermanentWidget(self.email, stretch=2)
        self.statusBar.addPermanentWidget(self.displayLabel, stretch=2)
        # self.statusBar.addPermanentWidget(self.license, stretch=2)

    def ui(self):
        """---GUI layout---"""
        self.setWindowTitle("Section moment curvature analyses")
        self.setGeometry(int(0.02 * self.screenSize[0]), int(0.06 * self.screenSize[1]), \
                         int(0.77 * self.screenSize[0]), int(0.68 * self.screenSize[1]))
        ##################################################################
        self.splitterH = QSplitter(orientation=Qt.Horizontal)
        frameMatplotlib = QFrame(self.splitterH)  ###
        ##############################
        frameDisplay = QFrame()
        frameDisplay.setFixedHeight(40)
        self.stacked_widget = QStackedWidget(self)
        # self.stacked_widget.setVisible(False)
        ####
        stackVBox = QVBoxLayout()
        stackVBox.addWidget(frameDisplay)
        stackVBox.addWidget(self.stacked_widget)
        self.leftFrame_visibleSwith = QFrame()
        self.leftFrame_visibleSwith.setLayout(stackVBox)
        self.leftFrame_visibleSwith.setVisible(False)
        ####
        self.fiberMeshInitFrame = QFrame()
        self.MCAnalysisInitFrame = QFrame()
        self.fiberResInitFrame = QFrame()
        self.stacked_widget.addWidget(self.fiberMeshInitFrame)
        self.stacked_widget.addWidget(self.MCAnalysisInitFrame)
        self.stacked_widget.addWidget(self.fiberResInitFrame)
        ####
        middleVBox = QVBoxLayout()
        middleVBox.addWidget(self.leftFrame_visibleSwith)
        frameMatplotlib.setLayout(middleVBox)
        #############---swith between moment curvature curve and section fiber meshing
        self.fiberMesh_radioButton = QRadioButton("fiber mesh", self)
        self.MCCurve_radioButton = QRadioButton("moment curvature curve", self)
        self.fiberRes_radioButton = QRadioButton("fiber response", self)
        self.fiberMesh_radioButton.clicked.connect(self.fiberMesh_radioButton_slot)
        self.MCCurve_radioButton.clicked.connect(self.MCCurve_radioButton_slot)
        self.fiberRes_radioButton.clicked.connect(self.fiberRes_radioButton_slot)
        #####
        self.fiberMesh_radioButton.setVisible(True)
        self.MCCurve_radioButton.setVisible(True)
        self.fiberRes_radioButton.setVisible(True)
        self.display_buttonGroup = QButtonGroup(self)
        self.display_buttonGroup.addButton(self.fiberMesh_radioButton)
        self.display_buttonGroup.addButton(self.MCCurve_radioButton)
        self.display_buttonGroup.addButton(self.fiberRes_radioButton)
        # self.fiberMesh_radioButton.setChecked(True)
        displayRadioHBox = QHBoxLayout()
        # displayRadioHBox.addItem(hSpacer)
        displayRadioHBox.addWidget(self.fiberMesh_radioButton)
        displayRadioHBox.addWidget(self.MCCurve_radioButton)
        displayRadioHBox.addWidget(self.fiberRes_radioButton)
        # displayRadioHBox.addItem(hSpacer)
        frameDisplay.setLayout(displayRadioHBox)
        ##################################################################
        self.fiberMesh_radioButton_ui()
        self.MCCurve_radioButton_ui()
        self.fiberRes_radioButton_ui()
        ##################################################################
        frameRight = QFrame(self.splitterH)
        frameRight_formLayout = QFormLayout(frameRight)
        ##########################
        self.rightPanel_fiberMesh_radioButton = QRadioButton("fiber mesh", self)
        self.rightPanel_mcAnalysis_radioButton = QRadioButton("moment curvature analysis", self)
        self.rightPanel_fiberMesh_radioButton.clicked.connect(self.rightPanel_fiberMesh_radioButton_slot)
        self.rightPanel_mcAnalysis_radioButton.clicked.connect(self.rightPanel_mcAnalysis_radioButton_slot)
        self.rightPanel_fiberMesh_radioButton.setChecked(False)
        ####
        self.analysisType_buttonGroup = QButtonGroup(self)
        self.analysisType_buttonGroup.addButton(self.rightPanel_fiberMesh_radioButton)
        self.analysisType_buttonGroup.addButton(self.rightPanel_mcAnalysis_radioButton)
        ############
        frameRight_formLayout.addRow(self.rightPanel_fiberMesh_radioButton, self.rightPanel_mcAnalysis_radioButton)
        ######################################################
        self.rightPanel_stacked_widget = QStackedWidget(self)
        self.rightPanel_stacked_widget.setVisible(False)
        ####
        self.rightPanel_fiberMesh_initFrame = QFrame()
        self.rightPanel_mcAnalysis_initFrame = QFrame()
        self.rightPanel_stacked_widget.addWidget(self.rightPanel_fiberMesh_initFrame)
        self.rightPanel_stacked_widget.addWidget(self.rightPanel_mcAnalysis_initFrame)
        # ######################################################
        frameRight_formLayout.addRow(self.rightPanel_stacked_widget)
        #################################################################
        self.rightPanel_fiberMesh_frame_ui()
        self.rightPanel_mcAnalysis_frame_ui()
        ##################################################################
        ##################################################################
        windowWidth = self.width()
        self.splitterH.setSizes([int(0.8 * windowWidth), int(0.2 * windowWidth)])
        mainFrame = QFrame()
        vBox = QVBoxLayout()
        vBox.addWidget(self.splitterH)
        mainFrame.setLayout(vBox)  ####---put vBox on mainFrame
        self.setCentralWidget(mainFrame)  ####---mainFrame fill the screen
        ##################################################

    def rightPanel_mc_newAnalysis_radioButton_slot(self):
        """"""
        curDir = QDir.currentPath()  # get current working directory
        aFile, filt = QFileDialog.getOpenFileName(self, "Open meshed fibers database", curDir, "(*.h5)")  # file dialog
        sectionDbPath = aFile
        if sectionDbPath:
            self.sectionDXFPath = aFile
            self.sectionDXFName = os.path.splitext(os.path.basename(sectionDbPath))[0]
            self.displayLabel.setText("Successfully open database file: " + sectionDbPath)
            ##########################################################
            self.rightPanel_mc_sectType_circle_radioButton.setVisible(True)
            self.rightPanel_mc_sectType_rect_radioButton.setVisible(True)
            ####################
            current_dir = os.path.dirname(self.sectionDXFPath)
            parant_dir=os.path.dirname(current_dir)
            self.mc_newAnalysis_DBInstance = MCAnalysisResultDB(parant_dir, self.sectionDXFName)
            ###########################################
            self.numSegs_frame.setVisible(True)
            self.fiberDivideParasSetting_frame.setVisible(True)
            self.fiberMesh_button.setVisible(False)
            self.outputMesh_button.setVisible(True)
            self._databaseFiberMeshPlot(sectionDbPath)
            self.mc_sectionName_ComboBox.setVisible(False)
            self.rightPanel_mc_sectType_rect_radioButton.setChecked(False)
            self.rightPanel_mc_sectType_circle_radioButton.setChecked(False)
            self.mc_circle_mcAnalysis_button.setVisible(True)
            self.mc_rect_mcAnalysis_button.setVisible(True)
            #########################################################

    def rightPanel_mc_openDb_radioButton_slot(self):
        """"""
        curDir = QDir.currentPath()  # get current working directory
        aFile, filt = QFileDialog.getOpenFileName(self, "Open moment curvature results database", curDir, "(*.h5)")  # file dialog
        sectionDbPath = aFile
        if sectionDbPath:
            self.sectionDXFPath = aFile
            self.sectionDXFName = os.path.splitext(os.path.basename(sectionDbPath))[0]
            self.displayLabel.setText("Successfully open database file: " + sectionDbPath)
            ##########################################################
            self.rightPanel_mc_sectType_circle_radioButton.setVisible(True)
            self.rightPanel_mc_sectType_rect_radioButton.setVisible(True)
            ####################
            current_dir = os.path.dirname(self.sectionDXFPath)
            parant_dir = os.path.dirname(current_dir)
            self.mc_newAnalysis_DBInstance = MCAnalysisResultDB(parant_dir, self.sectionDXFName)
            ###########################################
            self.numSegs_frame.setVisible(True)
            self.fiberDivideParasSetting_frame.setVisible(True)
            self.fiberMesh_button.setVisible(False)
            self.outputMesh_button.setVisible(True)
            self._databaseFiberMeshPlot(sectionDbPath)
            #########################################################
            self.mc_sectionName_ComboBox.clear()
            #########################################################
            sectionNames=self.mc_newAnalysis_DBInstance.partialMatchGroups(self.sectionDXFPath,"mc_analysis_")
            if len(sectionNames)>0:
                self.mc_sectionName_ComboBox.setVisible(True)
            for each in sectionNames:
                sectName=each.split("_")[-1]
                self.mc_sectionName_ComboBox.addItem(sectName)
            ################################################

    def rightPanel_mc_sectType_circle_radioButton_slot(self):
        """"""
        self.rightPanel_mc_stacked_widget.setVisible(True)
        self.rightPanel_mc_stacked_widget.setCurrentIndex(0)
        self.rightPanel_mc_rectSect_initFrame.setVisible(False)
        self.rightPanel_mc_circleSect_initFrame.setVisible(True)

    def rightPanel_mc_sectType_rect_radioButton_slot(self):
        """"""
        self.rightPanel_mc_stacked_widget.setVisible(True)
        self.rightPanel_mc_stacked_widget.setCurrentIndex(1)
        self.rightPanel_mc_circleSect_initFrame.setVisible(False)
        self.rightPanel_mc_rectSect_initFrame.setVisible(True)

    @Slot(str)
    def circle_coreMaterial_ComboBox_slot(self,selectedText):
        """"""
        if selectedText == "User":
            self.circle_userCoreMaterial_lineEdit.setVisible(True)
        else:
            self.circle_userCoreMaterial_lineEdit.setVisible(False)

    @Slot(str)
    def circle_rebarMaterial_ComboBox_slot(self,selectedText):
        if selectedText == "User":
            self.circle_userRebarMaterial_textEdit.setVisible(True)
        else:
            self.circle_userRebarMaterial_textEdit.setVisible(False)

    @Slot(str)
    def circle_loadingY_radioButton_slot(self,selectedText):
        """"""
        self.circle_momentLocal_label.setText("Moment at local Z(kN.m)")

    @Slot(str)
    def circle_loadingZ_radioButton_slot(self,selectedText):
        """"""
        self.circle_momentLocal_label.setText("Moment at local Y(kN.m)")

    @Slot(str)
    def rect_loadingY_radioButton_slot(self, selectedText):
        """"""
        self.rect_momentLocal_label.setText("Moment at local Z(kN.m)")

    @Slot(str)
    def rect_loadingZ_radioButton_slot(self, selectedText):
        """"""
        self.rect_momentLocal_label.setText("Moment at local Y(kN.m)")

    def mc_circle_mcAnalysis_button_slot(self):
        """"""
        self.mc_circle_mcAnalysis_button.setText("In progress...")
        self.mc_circle_mcAnalysis_button.setStyleSheet("background-color: #FFD39B;")
        QTimer.singleShot(1, self.reset_mc_circle_mcAnalysis_button_slot)
        #########################################################

    def reset_mc_circle_mcAnalysis_button_slot(self):
        """"""
        self.leftFrame_visibleSwith.setVisible(True)
        #######################################################
        self.mc_circle_caseName=self.mc_circle_caseName_lineEdit.text()
        ########################################################
        returnValue=self.mc_newAnalysis_DBInstance.dataSetsInGroup(self.sectionDXFPath,
                                    f"mc_analysis_{self.mc_circle_caseName}")
        if returnValue is not None:
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                    f"mc_analysis_{self.mc_circle_caseName}")
        ########################################################
        textValue =self.mc_circle_caseName
        savedName = f"mc_analysis_{self.mc_circle_caseName}/caseName"
        savedValueList = [[textValue]]
        headNameList = ['name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ########################################################
        textValue ="Circle"
        savedName = f"mc_analysis_{self.mc_circle_caseName}/sectionType"
        savedValueList = [[textValue]]
        headNameList = ['sectionType']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #########################################################
        textValue = self.circle_coreMaterial_ComboBox.currentText()
        if textValue == "User":
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
            f"mc_analysis_{self.mc_circle_caseName}/coreMaterial")
            textValue=self.circle_userCoreMaterial_lineEdit.text()
            savedName = f"mc_analysis_{self.mc_circle_caseName}/coreMaterial_user"
            try:
                textList=eval(textValue)
                textListStr=[str(each) for each in textList]
                for each in textListStr:
                    if each in ["None","True","False"]:
                        self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                        self.displayLabel.setStyleSheet("color: red;")
                        raise ValueError()
                    else:
                        self.displayLabel.setStyleSheet("color: black;")
                if not (all(isinstance(x, (int, float)) for x in textList) and len(textList)==4):
                    self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                    self.displayLabel.setStyleSheet("color: red;")
                    raise ValueError()
                else:
                    self.displayLabel.setStyleSheet("color: black;")
            except:
                self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError()
        else:
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
            f"mc_analysis_{self.mc_circle_caseName}/coreMaterial_user")
            savedName = f"mc_analysis_{self.mc_circle_caseName}/coreMaterial"
        savedValueList=[[textValue]]
        headNameList=['materialName']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.circle_rebarMaterial_ComboBox.currentText()
        if textValue == "User":
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
            f"mc_analysis_{self.mc_circle_caseName}/rebarMaterial")
            textValue = self.circle_userRebarMaterial_textEdit.document()
            textValueLines=textValue.toPlainText().splitlines()
            for ii in range(len(textValueLines)):
                savedName = f"mc_analysis_{self.mc_circle_caseName}/rebarMaterial_user_{ii+1}"
                savedValueList = [[textValueLines[ii]]]
                headNameList = ['materialName']
                operationIndexStr = 'replace'
                self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        else:
            matchList=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                f"mc_analysis_{self.mc_circle_caseName}",'rebarMaterial_user')
            for each in matchList:
                self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                f"mc_analysis_{self.mc_circle_caseName}/{each}")
            savedName = f"mc_analysis_{self.mc_circle_caseName}/rebarMaterial"
            savedValueList = [[textValue]]
            headNameList = ['materialName']
            operationIndexStr = 'replace'
            self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.circle_stirrupType_ComboBox.currentText()
        savedName = f"mc_analysis_{self.mc_circle_caseName}/stirrupType"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.mc_circle_stirrupDiameter_lineEdit.text()
        labelName = "Stirrup diameter"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue=self._intFloatPositiveInputValidate(textValue, labelName,nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/stirrupDiameter"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.mc_circle_stirrupSpace_lineEdit.text()
        labelName = "Stirrup space"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/stirrupSpace"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.mc_circle_stirrupYieldStength_lineEdit.text()
        labelName = "Stirrup yield strength"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/stirrupYieldStrength"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.mc_circle_axialLoad_lineEdit.text()
        labelName = "Axial load"
        nameErrorText = "'not a valid input value,input a number!"
        textValue = self._intFloatInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/axialLoad"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        if self.circle_loadingY_radioButton.isChecked():
            textValue="localY"
        else:
            textValue="localZ"
        savedName = f"mc_analysis_{self.mc_circle_caseName}/loadingDirection"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue =self.circle_momentLocal_lineEdit.text()
        labelName = "Moment at perperdicular direction"
        nameErrorText = "'not a valid input value,input a number!"
        textValue = self._intFloatInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/momentAtPperpendicularDirection"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.circle_targetDuctilityFactor_lineEdit.text()
        labelName = "Mu"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/Mu"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.circle_markerSize_lineEdit.text()
        labelName = "markerSize"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_circle_caseName}/markerSize"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #####################################################################################################
        ###---Get data from the database and conduct MC analysis
        groupName=f"mc_analysis_{self.mc_circle_caseName}"
        caseName = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/caseName")[0][0]

        coreMaterial=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                                        f"{groupName}","coreMaterial")[0]
        rebarMaterial=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                                    f"{groupName}","rebarMaterial")
        coreMaterialFinal=None
        if coreMaterial=="coreMaterial":
            coreMaterialFinal=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                f"{groupName}/coreMaterial")[0][0]
        else:
            coreMaterialFinal=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                f"{groupName}/{coreMaterial}")[0][0]
        #########
        rebarMaterialFinalList=[]
        if rebarMaterial[0]=="rebarMaterial":
            tempValue=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/rebarMaterial")[0][0]
            rebarMaterialFinalList.append(tempValue)
        else:
            for eachName in rebarMaterial:
                temValue=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/{eachName}")[0][0]
                rebarMaterialFinalList.append(temValue)
        ##################################################################################################
        stirrupType=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/stirrupType")[0][0]
        #########
        stirrupDiameter=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/stirrupDiameter")[0][0]
        stirrupSpace=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/stirrupSpace")[0][0]
        stirrupYieldStrength=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                      f"{groupName}/stirrupYieldStrength")[0][0]
        axialLoad=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/axialLoad")[0][0]
        loadingDirction=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/loadingDirection")[0][0]
        momentAtPerperdicularDirection=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                            f"{groupName}/momentAtPperpendicularDirection")[0][0]
        Mu=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/Mu")[0][0]
        ########################
        stirrupDiameter=round(stirrupDiameter,6)
        stirrupSpace=round(stirrupSpace,6)
        stirrupYieldStrength=round(stirrupYieldStrength,6)
        axialLoad=round(axialLoad,6)
        momentAtPerperdicularDirection=round(momentAtPerperdicularDirection,6)
        Mu=round(Mu,6)
        ############################################---Material properties calculation
        barsNameList=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,"fiberMesh","bars")
        barsFiberList=[]
        for eachbar in barsNameList:
            tempValue=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/{eachbar}")
            if tempValue is None:
                barsFiberList.append([])
            else:
                barsFiberList.append(tempValue)
        totalBarList=[]
        [[totalBarList.append(each[3]) for each in eachBarValue] for eachBarValue in barsFiberList]
        ##########
        coreFiberList=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/coreFiberInfo")
        if coreFiberList is None:
            coreFiberList=[]
        totalCoreFiberList=[]
        [totalCoreFiberList.append(each[3]) for each in coreFiberList]
        ##########
        innerFiberList=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                f"fiberMesh/innerCoverFiberInfo")
        if innerFiberList is None:
            innerFiberList=[]
        totalInnerFiberList=[]
        [totalInnerFiberList.append(each[3]) for each in innerFiberList]
        ######
        outFiberList=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                              f"fiberMesh/outCoverFiberInfo")
        if outFiberList is None:
            outFiberList=[]
        totalOutFiberList=[]
        [totalOutFiberList.append(each[3]) for each in outFiberList]
        ####################
        totalBarArea=np.sum(totalBarList)
        totalInnerArea=np.sum(totalInnerFiberList)
        totalCoreArea=np.sum(totalCoreFiberList)
        totalOutArea=np.sum(totalOutFiberList)
        ###################
        roucc=totalBarArea/float(totalInnerArea+totalCoreArea+totalOutArea)
        ###################
        conCreateGradeList=["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
             "C65", "C70", "C75", "C80"]
        rebarGradeList=["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400","RRB400", "HRB500","HRBF500"]
        ####################
        outPoints=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,"fiberMesh/outPoints")
        corePoints=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,"fiberMesh/corePoints")
        yValueList=[]
        zValueList=[]
        [[yValueList.append(each[0]),zValueList.append(each[1])] for each in outPoints]
        [[yValueList.append(each[0]),zValueList.append(each[1])] for each in corePoints]
        minY,maxY=min(yValueList),max(yValueList)
        minZ,maxZ=min(zValueList),max(zValueList)
        yD,zD=(maxY-minY),(maxZ-minZ)
        outD=round(0.5*(yD+zD),6)
        #############################################################
        coverThick=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,"fiberMesh/outCoverThickness")[0][0]
        if coverThick is None:
            coverThick=0.0
        #############################################################
        material = Material()
        if coreMaterialFinal in conCreateGradeList:
            coverParameter = material.coverParameter(coreMaterialFinal)
            coreParameter = material.coreParameterCircular(coreMaterialFinal, stirrupType, outD, coverThick,
                            roucc, stirrupSpace, stirrupDiameter, stirrupYieldStrength)
        else:
            coverParameter = eval(self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                        f"{groupName}/coreMaterial_user")[0][0])
            #####################################################
            fco =coverParameter[0]
            Ec = math.sqrt(-fco / 1000) * 5e6
            confinedConcrete = Mander()
            fc, ec, ecu = confinedConcrete.circular(stirrupType,outD, coverThick, roucc,stirrupSpace,stirrupDiameter,
                                                    stirrupYieldStrength, -fco / 1000)
            coreParameter = [float(1000 * fc), float(ec), float(ecu), Ec]
        ###############################################################################################
        savedName =groupName+"/coverConcreteMatParas"
        savedValueList = [coverParameter]
        headNameList=["concreteCompressiveStrengthAt28Days-fc(kPa)",
                        "concreteStrainAtMaximumStrength-ec",
                        "concreteStrainAtCrushingStrength-ecu",
                        "initialStiffness-Ec(kPa)"]
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ##############################################
        savedName = groupName + "/coreConcreteMatParas"
        savedValueList = [coreParameter]
        headNameList = ["concreteCompressiveStrengthAt28Days-fc(kPa)",
                        "concreteStrainAtMaximumStrength-ec",
                        "concreteStrainAtCrushingStrength-ecu",
                        "initialStiffness-Ec(kPa)"]
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###############################################################################################
        barsFiber=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,'fiberMesh','bars')
        barMatDict={}
        for i0 in range(len(rebarMaterialFinalList)):
            if rebarMaterialFinalList[i0] in rebarGradeList:
                barParameter = material.barParameter(rebarMaterialFinalList[i0])
                for i1 in range(len(barsFiber)):
                    barMatDict[f'bars_{i1 + 1}']= barParameter
                    barMatDict[f'bars_{i1 + 1}_number']= 11
                ###########################################################################################
                savedName = groupName + "/barMatParas"
                savedValueList = [barParameter]
                headNameList = ["fy --Yield stress in tension(kPa)",
                                "fu --Ultimate stress in tension(kPa)",
                                "Es--Initial elastic tangent(kPa)",
                                "Esh--Tangent at initial strain hardening(kPa)",
                                "esh--Strain corresponding to initial strain hardening",
                                "eult--Strain at peak stress"]
                operationIndexStr = 'replace'
                self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
                ###########################################################################################
            else:
                barsplitTag = rebarMaterialFinalList[i0].split(",")[1]
                barMatDict[f'bars_{barsplitTag}'] = rebarMaterialFinalList[i0]
                barMatDict[f'bars_{barsplitTag}_number'] = int(barsplitTag)
        ######################################################################################
        if type(barMatDict['bars_1']) is list:
            barMatDict['bars_type']="barGradeType"
        else:
            barMatDict['bars_type']="userInput"
        ##################################################################################################
        if barMatDict['bars_type']=="userInput":
            if len(barsFiber)*2!=(len(barMatDict)-1):
                self.displayLabel.setText(f"The number of user defined rebar materials should be equal to the rebar"
                                          f"material used in dxf file!")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError()
            else:
                self.displayLabel.setStyleSheet("color: black;")
        ###################################################################################################
        ###############################################
        # Estimate the yield curvature of circular section
        D = outD  # length of the outer section in x direction
        kx = 2.213 * 400000/ float(2e8) / float(D)
        ky = kx
        estimatedYieldCurvatureList = [[kx, ky]]
        estimatedYieldCurvatureSaveName = f"{groupName}/estimatedYieldCurvature"
        headNameList = ['estimatedYieldCurvature-kx', 'estimatedYieldCurvature-ky']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(estimatedYieldCurvatureSaveName, estimatedYieldCurvatureList, headNameList,
                              operationIndexStr)
        ###############################################
        loadingDirection =self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/loadingDirection")[0][0]
        if loadingDirection == 'localY':
            loadDir="X"
        elif loadingDirection == 'localZ':
            loadDir="Y"
        ##################################################
        mcInstance = MC(groupName, self.mc_newAnalysis_DBInstance, loadDir,barMatDict,self.sectionDXFPath)
        #######################
        axialLoad =self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/axialLoad")[0][0]
        moment =self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                         f"{groupName}/momentAtPperpendicularDirection")[0][0]
        numIncr = 50
        mcInstance.MCAnalysis(axialLoad=axialLoad, moment=moment, numIncr=numIncr)
        ########################################
        mcInstance.MCCurve(self.mcCurve_figure, self.mcCurve_ax, self.mcCurve_figCanvas,
                           self.sectionDXFPath,groupName,self)
        self.MCCurve_radioButton.setVisible(True)
        self.fiberRes_radioButton.setVisible(True)
        #######################################################---fibers stress strain display
        coreFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/coreFiberInfo")
        innerCoverFiberList=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,"fiberMesh/innerCoverFiberInfo")
        if innerCoverFiberList is None:
            innerCoverFiberList=[]
        outCoverFiberList=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/outCoverFiberInfo")
        if outCoverFiberList is None:
            outCoverFiberList=[]
        barsNameList=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,"fiberMesh","bars")
        if barsNameList is None:
            barsNameList=[]
        barsFiberList=[]
        for each in barsNameList:
            temp=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/{each}")
            barsFiberList.append(temp)
        #################################
        self.xPlot=[]
        [self.xPlot.append(each[1]) for each in coreFiberList]
        [self.xPlot.append(each[1]) for each in innerCoverFiberList]
        [self.xPlot.append(each[1]) for each in outCoverFiberList]
        [[self.xPlot.append(each[1]) for each in eachType] for eachType in barsFiberList]
        ################
        self.yPlot = []
        [self.yPlot.append(each[2]) for each in coreFiberList]
        [self.yPlot.append(each[2]) for each in innerCoverFiberList]
        [self.yPlot.append(each[2]) for each in outCoverFiberList]
        [[self.yPlot.append(each[2]) for each in eachType] for eachType in barsFiberList]
        ##############################
        barColorList=["k","brown","lightblue","gold"]
        colorsList = []
        for each in coreFiberList:
            colorsList.append("b")
        for each in innerCoverFiberList:
            colorsList.append("g")
        for each in outCoverFiberList:
            colorsList.append("g")
        for i1 in range(len(barsFiberList)):
            color=barColorList[i1%4]
            for each in barsFiberList[i1]:
                colorsList.append(color)
        #######################################
        self.indices = np.arange(len(self.xPlot))
        self.colors = np.array(colorsList)
        self.initial_colors = self.colors.copy()
        markerSize = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/markerSize")[0][0]
        self.sizes = np.full(len(self.xPlot), markerSize)
        ##########################################
        interFigure = self.fiberInter_figure
        interAx = self.fiberInter_ax
        interCanvas = self.fiberInter_figCanvas
        ############
        sectionName=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/caseName")[0][0]
        interFigure.suptitle(sectionName + " discreted fiber points")
        self.stacked_widget.setCurrentIndex(2)
        interAx.clear()
        ############################################################
        sectionWidthHeightRatio = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                        f"fiberMesh/sectionWidthHeightRatio")[0][0]
        if self.fiberRespIndexValueCircle == 0:
            self.fiberMesh_figureSize = interFigure.get_size_inches()
            self.fiberRespIndexValueCircle += 1
        sizeValue = self.fiberMesh_figureSize
        originalSizeRatio = sizeValue[0] / float(sizeValue[1])

        if sectionWidthHeightRatio > originalSizeRatio:
            newWidth = sizeValue[0]
            newHeight = sizeValue[0] / float(sectionWidthHeightRatio)
        else:
            newHeight = sizeValue[1]
            newWidth = sizeValue[1] * sectionWidthHeightRatio
        if self.fiberRespIndexValueCircle == 0:
            interFigure.set_figwidth(newWidth)
            interFigure.set_figheight(newHeight)
        # ######################
        interAx.set_xlabel("Local y direction dimension(m)---y")
        interAx.set_ylabel("Local z direction dimension(m)---z")
        #############################
        ######################
        self.scatter = interAx.scatter(self.xPlot, self.yPlot, c=self.colors, picker=True, s=self.sizes)
        figureSize = min(interFigure.get_size_inches())
        interFigure.set_figwidth(figureSize)
        interFigure.set_figheight(figureSize)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        interCanvas.draw()
        ####################################################################################################
        self.fiberIndexDict={}
        self.fiberIndexDict["coreFiber"]=[each[0] for each in coreFiberList]
        self.fiberIndexDict["innerCoverFiber"]=[each[0] for each in innerCoverFiberList]
        self.fiberIndexDict["outCoverFiber"]=[each[0] for each in outCoverFiberList]
        for i1 in range(len(barsFiberList)):
            temp=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/bars_{i1+1}")
            self.fiberIndexDict[f"bars_{i1+1}"]=[each[0] for each in temp]
        ###############################################
        #####################################################################################################
        self.last_clicked = None
        interCanvas.mpl_connect('pick_event', lambda event: self.on_pick(event,self.mc_newAnalysis_DBInstance,
                                                                         self.sectionDXFPath,groupName))
        #################################################################
        self.cyclicMaterialResponse(matType="coreMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath,groupName=groupName)
        self.cyclicMaterialResponse(matType="coverMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=groupName)
        for each in barsNameList:
            self.cyclicMaterialResponse(matType=each, dbInstance=self.mc_newAnalysis_DBInstance,
                                        dbPath=self.sectionDXFPath, groupName=groupName)
        #############################################################
        self.mc_circle_mcAnalysis_button.setText("Start analysis!")
        self.mc_circle_mcAnalysis_button.setStyleSheet("background-color: #7FFFD4;")
        self.mc_circle_mcAnalysis_button.setEnabled(True)
        ########################################################################
        self.mc_circle_outPutResults_button.setVisible(True)
        ########################################################################

    def mc_rect_mcAnalysis_button_slot(self):
        """"""
        self.mc_rect_mcAnalysis_button.setText("In progress...")
        self.mc_rect_mcAnalysis_button.setStyleSheet("background-color: #FFD39B;")
        QTimer.singleShot(1, self.reset_mc_rect_mcAnalysis_button_slot)
        #########################################################

    def reset_mc_rect_mcAnalysis_button_slot(self):
        """"""
        self.leftFrame_visibleSwith.setVisible(True)
        #######################################################
        self.mc_rect_caseName = self.mc_rect_caseName_lineEdit.text()
        ########################################################
        returnValue = self.mc_newAnalysis_DBInstance.dataSetsInGroup(self.sectionDXFPath,
                                                f"mc_analysis_{self.mc_rect_caseName}")
        if returnValue is not None:
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                                                      f"mc_analysis_{self.mc_rect_caseName}")
        ########################################################
        textValue = self.mc_rect_caseName
        savedName = f"mc_analysis_{self.mc_rect_caseName}/caseName"
        savedValueList = [[textValue]]
        headNameList = ['name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ########################################################
        textValue = "Rect"
        savedName = f"mc_analysis_{self.mc_rect_caseName}/sectionType"
        savedValueList = [[textValue]]
        headNameList = ['sectionType']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #########################################################
        textValue = self.rect_coreMaterial_ComboBox.currentText()
        if textValue == "User":
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                                                      f"mc_analysis_{self.mc_rect_caseName}/coreMaterial")
            textValue = self.rect_userCoreMaterial_lineEdit.text()
            savedName = f"mc_analysis_{self.mc_rect_caseName}/coreMaterial_user"
            try:
                textList = eval(textValue)
                textListStr = [str(each) for each in textList]
                for each in textListStr:
                    if each in ["None", "True", "False"]:
                        self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                        self.displayLabel.setStyleSheet("color: red;")
                        raise ValueError()
                    else:
                        self.displayLabel.setStyleSheet("color: black;")
                if not (all(isinstance(x, (int, float)) for x in textList) and len(textList) == 4):
                    self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                    self.displayLabel.setStyleSheet("color: red;")
                    raise ValueError()
                else:
                    self.displayLabel.setStyleSheet("color: black;")
            except:
                self.displayLabel.setText(f"Concrete:User parameters should be 4 real numbers in a list!")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError()
        else:
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                                                      f"mc_analysis_{self.mc_rect_caseName}/coreMaterial_user")
            savedName = f"mc_analysis_{self.mc_rect_caseName}/coreMaterial"
        savedValueList = [[textValue]]
        headNameList = ['materialName']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.rect_rebarMaterial_ComboBox.currentText()
        if textValue == "User":
            self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                                    f"mc_analysis_{self.mc_rect_caseName}/rebarMaterial")
            textValue = self.rect_userRebarMaterial_textEdit.document()
            textValueLines = textValue.toPlainText().splitlines()
            for ii in range(len(textValueLines)):
                savedName = f"mc_analysis_{self.mc_rect_caseName}/rebarMaterial_user_{ii + 1}"
                savedValueList = [[textValueLines[ii]]]
                headNameList = ['materialName']
                operationIndexStr = 'replace'
                self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        else:
            matchList = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                    f"mc_analysis_{self.mc_rect_caseName}",'rebarMaterial_user')
            for each in matchList:
                self.mc_newAnalysis_DBInstance.deleteData(self.sectionDXFPath,
                                                          f"mc_analysis_{self.mc_rect_caseName}/{each}")
            savedName = f"mc_analysis_{self.mc_rect_caseName}/rebarMaterial"
            savedValueList = [[textValue]]
            headNameList = ['materialName']
            operationIndexStr = 'replace'
            self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.mc_rect_rebarSpace_lineEdit.text()
        labelName = "Rebar space"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/rebarSpace"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ##############################################################
        textValue = self.mc_rect_stirrupRatioY_lineEdit.text()
        labelName = "stirrup ratio in Y"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/stirrupRatioY"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ##############################################################
        textValue = self.mc_rect_stirrupRatioZ_lineEdit.text()
        labelName = "stirrup ratio in Z"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/stirrupRatioZ"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ##############################################################
        textValue = self.mc_rect_stirrupSpace_lineEdit.text()
        labelName = "Stirrup space"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/stirrupSpace"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        ###########################################################
        textValue = self.mc_rect_stirrupDiameter_lineEdit.text()
        labelName = "Stirrup diameter"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/stirrupDiameter"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.mc_rect_stirrupYieldStrength_lineEdit.text()
        labelName = "Stirrup yield strength"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/stirrupYieldStrength"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.mc_rect_axialLoad_lineEdit.text()
        labelName = "Axial load"
        nameErrorText = "'not a valid input value,input a number!"
        textValue = self._intFloatInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/axialLoad"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        if self.rect_loadingY_radioButton.isChecked():
            textValue = "localY"
        else:
            textValue = "localZ"
        savedName = f"mc_analysis_{self.mc_rect_caseName}/loadingDirection"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.rect_momentLocal_lineEdit.text()
        labelName = "Moment at perperdicular direction"
        nameErrorText = "'not a valid input value,input a number!"
        textValue = self._intFloatInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/momentAtPperpendicularDirection"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        # #############################################################
        textValue = self.rect_targetDuctilityFactor_lineEdit.text()
        labelName = "Mu"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/Mu"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #############################################################
        textValue = self.rect_markerSize_lineEdit.text()
        labelName = "markerSize"
        nameErrorText = "'not a valid input value,input a positive number!"
        textValue = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ##################
        savedName = f"mc_analysis_{self.mc_rect_caseName}/markerSize"
        savedValueList = [[textValue]]
        headNameList = ['Name']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #####################################################################################################
        # #####################################################################################################
        outCoverNodes=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/outPoints")
        xValues=[each[0] for each in outCoverNodes]
        yValues=[each[1] for each in outCoverNodes]
        lx=max(xValues)-min(xValues)
        ly=max(yValues)-min(yValues)
        ############################
        groupName = f"mc_analysis_{self.mc_rect_caseName}"
        sl=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/rebarSpace")[0][0]
        #######################################################
        barAreaList=[]
        rebarNameList=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,"fiberMesh","bars_")
        if rebarNameList is not None:
            diameterList=[]
            for each in rebarNameList:
                barFiber=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/{each}")
                for eachValue in barFiber:
                    diameterList.append((eachValue[3]*4/3.14159267)**0.5)
                    barAreaList.append(eachValue[3])
            dsl=np.mean(diameterList)
        else:
            dsl=0
        ##########################################################
        roux=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"{groupName}/stirrupRatioY")[0][0]
        rouy = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/stirrupRatioZ")[0][0]
        ##########################################################
        st=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/stirrupSpace")[0][0]
        dst=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/stirrupDiameter")[0][0]
        fyh=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/stirrupYieldStrength")[0][0]
        ############################
        if len(barAreaList)>0:
            corBarFiber=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,f"fiberMesh/coreFiberInfo")
            coreAreaList=[each[3] for each in corBarFiber]
            roucc=np.sum(barAreaList)/float(np.sum(coreAreaList))
        else:
            roucc=0
        #########################################################

        # ############################################---Material properties calculation
        barsFiberList = []
        for eachbar in rebarNameList:
            tempValue = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/{eachbar}")
            if tempValue is None:
                barsFiberList.append([])
            else:
                barsFiberList.append(tempValue)
        # ##########
        coreFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/coreFiberInfo")
        if coreFiberList is None:
            coreFiberList = []
        # ##########
        innerFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                  f"fiberMesh/innerCoverFiberInfo")
        if innerFiberList is None:
            innerFiberList = []
        # ######
        outFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                f"fiberMesh/outCoverFiberInfo")
        if outFiberList is None:
            outFiberList = []
        # ###################
        conCreateGradeList = ["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
                              "C65", "C70", "C75", "C80"]
        rebarGradeList = ["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400", "RRB400", "HRB500", "HRBF500"]
        # ####################
        # #############################################################
        coreMaterial = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                                                           f"{groupName}", "coreMaterial")[0]
        rebarMaterial = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                                                            f"{groupName}", "rebarMaterial")
        coreMaterialFinal = None
        if coreMaterial == "coreMaterial":
            coreMaterialFinal = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                         f"{groupName}/coreMaterial")[0][0]
        else:
            coreMaterialFinal = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                              f"{groupName}/{coreMaterial}")[0][0]
        #########
        rebarMaterialFinalList = []
        if rebarMaterial[0] == "rebarMaterial":
            tempValue = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                 f"{groupName}/rebarMaterial")[0][0]
            rebarMaterialFinalList.append(tempValue)
        else:
            for eachName in rebarMaterial:
                temValue = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                    f"{groupName}/{eachName}")[0][0]
                rebarMaterialFinalList.append(temValue)
        ##################################################################################################
        innerCoverThick=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                 f"fiberMesh/innerCoverThickness")[0][0]
        outCoverThick = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                   f"fiberMesh/outCoverThickness")[0][0]
        coverThick=0.5*(innerCoverThick+outCoverThick)
        ##################################################################
        material = Material()
        if coreMaterialFinal in conCreateGradeList:
            coverParameter = material.coverParameter(coreMaterialFinal)
            coreParameter = material.coreParameterRectangular(coreMaterialFinal, lx, ly, coverThick, roucc,
                                                              sl, dsl, roux, rouy, st,dst, fyh)
        else:
            coverParameter = eval(self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                           f"{groupName}/coreMaterial_user")[0][0])
            fco = coverParameter[0]
            Ec = math.sqrt(-fco / 1000) * 5e6
            confinedConcrete = Mander()
            fc, ec, ecu = confinedConcrete.rectangular(lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh,
                                                       -fco / 1000)
            coreParameter = [float(1000 * fc), float(ec), float(ecu), Ec]
        # ###############################################################################################
        savedName = groupName + "/coverConcreteMatParas"
        savedValueList = [coverParameter]
        headNameList = ["concreteCompressiveStrengthAt28Days-fc(kPa)",
                        "concreteStrainAtMaximumStrength-ec",
                        "concreteStrainAtCrushingStrength-ecu",
                        "initialStiffness-Ec(kPa)"]
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        # ##############################################
        savedName = groupName + "/coreConcreteMatParas"
        savedValueList = [coreParameter]
        headNameList = ["concreteCompressiveStrengthAt28Days-fc(kPa)",
                        "concreteStrainAtMaximumStrength-ec",
                        "concreteStrainAtCrushingStrength-ecu",
                        "initialStiffness-Ec(kPa)"]
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        # ###############################################################################################
        barsFiber = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath, 'fiberMesh', 'bars')
        barMatDict = {}
        for i0 in range(len(rebarMaterialFinalList)):
            if rebarMaterialFinalList[i0] in rebarGradeList:
                barParameter = material.barParameter(rebarMaterialFinalList[i0])
                for i1 in range(len(barsFiber)):
                    barMatDict[f'bars_{i1 + 1}'] = barParameter
                    barMatDict[f'bars_{i1 + 1}_number'] = 11
        #         ###########################################################################################
                savedName = groupName + "/barMatParas"
                savedValueList = [barParameter]
                headNameList = ["fy --Yield stress in tension(kPa)",
                                "fu --Ultimate stress in tension(kPa)",
                                "Es--Initial elastic tangent(kPa)",
                                "Esh--Tangent at initial strain hardening(kPa)",
                                "esh--Strain corresponding to initial strain hardening",
                                "eult--Strain at peak stress"]
                operationIndexStr = 'replace'
                self.mc_newAnalysis_DBInstance.saveResult(savedName, savedValueList, headNameList, operationIndexStr)
        #         ###########################################################################################

            else:
                barsplitTag = rebarMaterialFinalList[i0].split(",")[1]

                barMatDict[f'bars_{barsplitTag}'] = rebarMaterialFinalList[i0]
                barMatDict[f'bars_{barsplitTag}_number'] = int(barsplitTag)
        # ######################################################################################
        if type(barMatDict['bars_1']) is list:
            barMatDict['bars_type'] = "barGradeType"
        else:
            barMatDict['bars_type'] = "userInput"
        # ##################################################################################################
        if barMatDict['bars_type'] == "userInput":
            if len(barsFiber) * 2 != (len(barMatDict) - 1):
                self.displayLabel.setText(f"The number of user defined rebar materials should be equal to the rebar"
                                          f"material used in dxf file!")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError()
            else:
                self.displayLabel.setStyleSheet("color: black;")
        # ###################################################################################################
        kx = 1.957 * 400000/ 200000000.0 / lx
        ky = 1.957 * 400000/ 200000000.0 / ly
        estimatedYieldCurvatureList = [[kx, ky]]
        estimatedYieldCurvatureSaveName = f"{groupName}/estimatedYieldCurvature"
        headNameList = ['estimatedYieldCurvature-kx', 'estimatedYieldCurvature-ky']
        operationIndexStr = 'replace'
        self.mc_newAnalysis_DBInstance.saveResult(estimatedYieldCurvatureSaveName, estimatedYieldCurvatureList,
                                                  headNameList,operationIndexStr)
        # ###############################################
        loadingDirection=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                    f"{groupName}/loadingDirection")[0][0]
        if loadingDirection == 'localY':
            loadDir = "X"
        elif loadingDirection == 'localZ':
            loadDir = "Y"
        # ##################################################
        mcInstance = MC(groupName, self.mc_newAnalysis_DBInstance, loadDir, barMatDict, self.sectionDXFPath)
        #######################
        axialLoad = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/axialLoad")[0][0]
        moment = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                          f"{groupName}/momentAtPperpendicularDirection")[0][0]
        numIncr =50
        mcInstance.MCAnalysis(axialLoad=axialLoad, moment=moment, numIncr=numIncr)
        # ########################################
        mcInstance.MCCurve(self.mcCurve_figure, self.mcCurve_ax, self.mcCurve_figCanvas,
                           self.sectionDXFPath, groupName, self)
        self.MCCurve_radioButton.setVisible(True)
        self.fiberRes_radioButton.setVisible(True)
        # #######################################################---fibers stress strain display
        coreFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/coreFiberInfo")
        innerCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                       "fiberMesh/innerCoverFiberInfo")
        if innerCoverFiberList is None:
            innerCoverFiberList = []
        outCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                     f"fiberMesh/outCoverFiberInfo")
        if outCoverFiberList is None:
            outCoverFiberList = []
        barsNameList = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath, "fiberMesh", "bars")
        if barsNameList is None:
            barsNameList = []
        barsFiberList = []
        for each in barsNameList:
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/{each}")
            barsFiberList.append(temp)
        # #################################
        self.xPlot = []
        [self.xPlot.append(each[1]) for each in coreFiberList]
        [self.xPlot.append(each[1]) for each in innerCoverFiberList]
        [self.xPlot.append(each[1]) for each in outCoverFiberList]
        [[self.xPlot.append(each[1]) for each in eachType] for eachType in barsFiberList]
        # ################
        self.yPlot = []
        [self.yPlot.append(each[2]) for each in coreFiberList]
        [self.yPlot.append(each[2]) for each in innerCoverFiberList]
        [self.yPlot.append(each[2]) for each in outCoverFiberList]
        [[self.yPlot.append(each[2]) for each in eachType] for eachType in barsFiberList]
        # ##############################
        barColorList = ["k", "brown", "lightblue", "gold"]
        colorsList = []
        for each in coreFiberList:
            colorsList.append("b")
        for each in innerCoverFiberList:
            colorsList.append("g")
        for each in outCoverFiberList:
            colorsList.append("g")
        for i1 in range(len(barsFiberList)):
            color = barColorList[i1 % 4]
            for each in barsFiberList[i1]:
                colorsList.append(color)
        # #######################################
        self.indices = np.arange(len(self.xPlot))
        self.colors = np.array(colorsList)
        self.initial_colors = self.colors.copy()
        markerSize = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/markerSize")[0][0]
        self.sizes = np.full(len(self.xPlot), markerSize)
        # ##########################################
        interFigure = self.fiberInter_figure
        interAx = self.fiberInter_ax
        interCanvas = self.fiberInter_figCanvas
        #####################################################################
        sectionName = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"{groupName}/caseName")[0][0]
        interFigure.suptitle(sectionName + " discreted fiber points")
        self.stacked_widget.setCurrentIndex(2)
        interAx.clear()
        ############################################################
        sectionWidthHeightRatio = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                    f"fiberMesh/sectionWidthHeightRatio")[0][0]
        if self.fiberRespIndexValue == 0:
            self.fiberMesh_figureSize = interFigure.get_size_inches()
            self.fiberRespIndexValue += 1
        sizeValue = self.fiberMesh_figureSize
        originalSizeRatio = sizeValue[0] / float(sizeValue[1])

        if sectionWidthHeightRatio > originalSizeRatio:
            newWidth = sizeValue[0]
            newHeight = sizeValue[0] / float(sectionWidthHeightRatio)
        else:
            newHeight = sizeValue[1]
            newWidth = sizeValue[1] * sectionWidthHeightRatio
        if self.fiberRespIndexValue == 0:
            interFigure.set_figwidth(newWidth)
            interFigure.set_figheight(newHeight)
        #####################################################
        interAx.set_xlabel("Local y direction dimension(m)---y")
        interAx.set_ylabel("Local z direction dimension(m)---z")
        # ######################
        self.scatter = interAx.scatter(self.xPlot, self.yPlot, c=self.colors, picker=True, s=self.sizes)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        interCanvas.draw()
        # ####################################################################################################
        self.fiberIndexDict = {}
        self.fiberIndexDict["coreFiber"] = [each[0] for each in coreFiberList]
        self.fiberIndexDict["innerCoverFiber"] = [each[0] for each in innerCoverFiberList]
        self.fiberIndexDict["outCoverFiber"] = [each[0] for each in outCoverFiberList]
        for i1 in range(len(barsFiberList)):
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/bars_{i1 + 1}")
            self.fiberIndexDict[f"bars_{i1 + 1}"] = [each[0] for each in temp]
        # ###############################################
        # #####################################################################################################
        self.last_clicked = None
        interCanvas.mpl_connect('pick_event', lambda event: self.on_pick(event, self.mc_newAnalysis_DBInstance,
                                                                         self.sectionDXFPath, groupName))
        # #################################################################
        self.cyclicMaterialResponse(matType="coreMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=groupName)
        self.cyclicMaterialResponse(matType="coverMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=groupName)
        for each in barsNameList:
            self.cyclicMaterialResponse(matType=each, dbInstance=self.mc_newAnalysis_DBInstance,
                                        dbPath=self.sectionDXFPath, groupName=groupName)
        # #############################################################
        self.mc_rect_mcAnalysis_button.setText("Start analysis!")
        self.mc_rect_mcAnalysis_button.setStyleSheet("background-color: #7FFFD4;")
        self.mc_rect_mcAnalysis_button.setEnabled(True)
        ##########################################################################
        self.mc_rect_outPutResults_button.setVisible(True)
        # ########################################################################

    def cyclicMaterialResponse(self,matType,dbInstance,dbPath,groupName):
        """calculate cyclic material response"""
        ultStrain = None
        coreParameterList=None
        coverParameterList=None
        if matType == "coreMaterial":
            coreParameterList=dbInstance.getResult(dbPath,f"{groupName}/coreConcreteMatParas")[0]
            ultStrain=coreParameterList[2]*1.5
        elif matType == "coverMaterial":
            coverParameterList=dbInstance.getResult(dbPath, f"{groupName}/coverConcreteMatParas")[0]
            ultStrain = coverParameterList[2] * 1.5
        else:
            ultStrain=0.1*1.5
        #########################
        singleDirNum =50
        iterNum = 10
        strainStep=ultStrain/float(iterNum*singleDirNum)
        #########################
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)  ###for 3D model
        ops.node(1, 0, 0, 0)
        ops.node(2, 0, 0, 0)
        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ########################
        if matType == "coreMaterial":
            ops.uniaxialMaterial('Concrete04', 3, coreParameterList[0], coreParameterList[1], coreParameterList[2],
                                 coreParameterList[3])
            ops.uniaxialMaterial('Elastic', 2, 1)
            ops.uniaxialMaterial('Parallel', 9999, 2, 3)
        elif matType == "coverMaterial":
            ops.uniaxialMaterial('Concrete04', 3, coverParameterList[0], coverParameterList[1], coverParameterList[2],
                                 coverParameterList[3])
            ops.uniaxialMaterial('Elastic', 2, 1)
            ops.uniaxialMaterial('Parallel', 9999, 2, 3)
        else:
            rebarMatParas=dbInstance.getResult(dbPath,f"{groupName}/barMatParas")
            if rebarMatParas is not None:
                barM=rebarMatParas[0]
                ops.uniaxialMaterial('ReinforcingSteel', 33, barM[0], barM[1], barM[2],barM[3], barM[4], barM[5])
                ops.uniaxialMaterial('MinMax', 9999, 33, '-min', -barM[5], '-max', barM[5])
            else:
                rebarMat=f"rebarMaterial_user_{matType.split('_')[1]}"
                temp=dbInstance.getResult(dbPath,f"{groupName}/{rebarMat}")[0][0]
                eval(f"ops.{temp}")
                matTag=int(temp.split(',')[1])
                ops.uniaxialMaterial('Elastic',9998, 1)
                ops.uniaxialMaterial('Parallel', 9999,9998,matTag)
        ########################
        ops.equalDOF(1, 2, 2, 3, 4, 5, 6)
        ops.element('zeroLength', 1, 1, 2, '-mat',9999, '-dir', 1)
        ops.loadConst('-time', 0.0)
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(2, 1, 0.0, 0.0, 0.0, 0.0, 0.0)
        ops.system('UmfPack')
        ops.constraints('Plain')
        ops.numberer('RCM')
        ops.test('NormDispIncr', 1.0e-1, 2000)
        ops.algorithm('KrylovNewton')
        ops.analysis('Static')
        ########################
        ########################
        strainList=[]
        [[[strainList.append(strainStep) for j1 in range(int(singleDirNum*(i1+1)))],
          [strainList.append(-strainStep) for j1 in range(int(singleDirNum * (i1 + 1)))],
          [strainList.append(-strainStep) for j1 in range(int(singleDirNum * (i1 + 1)))],
          [strainList.append(strainStep) for j1 in range(int(singleDirNum * (i1 + 1)))]] for i1 in range(iterNum)]
        resultList = []
        [[ops.integrator('DisplacementControl', 2, 1, eachStrain),ops.analyze(1),
          dispValues:= round(ops.nodeDisp(2, 1), 8),forceValues:= round(ops.eleForce(1, 1) * -1, 8),
        resultList.append([dispValues, forceValues])] for eachStrain in strainList]
        #############################
        stressStrainSaveName = f"{groupName}/{matType}_cyclicResp"
        headNameList = ['strain', 'stress(kPa)']
        operationIndexStr = 'replace'
        dbInstance.saveResult(stressStrainSaveName, resultList, headNameList,
                              operationIndexStr)
        ###############################################

    def on_pick(self, event,dbInstance,dbPath,groupName):
        """"""
        markerSize=dbInstance.getResult(dbPath,f"{groupName}/markerSize")[0][0]
        ##################################################
        artist = event.artist
        if isinstance(artist, collections.PathCollection):
            ind = event.ind
            point_id = self.indices[ind][0]
            if self.last_clicked is not None:
                last_ind = self.last_clicked
                self.colors[last_ind] = self.initial_colors[last_ind]
                self.sizes[last_ind] =markerSize
            self.colors[ind] = 'red'
            self.sizes[ind] =2*markerSize
            self.scatter.set_facecolor(self.colors)
            self.scatter.set_sizes(self.sizes)
            self.fiberInter_figCanvas.draw()
            self.last_clicked = ind
            ############################################
            respType=None
            indexNumber=point_id+1
            for key,value in self.fiberIndexDict.items():
                if indexNumber in value:
                    respType=key
                    break
            ##############################
            self.pickedFiberRespPlot_slot(indexNumber, respType,dbInstance,dbPath,groupName)


    def pickedFiberRespPlot_slot(self,indexNumber,respType,dbInstance,dbPath,groupName):
        """"""
        ############################################---monotonic curve
        if respType == "coreFiber":
            cyclicStressStrain = dbInstance.getResult(dbPath, f"{groupName}/coreMaterial_cyclicResp")
            stressStrain = dbInstance.getResult(dbPath, f"{groupName}/coreFiberResp/{indexNumber}")
        elif respType == "innerCoverFiber":
            cyclicStressStrain = dbInstance.getResult(dbPath, f"{groupName}/coverMaterial_cyclicResp")
            stressStrain = dbInstance.getResult(dbPath, f"{groupName}/innerCoverFiberResp/{indexNumber}")
        elif respType == "outCoverFiber":
            cyclicStressStrain = dbInstance.getResult(dbPath, f"{groupName}/coverMaterial_cyclicResp")
            stressStrain = dbInstance.getResult(dbPath, f"{groupName}/outCoverFiberResp/{indexNumber}")
        else:
            temp = respType.split('_')[1]
            barsName = f"bars_{temp}_cyclicResp"
            cyclicStressStrain = dbInstance.getResult(dbPath, f"{groupName}/{barsName}")
            stressStrain = dbInstance.getResult(dbPath, f"{groupName}/barsResp_{temp}/{indexNumber}")
        ############################################################
        cyclicStrainList=[each[0] for each in cyclicStressStrain]
        cyclicStressList=[each[1]/1000.0 for each in cyclicStressStrain]
        ############################################
        strainList=[each[1] for each in stressStrain]
        stressList=[each[0]/1000.0 for each in stressStrain]
        ############################################
        respFigure = self.fiberRes_figure
        respAx = self.fiberRes_ax
        respCanvas = self.fiberRes_figCanvas
        ############
        respFigure.suptitle(f"fiber point response for-{respType}-{indexNumber}")
        self.stacked_widget.setCurrentIndex(2)
        respAx.clear()
        respAx.set_xlabel("fiber strain")
        respAx.set_ylabel("fiber stress(MPa)")
        respFigure.subplots_adjust(left=0.15)
        figureSize=min(respFigure.get_size_inches())
        respFigure.set_size_inches(figureSize,figureSize)
        respAx.grid(True,linestyle='--', color='gray',linewidth=0.2)
        ###############
        # if strainList[-1]>0:
        #     respAx.plot(monotonicStrainList,monotonicStressList,c='b',linestyle='--',linewidth=1)
        # else:
        #     respAx.plot([-each for each in monotonicStrainList], [-each for each in monotonicStressList],
        #                 c='b', linestyle='--', linewidth=1)
        respAx.plot(cyclicStrainList,cyclicStressList,c='k',linestyle='--',linewidth=0.3)
        ###############################################
        #################################################
        yMaxValue=max(np.abs(respAx.get_ylim()))
        keyPointList=dbInstance.getResult(dbPath,f"{groupName}/pointsIndex")
        if keyPointList is not None:
            keyPointList=keyPointList[0]
            yieldX=strainList[keyPointList[0]]
            effectiveX=strainList[keyPointList[1]]
            maximumX=strainList[keyPointList[2]]
            ultimateX=strainList[keyPointList[3]]
            yieldLineX,yieldLineY=[yieldX,yieldX],[-yMaxValue,yMaxValue]
            effectiveLineX,effectiveLineY=[effectiveX,effectiveX],[-yMaxValue,yMaxValue]
            maximumLineX,maximumLineY=[maximumX,maximumX],[-yMaxValue,yMaxValue]
            ultimateLineX,ultimateLineY=[ultimateX,ultimateX],[-yMaxValue,yMaxValue]
            respAx.plot(yieldLineX, yieldLineY, c='green', linestyle='--', linewidth=0.6, label="Yield")
            respAx.plot(effectiveLineX,effectiveLineY, c='blue', linestyle='--', linewidth=0.6, label="Effective")
            respAx.plot(maximumLineX, maximumLineY, c='purple', linestyle='--', linewidth=0.6, label="Maximum")
            respAx.plot(ultimateLineX, ultimateLineY, c='red', linestyle='--', linewidth=0.6, label="Ultimate")
            #################################################
            respAx.plot(strainList, stressList, c='r', linestyle='--', linewidth=1)
            respAx.legend(loc="lower right")
        else:
            respAx.plot(strainList, stressList, c='r', linestyle='--', linewidth=1)
        respCanvas.draw()
        #################################################


    def rightPanel_mc_circleSect_frame_ui(self):
        """"""
        self.rightPanel_mc_circle_formLayout = QFormLayout(self.rightPanel_mc_circleSect_initFrame)
        #########################################
        mc_caseName_label = QLabel("Case Name:")
        self.mc_circle_caseName_lineEdit = QLineEdit("defaultName",toolTip="Please input the case name!")
        self.rightPanel_mc_circle_formLayout.addRow(mc_caseName_label, self.mc_circle_caseName_lineEdit)
        #########################################
        coreMaterial_label = QLabel("Concrete material:")
        #######
        self.circle_coreMaterial_ComboBox = QComboBox()
        self.circle_coreMaterial_ComboBox.addItems(
            ["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
             "C65", "C70", "C75", "C80", "User"])
        self.circle_coreMaterial_ComboBox.currentTextChanged.connect(self.circle_coreMaterial_ComboBox_slot)
        ############################################

        coreUserToolTip=("Input parameters of unconfied concrete: 1. fc --concrete compressive strength at 28 days(kPa)"
        "2. ec --concrete strain at maximum strength 3. ecu-- concrete strain at crushing strength 4. Ec--initial stiffness(kPa)")
        self.circle_userCoreMaterial_lineEdit = QLineEdit("[-26752, -0.002, -0.004, 25861168]",toolTip=coreUserToolTip)
        self.circle_userCoreMaterial_lineEdit.setVisible(False)
        ########################
        hBox_1 = QHBoxLayout()
        hBox_1.addWidget(coreMaterial_label)
        hBox_1.addWidget(self.circle_coreMaterial_ComboBox)
        self.rightPanel_mc_circle_formLayout.addRow(hBox_1)
        self.rightPanel_mc_circle_formLayout.addRow(self.circle_userCoreMaterial_lineEdit)
        ##############################################################################
        rebarMaterial_label = QLabel("Rebar material:")
        #######
        self.circle_rebarMaterial_ComboBox = QComboBox()
        self.circle_rebarMaterial_ComboBox.addItems(["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400",
                            "RRB400", "HRB500","HRBF500","User"])
        self.circle_rebarMaterial_ComboBox.currentTextChanged.connect(self.circle_rebarMaterial_ComboBox_slot)
        ############################################
        defaultStr="uniaxialMaterial('ReinforcingSteel',1,400000, 510000, 200000000, 2000000, 0.045, 0.1)"
        toopTipStr=("Input the rebar material using the unixialMaterial in OpenSeesPy,unit: kN,m,kPa;each material is "
                    "seperated by line break, and the first material corresponding to 'rebars_1' as a named dxf layer, "
                    "and so on!")
        self.circle_userRebarMaterial_textEdit = QTextEdit(defaultStr,toolTip=toopTipStr)
        self.circle_userRebarMaterial_textEdit.setFixedHeight(60)
        self.circle_userRebarMaterial_textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.circle_userRebarMaterial_textEdit.setVisible(False)
        ########################
        hBox_2 = QHBoxLayout()
        hBox_2.addWidget(rebarMaterial_label)
        hBox_2.addWidget(self.circle_rebarMaterial_ComboBox)
        self.rightPanel_mc_circle_formLayout.addRow(hBox_2)
        self.rightPanel_mc_circle_formLayout.addRow(self.circle_userRebarMaterial_textEdit)
        ##############################################################################
        stirrupType_label = QLabel("Stirrup type:")
        #######
        self.circle_stirrupType_ComboBox = QComboBox()
        self.circle_stirrupType_ComboBox.addItems(["Circular", "Spiral"])
        #######
        self.rightPanel_mc_circle_formLayout.addRow(stirrupType_label, self.circle_stirrupType_ComboBox)
        ####################################################################################
        stirrupDiameter_label = QLabel("Stirrup diameter (m):")
        #######
        self.mc_circle_stirrupDiameter_lineEdit = QLineEdit(toolTip="Input the diameter of stirrup (m)")
        self.mc_circle_stirrupDiameter_lineEdit.setText("0.014")
        self.rightPanel_mc_circle_formLayout.addRow(stirrupDiameter_label, self.mc_circle_stirrupDiameter_lineEdit)
        ####################################################################################
        stirrupSpace_label = QLabel("Stirrup space (m):")
        #######
        self.mc_circle_stirrupSpace_lineEdit = QLineEdit(toolTip="Input the space of stirrup (m)")
        self.mc_circle_stirrupSpace_lineEdit.setText("0.1")
        self.rightPanel_mc_circle_formLayout.addRow(stirrupSpace_label, self.mc_circle_stirrupSpace_lineEdit)
        ####################################################################################
        stirrupYieldStrength_label = QLabel("Stirrup yield strength (MPa):")
        #######
        self.mc_circle_stirrupYieldStength_lineEdit = QLineEdit(toolTip="Input the yield strength of stirrup (MPa)")
        self.mc_circle_stirrupYieldStength_lineEdit.setText("400")
        self.rightPanel_mc_circle_formLayout.addRow(stirrupYieldStrength_label, self.mc_circle_stirrupYieldStength_lineEdit)
        ####################################################################################
        axialLoad_label = QLabel("Axial load (kN):")
        #######
        self.mc_circle_axialLoad_lineEdit = QLineEdit(toolTip="Input the axial load, negative value is compressive load (kN)")
        self.mc_circle_axialLoad_lineEdit.setText("-3000")
        self.rightPanel_mc_circle_formLayout.addRow(axialLoad_label, self.mc_circle_axialLoad_lineEdit)
        ####################################################################################
        self.circle_loadingY_radioButton = QRadioButton("local Y", self)
        self.circle_loadingZ_radioButton = QRadioButton("local Z", self)
        self.circle_loadingY_radioButton.setChecked(True)
        self.circle_loadingY_radioButton.clicked.connect(self.circle_loadingY_radioButton_slot)
        self.circle_loadingZ_radioButton.clicked.connect(self.circle_loadingZ_radioButton_slot)
        #################
        self.circle_loadingDir_buttonGroup = QButtonGroup(self)
        self.circle_loadingDir_buttonGroup.addButton(self.circle_loadingY_radioButton)
        self.circle_loadingDir_buttonGroup.addButton(self.circle_loadingZ_radioButton)
        ###############
        loadingDir_label = QLabel("Loading direction:")
        ###############
        hBox_3 = QHBoxLayout()
        hBox_3.addWidget(self.circle_loadingY_radioButton)
        hBox_3.addWidget(self.circle_loadingZ_radioButton)
        ################
        self.rightPanel_mc_circle_formLayout.addRow(loadingDir_label,hBox_3)
        ########################################################
        self.circle_momentLocal_label = QLabel("Moment at local Z(kN.m)")
        #######
        self.circle_momentLocal_lineEdit = QLineEdit(
            toolTip="Input the moment value perpendicular to the loading direction (kN.m)")
        self.circle_momentLocal_lineEdit.setText("0")
        self.rightPanel_mc_circle_formLayout.addRow(self.circle_momentLocal_label, self.circle_momentLocal_lineEdit)
        ####################################################################################
        targetDuctilityFactor_label = QLabel("Mu:")
        self.circle_targetDuctilityFactor_lineEdit = QLineEdit(toolTip="Input the expected ductility factor")
        self.circle_targetDuctilityFactor_lineEdit.setText("60")
        self.rightPanel_mc_circle_formLayout.addRow(targetDuctilityFactor_label,
                                                    self.circle_targetDuctilityFactor_lineEdit)
        ####################################################################################
        markerSize_label = QLabel("MarkerSize:")
        self.circle_markerSize_lineEdit = QLineEdit(toolTip="Input the marker size of the discrted fiber plot!")
        self.circle_markerSize_lineEdit.setText("5")
        self.rightPanel_mc_circle_formLayout.addRow(markerSize_label,
                                                    self.circle_markerSize_lineEdit)
        ####################################################################################
        self.mc_circle_mcAnalysis_button = QPushButton("Start analysis!")
        self.mc_circle_mcAnalysis_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.mc_circle_mcAnalysis_button.clicked.connect(self.mc_circle_mcAnalysis_button_slot)
        self.rightPanel_mc_circle_formLayout.addRow(self.mc_circle_mcAnalysis_button)
        ####################################################################################
        self.mc_circle_outPutResults_button = QPushButton("Output all results!")
        self.mc_circle_outPutResults_button.setVisible(False)
        self.mc_circle_outPutResults_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.mc_circle_outPutResults_button.clicked.connect(self.mc_circle_outPutResults_button_slot)
        self.rightPanel_mc_circle_formLayout.addRow(self.mc_circle_outPutResults_button)
        ####################################################################################

    def mc_circle_outPutResults_button_slot(self):
        """"""
        dirName = os.path.dirname(self.sectionDXFPath)
        caseName = self.mc_circle_caseName_lineEdit.text()
        savePath = dirName + f"/{self.sectionDXFName}-{caseName}-outPutAllResults"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        ############################################
        self._mc_saveFiberInfo_process(caseName)
        self._mc_saveMatParas_process(caseName)
        self._mc_savePushOverResults_process(caseName)
        ##################################

    def _mc_savePushOverResults_process(self,caseName):
        """"""
        dirName = os.path.dirname(self.sectionDXFPath)
        savePath = dirName + f"/{self.sectionDXFName}-{caseName}-outPutAllResults/momentCurvatureResults"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        #################################
        dataPath = dirName + f"/{self.sectionDXFName}.h5"
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/node2_disp"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[round(each[0],8), round(each[1], 8)] for each in resultList]
            headName = ["moment(kN.m)", "curvature"]
            saveFiberPath = savePath + f"/momentCurvature.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        groupName=f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}"
        barsNameList=MCAnalysisResultDB.partialMatchDataSets(dataPath,groupName,"bars_")
        for eachbar in range(len(barsNameList)):
            dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/barsResp_{int(eachbar+1)}"
            os.makedirs(savePath+f"/barsResp_{int(eachbar+1)}")
            dataset_names=self.mc_newAnalysis_DBInstance.dataSetsInGroup(dataPath,dataName)
            for dataSetName in dataset_names:
                setName=dataName+f"/{dataSetName}"
                resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, setName)
                if resultList is not None:
                    resultList = [[round(each[0], 12), round(each[1], 12)] for each in resultList]
                    headName = ["stress(kPa)", "strain"]
                    saveFiberPath = savePath+f"/barsResp_{int(eachbar+1)}" + f"/{dataSetName}.txt"
                    with open(saveFiberPath, "w") as file:
                        file.write("\t".join(headName) + "\n")
                        for eachRow in resultList:
                            file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/coreFiberResp"
        os.makedirs(savePath + f"/coreFiberResp")
        dataset_names = self.mc_newAnalysis_DBInstance.dataSetsInGroup(dataPath, dataName)
        for dataSetName in dataset_names:
            setName = dataName + f"/{dataSetName}"
            resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, setName)
            if resultList is not None:
                resultList = [[round(each[0], 12), round(each[1], 12)] for each in resultList]
                headName = ["stress(kPa)", "strain"]
                saveFiberPath = savePath + f"/coreFiberResp" + f"/{dataSetName}.txt"
                with open(saveFiberPath, "w") as file:
                    file.write("\t".join(headName) + "\n")
                    for eachRow in resultList:
                        file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/innerCoverFiberResp"
        os.makedirs(savePath + f"/innerCoverFiberResp")
        dataset_names = self.mc_newAnalysis_DBInstance.dataSetsInGroup(dataPath, dataName)
        if dataset_names is not None:
            for dataSetName in dataset_names:
                setName = dataName + f"/{dataSetName}"
                resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, setName)
                if resultList is not None:
                    resultList = [[round(each[0], 12), round(each[1], 12)] for each in resultList]
                    headName = ["stress(kPa)", "strain"]
                    saveFiberPath = savePath + f"/innerCoverFiberResp" + f"/{dataSetName}.txt"
                    with open(saveFiberPath, "w") as file:
                        file.write("\t".join(headName) + "\n")
                        for eachRow in resultList:
                            file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/outCoverFiberResp"
        os.makedirs(savePath + f"/outCoverFiberResp")
        dataset_names = self.mc_newAnalysis_DBInstance.dataSetsInGroup(dataPath, dataName)
        if dataset_names is not None:
            for dataSetName in dataset_names:
                setName = dataName + f"/{dataSetName}"
                resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, setName)
                if resultList is not None:
                    resultList = [[round(each[0], 12), round(each[1], 12)] for each in resultList]
                    headName = ["stress(kPa)", "strain"]
                    saveFiberPath = savePath + f"/outCoverFiberResp" + f"/{dataSetName}.txt"
                    with open(saveFiberPath, "w") as file:
                        file.write("\t".join(headName) + "\n")
                        for eachRow in resultList:
                            file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################

    def _mc_saveMatParas_process(self,caseName):
        """"""
        dirName = os.path.dirname(self.sectionDXFPath)
        savePath = dirName + f"/{self.sectionDXFName}-{caseName}-outPutAllResults/matPropertyInfo"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        #################################
        dataPath = dirName + f"/{self.sectionDXFName}.h5"
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/barMatParas"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[round(each[0],8), round(each[1], 8), round(each[2], 8), round(each[3], 8),
                           round(each[4],8),round(each[5],8)] for each in resultList]
            headName = ["yieldStrengthInTension(kPa)", "ultimateStressInTension(kPa)",
                        "initialElasticTangent(kPa)", "tangentAtInitialStrainHardening(kPa)",
                        "strainCorrespondingToInitialStrainHardening","strainAtPeakStress"]
            saveFiberPath = savePath + f"/barMatParas.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        dataPath = dirName + f"/{self.sectionDXFName}.h5"
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/coverConcreteMatParas"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[round(each[0], 8), round(each[1], 8), round(each[2], 8),
                           round(each[3], 8)] for each in resultList]
            headName = ["concreteCompressiveStrengthAt28Days(kPa)", "concreteStrainAtMaximumStrength",
                        "concreteStrainAtCrushingStrength", "initialStiffness(kPa)"]
            saveFiberPath = savePath + f"/coverConcreteMatParas.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################
        dataPath = dirName + f"/{self.sectionDXFName}.h5"
        dataName = f"mc_analysis_{self.mc_circle_caseName_lineEdit.text()}/coreConcreteMatParas"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[round(each[0], 8), round(each[1], 8), round(each[2], 8),
                           round(each[3], 8)] for each in resultList]
            headName = ["concreteCompressiveStrengthAt28Days(kPa)", "concreteStrainAtMaximumStrength",
                        "concreteStrainAtCrushingStrength", "initialStiffness(kPa)"]
            saveFiberPath = savePath + f"/coreConcreteMatParas.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ########################################

    def _mc_saveFiberInfo_process(self,caseName):
        """"""
        dirName=os.path.dirname(self.sectionDXFPath)
        savePath = dirName + f"/{self.sectionDXFName}-{caseName}-outPutAllResults/fiberInfo"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        ######################################
        dataPath = dirName + f"/{self.sectionDXFName}.h5"
        dataName = f"fiberMesh/coreFiberInfo"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in resultList]
            headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
            saveFiberPath = savePath + f"/coreFiberInfo.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ############################################
        dataName = f"fiberMesh/innerCoverFiberInfo"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in resultList]
            headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
            saveFiberPath = savePath + f"/innerCoverFiberInfo.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ###############################################
        dataName = f"fiberMesh/outCoverFiberInfo"
        resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in resultList]
            headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
            saveFiberPath = savePath + f"/outCoverFiberInfo.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        #################################################
        dataName = f"fiberMesh/barFiberName"
        barsName = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
        if barsName is not None:
            for each in barsName:
                dataName = f"fiberMesh/{each[0]}"
                resultList = self.mc_newAnalysis_DBInstance.getResult(dataPath, dataName)
                if resultList is not None:
                    resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in
                                  resultList]
                    headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
                    saveFiberPath = savePath + f"/{each[0]}_FiberInfo.txt"
                    with open(saveFiberPath, "w") as file:
                        file.write("\t".join(headName) + "\n")
                        for eachRow in resultList:
                            file.write("\t".join(map(str, eachRow)) + "\n")
        #################################################

    @Slot(str)
    def rect_coreMaterial_ComboBox_slot(self, selectedText):
        """"""
        if selectedText == "User":
            self.rect_userCoreMaterial_lineEdit.setVisible(True)
        else:
            self.rect_userCoreMaterial_lineEdit.setVisible(False)

    @Slot(str)
    def rect_rebarMaterial_ComboBox_slot(self, selectedText):
        if selectedText == "User":
            self.rect_userRebarMaterial_textEdit.setVisible(True)
        else:
            self.rect_userRebarMaterial_textEdit.setVisible(False)

    def rightPanel_mc_rectSect_frame_ui(self):
        """"""
        self.rightPanel_mc_rect_formLayout = QFormLayout(self.rightPanel_mc_rectSect_initFrame)
        #########################################
        mc_caseName_label = QLabel("Case Name:")
        self.mc_rect_caseName_lineEdit = QLineEdit("defaultName", toolTip="Please input the case name!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_caseName_label, self.mc_rect_caseName_lineEdit)
        #########################################
        coreMaterial_label = QLabel("Concrete material:")
        #######
        self.rect_coreMaterial_ComboBox = QComboBox()
        self.rect_coreMaterial_ComboBox.addItems(
            ["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
             "C65", "C70", "C75", "C80", "User"])
        self.rect_coreMaterial_ComboBox.currentTextChanged.connect(self.rect_coreMaterial_ComboBox_slot)
        ############################################

        coreUserToolTip = (
            "Input parameters of unconfied concrete: 1. fc --concrete compressive strength at 28 days(kPa)"
            "2. ec --concrete strain at maximum strength 3. ecu-- concrete strain at crushing strength 4. Ec--initial stiffness(kPa)")
        self.rect_userCoreMaterial_lineEdit = QLineEdit("[-26752, -0.002, -0.004, 25861168]", toolTip=coreUserToolTip)
        self.rect_userCoreMaterial_lineEdit.setVisible(False)
        ########################
        self.rightPanel_mc_rect_formLayout.addRow(coreMaterial_label,self.rect_coreMaterial_ComboBox)
        self.rightPanel_mc_rect_formLayout.addRow(self.rect_userCoreMaterial_lineEdit)
        ##############################################################################
        rebarMaterial_label = QLabel("Rebar material:")
        #######
        self.rect_rebarMaterial_ComboBox = QComboBox()
        self.rect_rebarMaterial_ComboBox.addItems(["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400",
                                                     "RRB400", "HRB500", "HRBF500", "User"])
        self.rect_rebarMaterial_ComboBox.currentTextChanged.connect(self.rect_rebarMaterial_ComboBox_slot)
        ############################################
        defaultStr = "uniaxialMaterial('ReinforcingSteel',1,400000, 510000, 200000000, 2000000, 0.045, 0.1)"
        toopTipStr = (
            "Input the rebar material using the unixialMaterial in OpenSeesPy,unit: kN,m,kPa;each material is "
            "seperated by line break, and the first material corresponding to 'rebars_1' as a named dxf layer, "
            "and so on!")
        self.rect_userRebarMaterial_textEdit = QTextEdit(defaultStr, toolTip=toopTipStr)
        self.rect_userRebarMaterial_textEdit.setFixedHeight(60)
        self.rect_userRebarMaterial_textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rect_userRebarMaterial_textEdit.setVisible(False)
        ########################
        self.rightPanel_mc_rect_formLayout.addRow(rebarMaterial_label,self.rect_rebarMaterial_ComboBox)
        self.rightPanel_mc_rect_formLayout.addRow(self.rect_userRebarMaterial_textEdit)
        ##############################################################################
        mc_rebarSpace_label = QLabel("Rebar space (m):")
        self.mc_rect_rebarSpace_lineEdit = QLineEdit("0.15", toolTip="Please input the longitudinal rebar space (m)!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_rebarSpace_label, self.mc_rect_rebarSpace_lineEdit)
        #########################################
        mc_stirrupRatioY_label = QLabel("stirrup volume ratio in Y direction:")
        self.mc_rect_stirrupRatioY_lineEdit = QLineEdit("0.005",
                            toolTip="Please input the stirrup reinforcement volume ratio in local Y direction!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_stirrupRatioY_label, self.mc_rect_stirrupRatioY_lineEdit)
        #########################################
        mc_stirrupRatioZ_label = QLabel("stirrup volume ratio in Z direction:")
        self.mc_rect_stirrupRatioZ_lineEdit = QLineEdit("0.005",
                        toolTip="Please input the stirrup reinforcement volume ratio in local Z direction!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_stirrupRatioZ_label, self.mc_rect_stirrupRatioZ_lineEdit)
        #########################################
        mc_stirrupSpace_label = QLabel("Stirrup space (m):")
        self.mc_rect_stirrupSpace_lineEdit = QLineEdit("0.1",
                                                        toolTip="Please input the stirrup space (m)!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_stirrupSpace_label, self.mc_rect_stirrupSpace_lineEdit)
        #########################################
        mc_stirrupDiameter_label = QLabel("Stirrup diameter (m):")
        self.mc_rect_stirrupDiameter_lineEdit = QLineEdit("0.014",
                                                       toolTip="Please input the stirrup diameter (m)!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_stirrupDiameter_label, self.mc_rect_stirrupDiameter_lineEdit)
        #########################################
        mc_stirrupYieldStrength_label = QLabel("Stirrup yield strength (MPa):")
        self.mc_rect_stirrupYieldStrength_lineEdit = QLineEdit("400",
                                                          toolTip="Please input the stirrup yield strength (m)!")
        self.rightPanel_mc_rect_formLayout.addRow(mc_stirrupYieldStrength_label, self.mc_rect_stirrupYieldStrength_lineEdit)
        #########################################
        axialLoad_label = QLabel("Axial load (kN):")
        #######
        self.mc_rect_axialLoad_lineEdit = QLineEdit(
            toolTip="Input the axial load, negative value is compressive load (kN)")
        self.mc_rect_axialLoad_lineEdit.setText("-3000")
        self.rightPanel_mc_rect_formLayout.addRow(axialLoad_label, self.mc_rect_axialLoad_lineEdit)
        ####################################################################################
        self.rect_loadingY_radioButton = QRadioButton("local Y", self)
        self.rect_loadingZ_radioButton = QRadioButton("local Z", self)
        self.rect_loadingY_radioButton.setChecked(True)
        self.rect_loadingY_radioButton.clicked.connect(self.rect_loadingY_radioButton_slot)
        self.rect_loadingZ_radioButton.clicked.connect(self.rect_loadingZ_radioButton_slot)
        #################
        self.rect_loadingDir_buttonGroup = QButtonGroup(self)
        self.rect_loadingDir_buttonGroup.addButton(self.rect_loadingY_radioButton)
        self.rect_loadingDir_buttonGroup.addButton(self.rect_loadingZ_radioButton)
        ###############
        loadingDir_label = QLabel("Loading direction:")
        ###############
        hBox_3 = QHBoxLayout()
        hBox_3.addWidget(self.rect_loadingY_radioButton)
        hBox_3.addWidget(self.rect_loadingZ_radioButton)
        ################
        self.rightPanel_mc_rect_formLayout.addRow(loadingDir_label, hBox_3)
        ########################################################
        self.rect_momentLocal_label = QLabel("Moment at local Z(kN.m)")
        #######
        self.rect_momentLocal_lineEdit = QLineEdit(
            toolTip="Input the moment value perpendicular to the loading direction (kN.m)")
        self.rect_momentLocal_lineEdit.setText("0")
        self.rightPanel_mc_rect_formLayout.addRow(self.rect_momentLocal_label, self.rect_momentLocal_lineEdit)
        ####################################################################################
        targetDuctilityFactor_label = QLabel("Mu:")
        self.rect_targetDuctilityFactor_lineEdit = QLineEdit(toolTip="Input the expected ductility factor")
        self.rect_targetDuctilityFactor_lineEdit.setText("30")
        self.rightPanel_mc_rect_formLayout.addRow(targetDuctilityFactor_label,
                                                    self.rect_targetDuctilityFactor_lineEdit)
        ####################################################################################
        markerSize_label = QLabel("MarkerSize:")
        self.rect_markerSize_lineEdit = QLineEdit(toolTip="Input the marker size of the discrted fiber plot!")
        self.rect_markerSize_lineEdit.setText("5")
        self.rightPanel_mc_rect_formLayout.addRow(markerSize_label,
                                                    self.rect_markerSize_lineEdit)
        ####################################################################################
        ####################################################################################
        self.mc_rect_mcAnalysis_button = QPushButton("Start analysis!")
        self.mc_rect_mcAnalysis_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.mc_rect_mcAnalysis_button.clicked.connect(self.mc_rect_mcAnalysis_button_slot)
        self.rightPanel_mc_rect_formLayout.addRow(self.mc_rect_mcAnalysis_button)
        ####################################################################################
        self.mc_rect_outPutResults_button = QPushButton("Output all results!")
        self.mc_rect_outPutResults_button.setVisible(False)
        self.mc_rect_outPutResults_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.mc_rect_outPutResults_button.clicked.connect(self.mc_rect_outPutResults_button_slot)
        self.rightPanel_mc_rect_formLayout.addRow(self.mc_rect_outPutResults_button)
        ####################################################################################

    def mc_rect_outPutResults_button_slot(self):
        """"""
        dirName = os.path.dirname(self.sectionDXFPath)
        caseName=self.mc_rect_caseName_lineEdit.text()
        savePath = dirName + f"/{self.sectionDXFName}-{caseName}-outPutAllResults"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        ############################################
        self._mc_saveFiberInfo_process(caseName)
        self._mc_saveMatParas_process(caseName)
        self._mc_savePushOverResults_process(caseName)
        ##################################

    @Slot(str)
    def mc_sectionName_ComboBox_slot(self,selectedText):
        """"""
        self.mcResultGroupName=f"mc_analysis_{selectedText}"
        dataName=f"{self.mcResultGroupName}/sectionType"
        sectionType=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,dataName)
        if sectionType is not None:
            if sectionType[0][0]=="Rect":
                self.rightPanel_mc_sectType_rect_radioButton.setChecked(True)
                self.rightPanel_mc_stacked_widget.setVisible(True)
                self.rightPanel_mc_stacked_widget.setCurrentIndex(1)
                self.mc_rect_mcAnalysis_button.setVisible(False)
                self.mc_rect_outPutResults_button.setVisible(True)
                self.mc_openResult_rect_process()
            elif sectionType[0][0]=="Circle":
                self.rightPanel_mc_sectType_circle_radioButton.setChecked(True)
                self.rightPanel_mc_stacked_widget.setVisible(True)
                self.rightPanel_mc_stacked_widget.setCurrentIndex(0)
                self.mc_circle_mcAnalysis_button.setVisible(False)
                self.mc_circle_outPutResults_button.setVisible(True)
                self.mc_openResult_circle_process()

    def mc_openResult_circle_process(self):
        """"""
        caseName = self.mcResultGroupName.split("_")[-1]
        self.mc_circle_caseName_lineEdit.setText(caseName)
        ####################
        dataName = f"{self.mcResultGroupName}/coreMaterial"
        concreteMaterial = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)
        matTags = ["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
                   "C65", "C70", "C75", "C80", "User"]
        if concreteMaterial is not None:
            matName = concreteMaterial[0][0]
            matIndex = matTags.index(matName)
            self.circle_coreMaterial_ComboBox.setCurrentIndex(matIndex)
        else:
            dataName = f"{self.mcResultGroupName}/coreMaterial_user"
            concreteMaterial_user = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)
            matIndex = matTags.index("User")
            self.circle_coreMaterial_ComboBox.setCurrentIndex(matIndex)
            self.circle_userCoreMaterial_lineEdit.setText(concreteMaterial_user[0][0])
            self.circle_userCoreMaterial_lineEdit.setVisible(True)
        #####################
        dataName = f"{self.mcResultGroupName}/rebarMaterial"
        rebarMaterial = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)
        rebarMatTag = ["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400", "RRB400", "HRB500", "HRBF500",
                       "User"]
        if rebarMaterial is not None:
            matName = rebarMaterial[0][0]
            matIndex = rebarMatTag.index(matName)
            self.circle_rebarMaterial_ComboBox.setCurrentIndex(matIndex)
        else:
            matIndex = rebarMatTag.index("User")
            self.circle_rebarMaterial_ComboBox.setCurrentIndex(matIndex)
            self.circle_userRebarMaterial_textEdit.clear()
            matNameList = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,
                                        self.mcResultGroupName,"rebarMaterial_user")
            for eachName in matNameList:
                dataName = f"{self.mcResultGroupName}/{eachName}"
                rebarMat = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
                self.circle_userRebarMaterial_textEdit.append(rebarMat)
        #############################
        dataName = f"{self.mcResultGroupName}/stirrupType"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        if getResult=="Spiral":
            self.circle_stirrupType_ComboBox.setCurrentIndex(1)
        else:
            self.circle_stirrupType_ComboBox.setCurrentIndex(0)
        # ###########################
        dataName = f"{self.mcResultGroupName}/stirrupDiameter"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_circle_stirrupDiameter_lineEdit.setText(str(round(getResult, 6)))
        # #########################
        dataName = f"{self.mcResultGroupName}/stirrupSpace"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_circle_stirrupSpace_lineEdit.setText(str(round(getResult, 6)))
        ###########################
        dataName = f"{self.mcResultGroupName}/stirrupYieldStrength"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_circle_stirrupYieldStength_lineEdit.setText(str(round(getResult, 6)))
        # #########################
        dataName = f"{self.mcResultGroupName}/axialLoad"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_circle_axialLoad_lineEdit.setText(str(round(getResult, 6)))
        # #########################
        dataName = f"{self.mcResultGroupName}/loadingDirection"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        if getResult == "localZ":
            self.circle_loadingZ_radioButton.setChecked(True)
        else:
            self.circle_loadingY_radioButton.setChecked(True)
        ##########################
        dataName = f"{self.mcResultGroupName}/momentAtPperpendicularDirection"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.circle_momentLocal_lineEdit.setText(str(round(getResult, 6)))
        ##########################
        dataName = f"{self.mcResultGroupName}/Mu"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.circle_targetDuctilityFactor_lineEdit.setText(str(round(getResult, 6)))
        ##########################
        dataName = f"{self.mcResultGroupName}/markerSize"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.circle_markerSize_lineEdit.setText(str(round(getResult, 6)))
        ########################################################################################---MC plot
        #########################################################################################
        mcInstance = MC(self.mcResultGroupName, self.mc_newAnalysis_DBInstance, None, None, self.sectionDXFPath)

        mcInstance.MCCurve(self.mcCurve_figure, self.mcCurve_ax, self.mcCurve_figCanvas,
                           self.sectionDXFPath, self.mcResultGroupName, self)
        self.MCCurve_radioButton.setVisible(True)
        self.fiberRes_radioButton.setVisible(True)
        #######################################################---fibers stress strain display
        coreFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/coreFiberInfo")
        innerCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                       "fiberMesh/innerCoverFiberInfo")
        if innerCoverFiberList is None:
            innerCoverFiberList = []
        outCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                     f"fiberMesh/outCoverFiberInfo")
        if outCoverFiberList is None:
            outCoverFiberList = []
        barsNameList = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath, "fiberMesh", "bars")
        if barsNameList is None:
            barsNameList = []
        barsFiberList = []
        for each in barsNameList:
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/{each}")
            barsFiberList.append(temp)
        # #################################
        self.xPlot = []
        [self.xPlot.append(each[1]) for each in coreFiberList]
        [self.xPlot.append(each[1]) for each in innerCoverFiberList]
        [self.xPlot.append(each[1]) for each in outCoverFiberList]
        [[self.xPlot.append(each[1]) for each in eachType] for eachType in barsFiberList]
        # ################
        self.yPlot = []
        [self.yPlot.append(each[2]) for each in coreFiberList]
        [self.yPlot.append(each[2]) for each in innerCoverFiberList]
        [self.yPlot.append(each[2]) for each in outCoverFiberList]
        [[self.yPlot.append(each[2]) for each in eachType] for eachType in barsFiberList]
        # # # ##############################
        barColorList = ["k", "brown", "lightblue", "gold"]
        colorsList = []
        for each in coreFiberList:
            colorsList.append("b")
        for each in innerCoverFiberList:
            colorsList.append("g")
        for each in outCoverFiberList:
            colorsList.append("g")
        for i1 in range(len(barsFiberList)):
            color = barColorList[i1 % 4]
            for each in barsFiberList[i1]:
                colorsList.append(color)
        # #######################################
        self.indices = np.arange(len(self.xPlot))
        self.colors = np.array(colorsList)
        self.initial_colors = self.colors.copy()
        markerSize = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                              f"{self.mcResultGroupName}/markerSize")[0][0]
        self.sizes = np.full(len(self.xPlot), markerSize)
        # ##########################################
        interFigure = self.fiberInter_figure
        interAx = self.fiberInter_ax
        interCanvas = self.fiberInter_figCanvas
        #####################################################################
        sectionName = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                               f"{self.mcResultGroupName}/caseName")[0][0]
        interFigure.suptitle(sectionName + " discreted fiber points")
        self.stacked_widget.setCurrentIndex(2)
        interAx.clear()
        ############################################################
        sectionWidthHeightRatio = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                    f"fiberMesh/sectionWidthHeightRatio")[0][0]
        if self.fiberRespIndexValue == 0:
            self.fiberMesh_figureSize = interFigure.get_size_inches()
            self.fiberRespIndexValue += 1
        sizeValue = self.fiberMesh_figureSize
        originalSizeRatio = sizeValue[0] / float(sizeValue[1])

        if sectionWidthHeightRatio > originalSizeRatio:
            newWidth = sizeValue[0]
            newHeight = sizeValue[0] / float(sectionWidthHeightRatio)
        else:
            newHeight = sizeValue[1]
            newWidth = sizeValue[1] * sectionWidthHeightRatio
        if self.fiberRespIndexValue == 0:
            interFigure.set_figwidth(newWidth)
            interFigure.set_figheight(newHeight)
        #####################################################
        interAx.set_xlabel("Local y direction dimension(m)---y")
        interAx.set_ylabel("Local z direction dimension(m)---z")
        # ######################
        self.scatter = interAx.scatter(self.xPlot, self.yPlot, c=self.colors, picker=True, s=self.sizes)
        figureSize = min(interFigure.get_size_inches())
        interFigure.set_figwidth(figureSize)
        interFigure.set_figheight(figureSize)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        interCanvas.draw()
        ####################################################################################################
        self.fiberIndexDict = {}
        self.fiberIndexDict["coreFiber"] = [each[0] for each in coreFiberList]
        self.fiberIndexDict["innerCoverFiber"] = [each[0] for each in innerCoverFiberList]
        self.fiberIndexDict["outCoverFiber"] = [each[0] for each in outCoverFiberList]
        for i1 in range(len(barsFiberList)):
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/bars_{i1 + 1}")
            self.fiberIndexDict[f"bars_{i1 + 1}"] = [each[0] for each in temp]
        ###############################################
        #####################################################################################################
        self.last_clicked = None
        interCanvas.mpl_connect('pick_event', lambda event: self.on_pick(event, self.mc_newAnalysis_DBInstance,
                                                                         self.sectionDXFPath, self.mcResultGroupName))
        # #################################################################
        self.cyclicMaterialResponse(matType="coreMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        self.cyclicMaterialResponse(matType="coverMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        for each in barsNameList:
            self.cyclicMaterialResponse(matType=each, dbInstance=self.mc_newAnalysis_DBInstance,
                                        dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        #############################################################

    def mc_openResult_rect_process(self):
        """"""
        ############################################################################
        ############################################################################
        caseName=self.mcResultGroupName.split("_")[-1]
        self.mc_rect_caseName_lineEdit.setText(caseName)
        ####################
        dataName=f"{self.mcResultGroupName}/coreMaterial"
        concreteMaterial=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,dataName)
        matTags=["C10", "C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50", "C55", "C60",
         "C65", "C70", "C75", "C80", "User"]
        if concreteMaterial is not None:
            matName=concreteMaterial[0][0]
            matIndex=matTags.index(matName)
            self.rect_coreMaterial_ComboBox.setCurrentIndex(matIndex)
        else:
            dataName = f"{self.mcResultGroupName}/coreMaterial_user"
            concreteMaterial_user = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)
            matIndex = matTags.index("User")
            self.rect_coreMaterial_ComboBox.setCurrentIndex(matIndex)
            self.rect_userCoreMaterial_lineEdit.setText(concreteMaterial_user[0][0])
            self.rect_userCoreMaterial_lineEdit.setVisible(True)
        #####################
        dataName = f"{self.mcResultGroupName}/rebarMaterial"
        rebarMaterial = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)
        rebarMatTag=["HPB235", "HPB300", "HRB335", "HRBF335", "HRB400", "HRBF400","RRB400", "HRB500", "HRBF500", "User"]
        if rebarMaterial is not None:
            matName = rebarMaterial[0][0]
            matIndex = rebarMatTag.index(matName)
            self.rect_rebarMaterial_ComboBox.setCurrentIndex(matIndex)
        else:
            matIndex = rebarMatTag.index("User")
            self.rect_rebarMaterial_ComboBox.setCurrentIndex(matIndex)
            self.rect_userRebarMaterial_textEdit.clear()
            matNameList=self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath,self.mcResultGroupName,
                                                                            "rebarMaterial_user")
            for eachName in matNameList:
                dataName=f"{self.mcResultGroupName}/{eachName}"
                rebarMat=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
                self.rect_userRebarMaterial_textEdit.append(rebarMat)
        ###########################
        dataName = f"{self.mcResultGroupName}/rebarSpace"
        rebarSpace=self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_rebarSpace_lineEdit.setText(str(round(rebarSpace,6)))
        #########################
        dataName = f"{self.mcResultGroupName}/stirrupRatioY"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_stirrupRatioY_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/stirrupRatioZ"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_stirrupRatioZ_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/stirrupSpace"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_stirrupSpace_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/stirrupDiameter"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_stirrupDiameter_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/stirrupYieldStrength"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_stirrupYieldStrength_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/axialLoad"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.mc_rect_axialLoad_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/loadingDirection"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        if getResult=="localZ":
            self.rect_loadingZ_radioButton.setChecked(True)
        else:
            self.rect_loadingY_radioButton.setChecked(True)
        #########################
        dataName = f"{self.mcResultGroupName}/momentAtPperpendicularDirection"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.rect_momentLocal_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/Mu"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.rect_targetDuctilityFactor_lineEdit.setText(str(round(getResult, 6)))
        #########################
        dataName = f"{self.mcResultGroupName}/markerSize"
        getResult = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, dataName)[0][0]
        self.rect_markerSize_lineEdit.setText(str(round(getResult, 6)))
        ########################################################################################---MC plot
        #########################################################################################
        mcInstance = MC(self.mcResultGroupName, self.mc_newAnalysis_DBInstance,None, None, self.sectionDXFPath)

        mcInstance.MCCurve(self.mcCurve_figure, self.mcCurve_ax, self.mcCurve_figCanvas,
                           self.sectionDXFPath, self.mcResultGroupName, self)
        self.MCCurve_radioButton.setVisible(True)
        self.fiberRes_radioButton.setVisible(True)
        #######################################################---fibers stress strain display
        coreFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/coreFiberInfo")
        innerCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                       "fiberMesh/innerCoverFiberInfo")
        if innerCoverFiberList is None:
            innerCoverFiberList = []
        outCoverFiberList = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                                                     f"fiberMesh/outCoverFiberInfo")
        if outCoverFiberList is None:
            outCoverFiberList = []
        barsNameList = self.mc_newAnalysis_DBInstance.partialMatchDataSets(self.sectionDXFPath, "fiberMesh", "bars")
        if barsNameList is None:
            barsNameList = []
        barsFiberList = []
        for each in barsNameList:
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/{each}")
            barsFiberList.append(temp)
        # #################################
        self.xPlot = []
        [self.xPlot.append(each[1]) for each in coreFiberList]
        [self.xPlot.append(each[1]) for each in innerCoverFiberList]
        [self.xPlot.append(each[1]) for each in outCoverFiberList]
        [[self.xPlot.append(each[1]) for each in eachType] for eachType in barsFiberList]
        # ################
        self.yPlot = []
        [self.yPlot.append(each[2]) for each in coreFiberList]
        [self.yPlot.append(each[2]) for each in innerCoverFiberList]
        [self.yPlot.append(each[2]) for each in outCoverFiberList]
        [[self.yPlot.append(each[2]) for each in eachType] for eachType in barsFiberList]
        # # ##############################
        barColorList = ["k", "brown", "lightblue", "gold"]
        colorsList = []
        for each in coreFiberList:
            colorsList.append("b")
        for each in innerCoverFiberList:
            colorsList.append("g")
        for each in outCoverFiberList:
            colorsList.append("g")
        for i1 in range(len(barsFiberList)):
            color = barColorList[i1 % 4]
            for each in barsFiberList[i1]:
                colorsList.append(color)
        # #######################################
        self.indices = np.arange(len(self.xPlot))
        self.colors = np.array(colorsList)
        self.initial_colors = self.colors.copy()
        markerSize = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                    f"{self.mcResultGroupName}/markerSize")[0][0]
        self.sizes = np.full(len(self.xPlot), markerSize)
        # ##########################################
        interFigure = self.fiberInter_figure
        interAx = self.fiberInter_ax
        interCanvas = self.fiberInter_figCanvas
        #####################################################################
        sectionName = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                            f"{self.mcResultGroupName}/caseName")[0][0]
        interFigure.suptitle(sectionName + " discreted fiber points")
        self.stacked_widget.setCurrentIndex(2)
        interAx.clear()
        ############################################################
        sectionWidthHeightRatio = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath,
                                    f"fiberMesh/sectionWidthHeightRatio")[0][0]
        if self.fiberRespIndexValue == 0:
            self.fiberMesh_figureSize = interFigure.get_size_inches()
            self.fiberRespIndexValue += 1
        sizeValue = self.fiberMesh_figureSize
        originalSizeRatio = sizeValue[0] / float(sizeValue[1])

        if sectionWidthHeightRatio > originalSizeRatio:
            newWidth = sizeValue[0]
            newHeight = sizeValue[0] / float(sectionWidthHeightRatio)
        else:
            newHeight = sizeValue[1]
            newWidth = sizeValue[1] * sectionWidthHeightRatio
        if self.fiberRespIndexValue ==0:
            interFigure.set_figwidth(newWidth)
            interFigure.set_figheight(newHeight)
        #####################################################
        interAx.set_xlabel("Local y direction dimension(m)---y")
        interAx.set_ylabel("Local z direction dimension(m)---z")
        # ######################
        self.scatter = interAx.scatter(self.xPlot, self.yPlot, c=self.colors, picker=True, s=self.sizes)
        figureSize = min(interFigure.get_size_inches())
        interFigure.set_figwidth(figureSize)
        interFigure.set_figheight(figureSize)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        interCanvas.draw()
        ####################################################################################################
        self.fiberIndexDict = {}
        self.fiberIndexDict["coreFiber"] = [each[0] for each in coreFiberList]
        self.fiberIndexDict["innerCoverFiber"] = [each[0] for each in innerCoverFiberList]
        self.fiberIndexDict["outCoverFiber"] = [each[0] for each in outCoverFiberList]
        for i1 in range(len(barsFiberList)):
            temp = self.mc_newAnalysis_DBInstance.getResult(self.sectionDXFPath, f"fiberMesh/bars_{i1 + 1}")
            self.fiberIndexDict[f"bars_{i1 + 1}"] = [each[0] for each in temp]
        ###############################################
        #####################################################################################################
        self.last_clicked = None
        interCanvas.mpl_connect('pick_event', lambda event: self.on_pick(event, self.mc_newAnalysis_DBInstance,
                                    self.sectionDXFPath, self.mcResultGroupName))
        # #################################################################
        self.cyclicMaterialResponse(matType="coreMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        self.cyclicMaterialResponse(matType="coverMaterial", dbInstance=self.mc_newAnalysis_DBInstance,
                                    dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        for each in barsNameList:
            self.cyclicMaterialResponse(matType=each, dbInstance=self.mc_newAnalysis_DBInstance,
                                        dbPath=self.sectionDXFPath, groupName=self.mcResultGroupName)
        #############################################################

    def rightPanel_mcAnalysis_frame_ui(self):
        """"""
        self.rightPanel_mcAnalysis_formLayout = QFormLayout(self.rightPanel_mcAnalysis_initFrame)
        ##############
        ###################
        self.rightPanel_mc_newAnalysis_radioButton = QRadioButton("new analysis", self)
        self.rightPanel_mc_openDb_radioButton = QRadioButton("open database", self)
        self.rightPanel_mc_newAnalysis_radioButton.clicked.connect(self.rightPanel_mc_newAnalysis_radioButton_slot)
        self.rightPanel_mc_openDb_radioButton.clicked.connect(self.rightPanel_mc_openDb_radioButton_slot)
        self.rightPanel_mc_newAnalysis_radioButton.setChecked(False)
        self.rightPanel_mc_openDb_radioButton.setChecked(False)
        self.rightPanel_mcAnalysis_formLayout.addRow(self.rightPanel_mc_newAnalysis_radioButton,
                                                     self.rightPanel_mc_openDb_radioButton)
        ###########################################################################
        #######
        self.mc_sectionName_ComboBox = QComboBox()
        self.mc_sectionName_ComboBox.setVisible(False)
        self.mc_sectionName_ComboBox.currentTextChanged.connect(self.mc_sectionName_ComboBox_slot)
        self.rightPanel_mcAnalysis_formLayout.addRow(self.mc_sectionName_ComboBox)
        ############################################
        ############################################################################################
        self.rightPanel_mc_sectType_circle_radioButton = QRadioButton("circle", self)
        self.rightPanel_mc_sectType_rect_radioButton = QRadioButton("rectangle", self)
        self.rightPanel_mc_sectType_circle_radioButton.clicked.connect(self.rightPanel_mc_sectType_circle_radioButton_slot)
        self.rightPanel_mc_sectType_rect_radioButton.clicked.connect(self.rightPanel_mc_sectType_rect_radioButton_slot)
        self.rightPanel_mc_sectType_circle_radioButton.setChecked(False)
        self.rightPanel_mc_sectType_circle_radioButton.setVisible(False)
        self.rightPanel_mc_sectType_rect_radioButton.setChecked(False)
        self.rightPanel_mc_sectType_rect_radioButton.setVisible(False)
        ####
        self.mc_sectType_buttonGroup = QButtonGroup(self)
        self.mc_sectType_buttonGroup.addButton(self.rightPanel_mc_sectType_circle_radioButton)
        self.mc_sectType_buttonGroup.addButton(self.rightPanel_mc_sectType_rect_radioButton)
        self.rightPanel_mcAnalysis_formLayout.addRow(self.rightPanel_mc_sectType_circle_radioButton,
                                                     self.rightPanel_mc_sectType_rect_radioButton)
        #####################################################################
        self.rightPanel_mc_stacked_widget = QStackedWidget(self)
        self.rightPanel_mc_stacked_widget.setVisible(False)
        ####
        self.rightPanel_mc_circleSect_initFrame = QFrame()
        self.rightPanel_mc_rectSect_initFrame = QFrame()
        self.rightPanel_mc_stacked_widget.addWidget(self.rightPanel_mc_circleSect_initFrame)
        self.rightPanel_mc_stacked_widget.addWidget(self.rightPanel_mc_rectSect_initFrame)
        self.rightPanel_mcAnalysis_formLayout.addRow(self.rightPanel_mc_stacked_widget)
        #####################################################################
        self.rightPanel_mc_circleSect_frame_ui()
        self.rightPanel_mc_rectSect_frame_ui()



    def rightPanel_fiberMesh_frame_ui(self):
        """"""
        rightPanel_fiberMesh_formLayout = QFormLayout(self.rightPanel_fiberMesh_initFrame)
        #############---working dirctory
        workDir_button = QPushButton("Select working directory")
        rightPanel_fiberMesh_formLayout.addRow(workDir_button)
        workDir_button.clicked.connect(self.select_work_path_slot)
        ###################
        self.rightPanel_dxfSection_radioButton = QRadioButton("dxf section", self)
        self.rightPanel_dxfSection_radioButton.setVisible(False)
        self.rightPanel_openDb_radioButton = QRadioButton("open database", self)
        self.rightPanel_openDb_radioButton.setVisible(False)
        self.rightPanel_dxfSection_radioButton.clicked.connect(self.rightPanel_dxfSection_radioButton_slot)
        self.rightPanel_openDb_radioButton.clicked.connect(self.rightPanel_openDb_radioButton_slot)
        self.rightPanel_dxfSection_radioButton.setChecked(False)
        ####
        self.fiberMeshFrom_buttonGroup = QButtonGroup(self)
        self.fiberMeshFrom_buttonGroup.addButton(self.rightPanel_dxfSection_radioButton)
        self.fiberMeshFrom_buttonGroup.addButton(self.rightPanel_openDb_radioButton)
        rightPanel_fiberMesh_formLayout.addRow(self.rightPanel_dxfSection_radioButton,
                                               self.rightPanel_openDb_radioButton)
        ############################################################################################
        #############---divide number setting
        self.numSegs_frame = QFrame()
        self.numSegs_frame.setVisible(False)
        rightPanel_fiberMesh_formLayout.addRow(self.numSegs_frame)
        numSegs_formLayout = QFormLayout(self.numSegs_frame)
        ###################
        self.numArcSeg_label = QLabel("numArcSeg:")
        self.numArcSeg_lineEdit = QLineEdit("20", ToolTip="Input the number of segments for an arc!")
        ##
        self.numSplineSeg_label = QLabel("numSplineSeg:")
        self.numSplineSeg_lineEdit = QLineEdit("20", ToolTip="Input the number of segments for a spline!")
        ##
        self.numCircleSeg_label = QLabel("numCircleSeg:")
        self.numCircleSeg_lineEdit = QLineEdit("20", ToolTip="Input the number of segments for a circle!")
        ##
        self.numEllipseSeg_label = QLabel("numEllipseSeg:")
        self.numEllipseSeg_lineEdit = QLineEdit("20", ToolTip="Input the number of segments for an ellipse!")
        ####
        numSeg1_hBox = QHBoxLayout()
        numSeg1_hBox.addWidget(self.numArcSeg_label)
        numSeg1_hBox.addWidget(self.numArcSeg_lineEdit)
        numSegs_formLayout.addRow(numSeg1_hBox)
        ########
        numSeg2_hBox = QHBoxLayout()
        numSeg2_hBox.addWidget(self.numSplineSeg_label)
        numSeg2_hBox.addWidget(self.numSplineSeg_lineEdit)
        numSegs_formLayout.addRow(numSeg2_hBox)
        ####
        numSeg3_hBox = QHBoxLayout()
        numSeg3_hBox.addWidget(self.numCircleSeg_label)
        numSeg3_hBox.addWidget(self.numCircleSeg_lineEdit)
        numSegs_formLayout.addRow(numSeg3_hBox)
        ####
        numSeg4_hBox = QHBoxLayout()
        numSeg4_hBox.addWidget(self.numEllipseSeg_label)
        numSeg4_hBox.addWidget(self.numEllipseSeg_lineEdit)
        numSegs_formLayout.addRow(numSeg4_hBox)
        ##############################################################################################
        #############---fiber divide parameters setting
        self.fiberDivideParasSetting_frame = QFrame()
        self.fiberDivideParasSetting_frame.setVisible(False)
        rightPanel_fiberMesh_formLayout.addRow(self.fiberDivideParasSetting_frame)
        fiberDivideParas_formLayout = QFormLayout(self.fiberDivideParasSetting_frame)
        self.innerCoverThickness_label = QLabel("innerCoverThickness(m):")
        self.innerCoverThickness_lineEdit = QLineEdit("0.05", ToolTip="Input the thickness of inner cover part!")
        self.outCoverThickness_label = QLabel("outCoverThickness(m):")
        self.outCoverThickness_lineEdit = QLineEdit("0.05", ToolTip="Input the thickness of out cover part!")
        ##
        self.coreFiberSize_label = QLabel("coreFiberSize(m):")
        self.coreFiberSize_lineEdit = QLineEdit("0.2", ToolTip="Input the fiber size of core part!")
        ##
        self.innerCoverFiberSize_label = QLabel("innerCoverFiberSize(m):")
        self.innerCoverFiberSize_lineEdit = QLineEdit("0.03", ToolTip="Input the fiber size of inner cover part!")
        ##
        self.outCoverFiberSize_label = QLabel("outCoverFiberSize(m):")
        self.outCoverFiberSize_lineEdit = QLineEdit("0.03", ToolTip="Input the fiber size of out cover part!")
        ####
        ####
        self.coreFiberSize_label = QLabel("coreFiberSize(m):")
        self.coreFiberSize_lineEdit = QLineEdit("0.2", ToolTip="Input the fiber size of core part!")
        ######
        fiberSize1_hBox = QHBoxLayout()
        fiberSize1_hBox.addWidget(self.outCoverThickness_label)
        fiberSize1_hBox.addWidget(self.outCoverThickness_lineEdit)
        fiberDivideParas_formLayout.addRow(fiberSize1_hBox)
        ############
        fiberSize2_hBox = QHBoxLayout()
        fiberSize2_hBox.addWidget(self.outCoverFiberSize_label)
        fiberSize2_hBox.addWidget(self.outCoverFiberSize_lineEdit)
        fiberDivideParas_formLayout.addRow(fiberSize2_hBox)
        ####
        fiberSize3_hBox = QHBoxLayout()
        fiberSize3_hBox.addWidget(self.innerCoverThickness_label)
        fiberSize3_hBox.addWidget(self.innerCoverThickness_lineEdit)
        fiberDivideParas_formLayout.addRow(fiberSize3_hBox)
        ####
        fiberSize4_hBox = QHBoxLayout()
        fiberSize4_hBox.addWidget(self.innerCoverFiberSize_label)
        fiberSize4_hBox.addWidget(self.innerCoverFiberSize_lineEdit)
        fiberDivideParas_formLayout.addRow(fiberSize4_hBox)
        #####
        fiberSize5_hBox = QHBoxLayout()
        fiberSize5_hBox.addWidget(self.coreFiberSize_label)
        fiberSize5_hBox.addWidget(self.coreFiberSize_lineEdit)
        fiberDivideParas_formLayout.addRow(fiberSize5_hBox)
        #############################################################################
        #####
        self.fiberMesh_button = QPushButton("Mesh fiber!")
        self.fiberMesh_button.setVisible(False)
        # self.fiberMesh_button.setFixedSize(100, 30)
        self.fiberMesh_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.fiberMesh_button.clicked.connect(self.fiberMesh_button_slot)
        rightPanel_fiberMesh_formLayout.addRow(self.fiberMesh_button)
        #####
        self.outputMesh_button = QPushButton("output mesh!")
        self.outputMesh_button.setVisible(False)
        # self.outputMesh_button.setFixedSize(100, 30)
        self.outputMesh_button.setStyleSheet("QPushButton{background-color:#7FFFD4;}")
        self.outputMesh_button.clicked.connect(self.outputMesh_button_slot)
        rightPanel_fiberMesh_formLayout.addRow(self.outputMesh_button)
        ###############################################################################

    def fiberMesh_radioButton_ui(self):
        """---fiber mesh page ui laylout---"""
        ##############interact matplotlib
        self.fiberMesh_figure = plt.figure()
        self.fiberMesh_figCanvas = FigureCanvas(self.fiberMesh_figure) ###---put figure on the canvas
        self.fiberMesh_toolbar = NavigationToolbar(self.fiberMesh_figCanvas, self)
        self.fiberMesh_ax = self.fiberMesh_figure.add_subplot(111)
        ############
        v1Box = QVBoxLayout()
        v1Box.addWidget(self.fiberMesh_toolbar)
        v1Box.addWidget(self.fiberMesh_figCanvas)
        self.fiberMeshInitFrame.setLayout(v1Box)
        #######################################

    def fiberMesh_radioButton_slot(self):
        """---Fiber meshing laylout page---"""
        ##############---
        self.stacked_widget.setVisible(True)
        self.stacked_widget.setCurrentIndex(0)
        ##############

    def MCCurve_radioButton_ui(self):
        """"""
        ##############interact matplotlib
        self.mcCurve_figure = plt.figure()
        self.mcCurve_figCanvas = FigureCanvas(self.mcCurve_figure)  ###---put figure on the canvas
        self.mcCurve_toolbar = NavigationToolbar(self.mcCurve_figCanvas, self)
        self.mcCurve_ax = self.mcCurve_figure.add_subplot(111)
        ############
        v1Box = QVBoxLayout()
        v1Box.addWidget(self.mcCurve_toolbar)
        v1Box.addWidget(self.mcCurve_figCanvas)
        self.MCAnalysisInitFrame.setLayout(v1Box)
        #######################################

    def MCCurve_radioButton_slot(self):
        """---Fiber meshing laylout page---"""
        ##############---
        self.stacked_widget.setVisible(True)
        self.stacked_widget.setCurrentIndex(1)
        ##############

    def fiberRes_radioButton_ui(self):
        """"""
        ##############interact matplotlib
        self.fiberInter_figure = plt.figure()
        self.fiberInter_figCanvas = FigureCanvas(self.fiberInter_figure)  ###---put figure on the canvas
        self.fiberInter_toolbar = NavigationToolbar(self.fiberInter_figCanvas, self)
        self.fiberInter_ax = self.fiberInter_figure.add_subplot(111)
        ############
        v1Box = QVBoxLayout()
        v1Box.addWidget(self.fiberInter_toolbar)
        v1Box.addWidget(self.fiberInter_figCanvas)
        ################################
        ##############interact matplotlib
        self.fiberRes_figure = plt.figure()
        self.fiberRes_figCanvas = FigureCanvas(self.fiberRes_figure)  ###---put figure on the canvas
        self.fiberRes_toolbar = NavigationToolbar(self.fiberRes_figCanvas, self)
        self.fiberRes_ax = self.fiberRes_figure.add_subplot(111)
        ############
        v2Box = QVBoxLayout()
        v2Box.addWidget(self.fiberRes_toolbar)
        v2Box.addWidget(self.fiberRes_figCanvas)
        ###########
        self.fiberInterFrame = QFrame()
        self.fiberResFrame = QFrame()
        self.fiberInterFrame.setLayout(v1Box)
        self.fiberResFrame.setLayout(v2Box)
        self.fiberRes_H1Box = QHBoxLayout()
        self.fiberRes_H1Box.addWidget(self.fiberInterFrame)
        self.fiberRes_H1Box.addWidget(self.fiberResFrame)
        ###########
        self.fiberRes_H1Box.setStretchFactor(self.fiberInterFrame,4)
        self.fiberRes_H1Box.setStretchFactor(self.fiberResFrame,3)
        ################################
        self.fiberResInitFrame.setLayout(self.fiberRes_H1Box)
        #######################################

    def fiberRes_radioButton_slot(self):
        """---Fiber meshing laylout page---"""
        ##############---
        self.stacked_widget.setVisible(True)
        self.stacked_widget.setCurrentIndex(2)
        ##############

    def _intFloatInputValidate(self,textValue,labelName,nameErrorText):
        """"""
        try:
            numArcSeg_text = eval(textValue)
            if (isinstance(numArcSeg_text, (int, float))):
                self.displayLabel.setText("")
                self.displayLabel.setStyleSheet("color: black;")
                numArcSeg = numArcSeg_text
                return numArcSeg
        except :
            self.displayLabel.setText(f"{labelName}: {nameErrorText}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError()

    def _intFloatPositiveInputValidate(self,textValue,labelName,nameErrorText):
        """"""
        try:
            numArcSeg_text=eval(textValue)
            if (isinstance(numArcSeg_text, (int,float)) and numArcSeg_text>0):
                self.displayLabel.setText("")
                self.displayLabel.setStyleSheet("color: black;")
                numArcSeg=numArcSeg_text
                return numArcSeg
            else:
                try:
                    raise NameError(f"{labelName}: {nameErrorText}")
                except Exception as err:
                    self.displayLabel.setText(f"{labelName}: {nameErrorText}")
                    self.displayLabel.setStyleSheet("color: red;")
                    raise err
        except NameError as e:
            self.displayLabel.setText(f"{labelName}: {nameErrorText}")
            self.displayLabel.setStyleSheet("color: red;")
            raise e

    def _intFloatPositiveAndNoneInputValidate(self, textValue, labelName, nameErrorText):
        """"""
        try:
            numArcSeg_text = eval(textValue)
            if (isinstance(numArcSeg_text, (int, float)) and numArcSeg_text > 0)or (numArcSeg_text is None):
                self.displayLabel.setText("")
                self.displayLabel.setStyleSheet("color: black;")
                numArcSeg = numArcSeg_text
                return numArcSeg
        except NameError as e:
            self.displayLabel.setText(f"{labelName}: {nameErrorText}")
            self.displayLabel.setStyleSheet("color: red;")
            raise e

    def fiberMeshPlot(self,coreFiberInfo, innerFiberInfo, outFiberInfo,barFiberInfo, corePoints, innerPoints,
                      outPoints,coreTriangles, outTriangles,innerTriangles,sectionWidthHeightRatio):
        """"""
        if self.indexValue==0:
            self.fiberMesh_figureSize=self.fiberMesh_figure.get_size_inches()
            self.indexValue+=1
        sizeValue=self.fiberMesh_figureSize
        originalSizeRatio=sizeValue[0]/float(sizeValue[1])

        if sectionWidthHeightRatio>originalSizeRatio:
            newWidth=sizeValue[0]
            newHeight=sizeValue[0]/float(sectionWidthHeightRatio)
        else:
            newHeight=sizeValue[1]
            newWidth=sizeValue[1]*sectionWidthHeightRatio
        if self.indexValue == 0:
            self.fiberMesh_figure.set_figwidth(newWidth)
            self.fiberMesh_figure.set_figheight(newHeight)

        self.fiberMesh_ax.clear()
        self.fiberMesh_ax.set_aspect('equal')
        self.fiberMesh_ax.triplot(corePoints[:, 0], corePoints[:, 1], coreTriangles, color='b', linewidth=1)
        [self.fiberMesh_ax.triplot(innerPoints[i1][:, 0], innerPoints[i1][:, 1], innerTriangles[i1], color='r', linewidth=1)
         for i1 in range(len(innerPoints))]
        [self.fiberMesh_ax.triplot(outPoints[i2][:, 0], outPoints[i2][:, 1], outTriangles[i2], color='r', linewidth=1)
         for i2 in range(len(outPoints))]
        ###########################
        self.fiberMesh_figCanvas.draw()
        pt0 = self.fiberMesh_ax.transData.transform((0, 0))
        pt1 = self.fiberMesh_ax.transData.transform((1, 0))  # X direction
        dx_pixels = pt1[0] - pt0[0]
        inches_per_data = dx_pixels / self.fiberMesh_figure.dpi  # translate to inch
        points_per_data = inches_per_data * 72
        [[[radius:=(eachBar[2]/3.14159267)**0.5,area:= (2 * radius * points_per_data) ** 2,
           self.fiberMesh_ax.scatter(eachBar[0],eachBar[1],marker='o',s=area,color='k')]
          for eachBar in eachType] for eachType in barFiberInfo]
        self.fiberMesh_figCanvas.draw()
        totalCoreFiber=len(coreFiberInfo)
        totalOutFiber=0
        for eachOutFiber in outFiberInfo:
            totalOutFiber += len(eachOutFiber)
        totalInnerFiber=0
        if innerFiberInfo is not None:
            for eachInnerFiber in innerFiberInfo:
                totalInnerFiber += len(eachInnerFiber)
        totalBarFiber=0
        for eachBar in barFiberInfo:
            totalBarFiber += len(eachBar)
        self.displayLabel.setText(f"{totalCoreFiber} core fibers, {totalOutFiber} outCover fibers, "
                                  f"{totalInnerFiber} innerCover fibers, {totalBarFiber} bar fibers!")

    def rightPanel_dxfSection_radioButton_slot(self):
        """"""
        curDir = QDir.currentPath()  # get current working directory
        aFile, filt = QFileDialog.getOpenFileName(self, "Open section DXF file", curDir, "(*.dxf)")  # file dialog
        self.sectionDXFPath = aFile
        if self.sectionDXFPath:
            self.sectionDXFName = os.path.splitext(os.path.basename(self.sectionDXFPath))[0]
            self.displayLabel.setText("Successfully open dxf file: " + self.sectionDXFPath)
            ####################################################
            self.numSegs_frame.setVisible(True)
            self.fiberDivideParasSetting_frame.setVisible(True)
            self.fiberMesh_button.setVisible(True)

    def _databaseFiberMeshPlot(self,dbPath):
        """"""
        #######################
        numArcSeg=MCAnalysisResultDB.getResult(dbPath,"fiberMesh/numArcSeg")
        if numArcSeg is not None:
            self.numArcSeg_lineEdit.setText(str(numArcSeg[0][0]))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"numArcSeg invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        numSplineSeg = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/numSplineSeg")
        if numSplineSeg is not None:
            self.numSplineSeg_lineEdit.setText(str(numSplineSeg[0][0]))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"numSplineSeg invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        numCircleSeg = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/numCircleSeg")
        if numCircleSeg is not None:
            self.numCircleSeg_lineEdit.setText(str(numCircleSeg[0][0]))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"numCircleSeg invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        numEllipseSeg = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/numEllipseSeg")
        if numEllipseSeg is not None:
            self.numEllipseSeg_lineEdit.setText(str(numEllipseSeg[0][0]))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"numEllipseSeg invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        outCoverThickness = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/outCoverThickness")
        if outCoverThickness is not None:
            self.outCoverThickness_lineEdit.setText(str(round(outCoverThickness[0][0],6)))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"outCoverThickness invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        outCoverFiberSize = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/outCoverFiberSize")
        if outCoverFiberSize is not None:
            self.outCoverFiberSize_lineEdit.setText(str(round(outCoverFiberSize[0][0],6)))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"outCoverFiberSize invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        innerCoverThickness = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/innerCoverThickness")
        if innerCoverThickness is not None:
            self.innerCoverThickness_lineEdit.setText(str(round(innerCoverThickness[0][0],6)))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"innerCoverThickness invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        innerCoverFiberSize = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/innerCoverFiberSize")
        if innerCoverFiberSize is not None:
            self.innerCoverFiberSize_lineEdit.setText(str(round(innerCoverFiberSize[0][0],6)))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"innerCoverFiberSize invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        coreFiberSize = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/coreFiberSize")
        if coreFiberSize is not None:
            self.coreFiberSize_lineEdit.setText(str(round(coreFiberSize[0][0],6)))
            self.displayLabel.setStyleSheet("color: black;")
        else:
            self.displayLabel.setText(f"coreFiberSize invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        coreFiberInfo = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/coreFiberInfo")
        self.displayLabel.setStyleSheet("color: black;")
        if coreFiberInfo is None:
            self.displayLabel.setText(f"coreFiberInfo invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        innerFiberInfo = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/innerCoverFiberInfo")
        self.displayLabel.setStyleSheet("color: black;")
        # if innerFiberInfo is None:
        #     self.displayLabel.setText(f"innerFiberInfo invalid in {dbPath}")
        #     self.displayLabel.setStyleSheet("color: red;")
        #     raise ValueError("")
        ################################################################################
        outFiberInfo = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/outCoverFiberInfo")
        self.displayLabel.setStyleSheet("color: black;")
        if outFiberInfo is None:
            self.displayLabel.setText(f"outFiberInfo invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        barFiberName= MCAnalysisResultDB.getResult(dbPath, "fiberMesh/barFiberName")
        self.displayLabel.setStyleSheet("color: black;")
        if barFiberName is None:
            self.displayLabel.setText(f"barFiberName invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        barFibersList=[]
        for eachName in barFiberName:
            barFiber=MCAnalysisResultDB.getResult(dbPath, f"fiberMesh/{eachName[0]}")
            self.displayLabel.setStyleSheet("color: black;")
            if barFiber is None:
                self.displayLabel.setText(f"{eachName[0]} invalid in {dbPath}")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError("")
            barFibersList.append(barFiber)
        ################################################################################
        corePoints = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/corePoints")
        self.displayLabel.setStyleSheet("color: black;")
        if corePoints is None:
            self.displayLabel.setText(f"corePoints invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        innerPointsName = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/innerPointsName")
        self.displayLabel.setStyleSheet("color: black;")
        # if innerPointsName is None:
        #     self.displayLabel.setText(f"innerPointsName invalid in {dbPath}")
        #     self.displayLabel.setStyleSheet("color: red;")
        #     raise ValueError("")
        ################################################################################
        innerPoints = []
        if innerPointsName is not None:
            for eachName in innerPointsName:
                innerPs = MCAnalysisResultDB.getResult(dbPath, f"fiberMesh/{eachName[0]}")
                self.displayLabel.setStyleSheet("color: black;")
                if innerPs is None:
                    self.displayLabel.setText(f"{eachName[0]} invalid in {dbPath}")
                    self.displayLabel.setStyleSheet("color: red;")
                    raise ValueError("")
                innerPoints.append(np.array(innerPs))
        ################################################################################
        outPoints = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/outPoints")
        self.displayLabel.setStyleSheet("color: black;")
        if outPoints is  None:
            self.displayLabel.setText(f"outPoints invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        coreTriangles = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/coreTriangles")
        self.displayLabel.setStyleSheet("color: black;")
        if coreTriangles is None:
            self.displayLabel.setText(f"coreTriangles invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        outTrianglesName = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/outTrianglesName")
        self.displayLabel.setStyleSheet("color: black;")
        if outTrianglesName is None:
            self.displayLabel.setText(f"outTriangles invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        ################################################################################
        outTriangles = []
        for eachName in outTrianglesName:
            outTriang = MCAnalysisResultDB.getResult(dbPath, f"fiberMesh/{eachName[0]}")
            self.displayLabel.setStyleSheet("color: black;")
            if outTriang is None:
                self.displayLabel.setText(f"{eachName[0]} invalid in {dbPath}")
                self.displayLabel.setStyleSheet("color: red;")
                raise ValueError("")
            outTriangles.append(outTriang)
        ################################################################################
        innerTrianglesName = MCAnalysisResultDB.getResult(dbPath, "fiberMesh/innerTrianglesName")
        self.displayLabel.setStyleSheet("color: black;")
        # if outTrianglesName is None:
        #     self.displayLabel.setText(f"outTriangles invalid in {dbPath}")
        #     self.displayLabel.setStyleSheet("color: red;")
        #     raise ValueError("")
        ################################################################################
        innerTriangles = []
        if innerTrianglesName is not None:
            for eachName in innerTrianglesName:
                innerTriang = MCAnalysisResultDB.getResult(dbPath, f"fiberMesh/{eachName[0]}")
                self.displayLabel.setStyleSheet("color: black;")
                if innerTriang is None:
                    self.displayLabel.setText(f"{eachName[0]} invalid in {dbPath}")
                    self.displayLabel.setStyleSheet("color: red;")
                    raise ValueError("")
                innerTriangles.append(innerTriang)
        ################################################################################
        sectionWidthHeightRatio= MCAnalysisResultDB.getResult(dbPath, "fiberMesh/sectionWidthHeightRatio")
        self.displayLabel.setStyleSheet("color: black;")
        if sectionWidthHeightRatio is None:
            self.displayLabel.setText(f"sectionWidthHeightRatio invalid in {dbPath}")
            self.displayLabel.setStyleSheet("color: red;")
            raise ValueError("")
        #######################
        self.leftFrame_visibleSwith.setVisible(True)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        self.MCCurve_radioButton.setVisible(False)
        self.fiberRes_radioButton.setVisible(False)

        barFiber3List=[]
        [[tempValueList:=[],[tempValueList.append([eachFiber[1],eachFiber[2],eachFiber[3]]) for eachFiber in eachType],
          barFiber3List.append(tempValueList)] for eachType in barFibersList]
        self.fiberMeshPlot(coreFiberInfo, innerFiberInfo, outFiberInfo, barFiber3List, np.array(corePoints), innerPoints,
                           [np.array(outPoints)], coreTriangles, outTriangles, innerTriangles, sectionWidthHeightRatio[0][0])
        ##########################################################################################################

    def rightPanel_openDb_radioButton_slot(self):
        """"""
        curDir = QDir.currentPath()  # get current working directory
        aFile, filt = QFileDialog.getOpenFileName(self, "Open section database", curDir, "(*.h5)")  # file dialog
        sectionDbPath = aFile
        self.sectionDXFPath=aFile
        if sectionDbPath:
            self.sectionDXFName = os.path.splitext(os.path.basename(sectionDbPath))[0]
            self.displayLabel.setText("Successfully open database file: " + sectionDbPath)
            ###########################################################
            self.numSegs_frame.setVisible(True)
            self.fiberDivideParasSetting_frame.setVisible(True)
            self.fiberMesh_button.setVisible(False)
            self.outputMesh_button.setVisible(True)
            self._databaseFiberMeshPlot(sectionDbPath)
            #########################################################

    def rightPanel_fiberMesh_radioButton_slot(self):
        """"""
        self.rightPanel_stacked_widget.setVisible(True)
        self.rightPanel_stacked_widget.setCurrentIndex(0)


    def rightPanel_mcAnalysis_radioButton_slot(self):
        """"""
        self.rightPanel_stacked_widget.setVisible(True)
        self.rightPanel_stacked_widget.setCurrentIndex(1)
        ###############################################

    def fiberMesh_button_slot(self):
        """"""
        #####################
        workingDirectory = self.currentWorkPath
        self.MCAnalysisResultDBInstance = MCAnalysisResultDB(workingDirectory, self.sectionDXFName)
        self.MCAnalysisResultDBInstance.initDB()
        ################
        textValue=self.numArcSeg_lineEdit.text()
        labelName="numArcSeg"
        nameErrorText="'not a valid input value,input a positive number!"
        numArcSeg=self._intFloatPositiveInputValidate(textValue,labelName,nameErrorText)
        ###
        saveValueList =[[numArcSeg]]
        saveName = f"fiberMesh/numArcSeg"
        headNameList = ['numArcSeg']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.numSplineSeg_lineEdit.text()
        labelName = "numSplineSeg"
        nameErrorText = "'not a valid input value,input a positive number!"
        numSplineSeg = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[numSplineSeg]]
        saveName = f"fiberMesh/numSplineSeg"
        headNameList = ['numSplineSeg']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.numCircleSeg_lineEdit.text()
        labelName = "numCircleSeg"
        nameErrorText = "'not a valid input value,input a positive number!"
        numCircleSeg= self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[numCircleSeg]]
        saveName = f"fiberMesh/numCircleSeg"
        headNameList = ['numCircleSeg']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.numEllipseSeg_lineEdit.text()
        labelName = "numEllipseSeg"
        nameErrorText = "'not a valid input value,input a positive number!"
        numEllipseSeg = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[numEllipseSeg]]
        saveName = f"fiberMesh/numEllipseSeg"
        headNameList = ['numEllipseSeg']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############################################################################
        textValue = self.outCoverThickness_lineEdit.text()
        labelName = "outCoverThickness"
        nameErrorText = "'not a valid input value,input a positive number!"
        outCoverThickness = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[outCoverThickness]]
        saveName = f"fiberMesh/outCoverThickness"
        headNameList = ['outCoverThickness']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.outCoverFiberSize_lineEdit.text()
        labelName = "outCoverFiberSize"
        nameErrorText = "'not a valid input value,input a positive number!"
        outCoverFiberSize = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[outCoverFiberSize]]
        saveName = f"fiberMesh/outCoverFiberSize"
        headNameList = ['outCoverFiberSize']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.innerCoverThickness_lineEdit.text()
        labelName = "innerCoverThickness"
        nameErrorText = "'not a valid input value,input a positive number!"
        innerCoverThickness = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[innerCoverThickness]]
        saveName = f"fiberMesh/innerCoverThickness"
        headNameList = ['innerCoverThickness']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.innerCoverFiberSize_lineEdit.text()
        labelName = "innerCoverFiberSize"
        nameErrorText = "'not a valid input value,input a positive number!"
        innerCoverFiberSize = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[innerCoverFiberSize]]
        saveName = f"fiberMesh/innerCoverFiberSize"
        headNameList = ['innerCoverFiberSize']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        textValue = self.coreFiberSize_lineEdit.text()
        labelName = "coreFiberSize"
        nameErrorText = "'not a valid input value,input a positive number!"
        coreFiberSize = self._intFloatPositiveInputValidate(textValue, labelName, nameErrorText)
        ###
        saveValueList = [[coreFiberSize]]
        saveName = f"fiberMesh/coreFiberSize"
        headNameList = ['coreFiberSize']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###############
        fiberMeshInstance=DxfFileSectionFiberMesh(filename=self.sectionDXFPath,numArcSeg=numArcSeg,
        numSplineSeg=numSplineSeg,numCircleSeg=numCircleSeg,numEllipseSeg=numEllipseSeg,outCoverThickness=outCoverThickness,
        outCoverFiberSize=outCoverFiberSize,innerCoverThickness=innerCoverThickness,innerCoverFiberSize=innerCoverFiberSize,
                                                  coreFiberSize=coreFiberSize,uiInstance=self)
        self.leftFrame_visibleSwith.setVisible(True)
        self.stacked_widget.setCurrentIndex(0)
        self.fiberMesh_radioButton.setChecked(True)
        self.MCCurve_radioButton.setVisible(False)
        self.fiberRes_radioButton.setVisible(False)
        (coreFiberInfo, innerFiberInfo, outFiberInfo,barFiberInfo, corePoints, innerPoints, outPoints,coreTriangles, outTriangles,
         innerTriangles,sectionWidthHeightRatio,rebarNameList)=fiberMeshInstance.cadModelProcess()
        self.fiberMeshPlot(coreFiberInfo, innerFiberInfo, outFiberInfo,barFiberInfo, corePoints, innerPoints, outPoints,
                           coreTriangles, outTriangles,innerTriangles,sectionWidthHeightRatio)
        ########################################################################################
        ########################################################################################

        #######################
        saveValueList = [[sectionWidthHeightRatio]]  ###---[[],[]]
        saveName = "fiberMesh/sectionWidthHeightRatio"
        headNameList = ['sectionWidthHeightRatio']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        #######################
        saveValueList = coreFiberInfo  ###---[[],[]]
        saveName = "fiberMesh/coreFiberInfo"
        headNameList = ['tagNumber','xCoord(m)', 'yCoord(m)', 'area(m2)']
        operationIndexStr = 'replace'
        ###########
        saveValueList =[[i1+1,saveValueList[i1][0],saveValueList[i1][1],saveValueList[i1][2]]
                        for i1 in range(len(saveValueList))]
        ###########
        self.MCAnalysisResultDBInstance.saveResult(saveName,saveValueList, headNameList, operationIndexStr)
        ##########################
        innerSaveList=[]
        for each in innerFiberInfo:
            innerSaveList+=each
        if innerSaveList:
            saveValueList = innerSaveList  ###---[[],[]]
            saveValueList=[[i1+1+len(coreFiberInfo),saveValueList[i1][0],saveValueList[i1][1],saveValueList[i1][2]]
                           for i1 in range(len(saveValueList))]
            saveName = "fiberMesh/innerCoverFiberInfo"
            headNameList = ['tagNumber','xCoord(m)', 'yCoord(m)', 'area(m2)']
            operationIndexStr = 'replace'
            self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ##########################
        outSaveList = []
        for each in outFiberInfo:
            outSaveList += each
        saveValueList = outSaveList  ###---[[],[]]
        saveValueList=[[i1+1+len(coreFiberInfo)+len(innerSaveList),saveValueList[i1][0],saveValueList[i1][1],
                        saveValueList[i1][2]] for i1 in range(len(saveValueList))]
        saveName = "fiberMesh/outCoverFiberInfo"
        headNameList = ['tagNumber','xCoord(m)', 'yCoord(m)', 'area(m2)']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        #################################
        if len(barFiberInfo)>0:
            barFiberInfoState=barFiberInfo[0]
        else:
            barFiberInfoState=barFiberInfo
        barNumTemp=0
        tagNumberList=[0]
        if barFiberInfoState:
            for i1 in range(len(rebarNameList)):
                indexValue=rebarNameList.index(f"bars_{i1+1}")
                saveValueList =barFiberInfo[indexValue]
                barNumTemp+=len(barFiberInfo[indexValue])
                tagNumberList.append(barNumTemp)
                saveValueListList=[[ii+1+len(coreFiberInfo)+len(innerSaveList)+len(outSaveList)+tagNumberList[i1],
                barFiberInfo[indexValue][ii][0],barFiberInfo[indexValue][ii][1],barFiberInfo[indexValue][ii][2]]
                                   for ii in range(len(barFiberInfo[indexValue]))]
                saveName=f"fiberMesh/{rebarNameList[indexValue]}"
                headNameList = ['tagNumber','xCoord(m)', 'yCoord(m)', 'area(m2)']
                operationIndexStr = 'replace'
                self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueListList, headNameList, operationIndexStr)
        #################################################
        saveRebarNameList=[]
        for each in rebarNameList:
            saveRebarNameList.append([each])
        saveValueList =saveRebarNameList
        saveName = f"fiberMesh/barFiberName"
        headNameList = ['barName']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ###################################
        saveValueList = corePoints
        saveName = f"fiberMesh/corePoints"
        headNameList = ['xCoord(m)', 'yCoord(m)', 'zCoord(m)']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ####################################
        innerPointsNameList=[]
        [innerPointsNameList.append(f"innerPoints_{i1+1}") for i1 in range(len(innerPoints))]
        [[saveValueList:= innerPoints[i2],saveName:= f"fiberMesh/{innerPointsNameList[i2]}",
          headNameList:= ['xCoord(m)', 'yCoord(m)', 'zCoord(m)'],operationIndexStr:= 'replace',
          self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)]
         for i2 in range(len(innerPoints))]
        #####################################
        saveInnerPointsNameList = []
        [saveInnerPointsNameList.append([each]) for each in innerPointsNameList]
        if saveInnerPointsNameList:
            saveValueList =saveInnerPointsNameList
            saveName = f"fiberMesh/innerPointsName"
            headNameList = ['innerPointsName']
            operationIndexStr = 'replace'
            self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        #######################################
        saveValueList = outPoints[0]
        saveName = f"fiberMesh/outPoints"
        headNameList = ['xCoord(m)', 'yCoord(m)', 'zCoord(m)']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        #####################################
        saveValueList = coreTriangles
        saveName = f"fiberMesh/coreTriangles"
        headNameList = ['I','J','K']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ######################################
        innerTrianglesNameList=[]
        [[innerTrianglesNameList.append(f"innerTriangles_{i1+1}"),saveValueList:= innerTriangles[i1],
        saveName:= f"fiberMesh/innerTriangles_{i1+1}",headNameList:= ['I', 'J', 'K'],operationIndexStr:= 'replace',
          self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)]
         for i1 in range(len(innerTriangles))]
        ################
        innerTrianglesName=[]
        [innerTrianglesName.append([each]) for each in innerTrianglesNameList]
        if innerTrianglesName:
            saveValueList =innerTrianglesName
            saveName = f"fiberMesh/innerTrianglesName"
            headNameList = ['innerTrianglesName']
            operationIndexStr = 'replace'
            self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        #######################################
        outTrianglesNameList = []
        [[outTrianglesNameList.append(f"outTriangles_{i1 + 1}"),saveValueList:= outTriangles[i1],
        saveName:= f"fiberMesh/outTriangles_{i1 + 1}",headNameList:= ['I', 'J', 'K'],operationIndexStr:= 'replace',
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)]
         for i1 in range(len(outTriangles))]
        ################
        outTrianglesName = []
        for each in outTrianglesNameList:
            outTrianglesName.append([each])
        saveValueList = outTrianglesName
        saveName = f"fiberMesh/outTrianglesName"
        headNameList = ['outTrianglesName']
        operationIndexStr = 'replace'
        self.MCAnalysisResultDBInstance.saveResult(saveName, saveValueList, headNameList, operationIndexStr)
        ##########################################
        self.outputMesh_button.setVisible(True)
        ################################################

    def outputMesh_button_slot(self):
        """"""
        self._rightPanel_outputMesh_process()

    def _rightPanel_outputMesh_process(self):
        savePath=self.currentWorkPath+f"/MCAnalysisResult/{self.sectionDXFName}-fiberInformation"
        if os.path.exists(savePath):
            shutil.rmtree(savePath)
        os.makedirs(savePath)
        ######################################
        dataPath=self.currentWorkPath+f"/MCAnalysisResult/{self.sectionDXFName}.h5"
        dataName=f"fiberMesh/coreFiberInfo"
        resultList=self.MCAnalysisResultDBInstance.getResult(dataPath,dataName)
        if resultList is not None:
            resultList=[[each[0],round(each[1],8),round(each[2],8),round(each[3],8)] for each in resultList]
            headName=["fiberNumber","yCoord(m)","zCoord(m)","area(m2)"]
            saveFiberPath=savePath+f"/coreFiberInfo.txt"
            with open(saveFiberPath,"w") as file:
                file.write("\t".join(headName)+"\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str,eachRow))+"\n")
        ############################################
        dataPath = self.currentWorkPath + f"/MCAnalysisResult/{self.sectionDXFName}.h5"
        dataName = f"fiberMesh/innerCoverFiberInfo"
        resultList = self.MCAnalysisResultDBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in resultList]
            headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
            saveFiberPath = savePath + f"/innerCoverFiberInfo.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        ###############################################
        dataPath = self.currentWorkPath + f"/MCAnalysisResult/{self.sectionDXFName}.h5"
        dataName = f"fiberMesh/outCoverFiberInfo"
        resultList = self.MCAnalysisResultDBInstance.getResult(dataPath, dataName)
        if resultList is not None:
            resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in resultList]
            headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
            saveFiberPath = savePath + f"/outCoverFiberInfo.txt"
            with open(saveFiberPath, "w") as file:
                file.write("\t".join(headName) + "\n")
                for eachRow in resultList:
                    file.write("\t".join(map(str, eachRow)) + "\n")
        #################################################
        dataPath = self.currentWorkPath + f"/MCAnalysisResult/{self.sectionDXFName}.h5"
        dataName = f"fiberMesh/barFiberName"
        barsName=self.MCAnalysisResultDBInstance.getResult(dataPath, dataName)
        if barsName is not None:
            for each in barsName:
                dataName = f"fiberMesh/{each[0]}"
                resultList = self.MCAnalysisResultDBInstance.getResult(dataPath, dataName)
                if resultList is not None:
                    resultList = [[each[0], round(each[1], 8), round(each[2], 8), round(each[3], 8)] for each in
                                  resultList]
                    headName = ["fiberNumber", "yCoord(m)", "zCoord(m)", "area(m2)"]
                    saveFiberPath = savePath + f"/{each[0]}_FiberInfo.txt"
                    with open(saveFiberPath, "w") as file:
                        file.write("\t".join(headName) + "\n")
                        for eachRow in resultList:
                            file.write("\t".join(map(str, eachRow)) + "\n")
        #################################################


    def select_work_path_slot(self):
        """---slot for selecting working directory---"""
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        work_path = QFileDialog.getExistingDirectory(self, "Select working directory:", options=options)
        if work_path:
            self.currentWorkPath = work_path
            self.rightPanel_dxfSection_radioButton.setVisible(True)
            self.rightPanel_openDb_radioButton.setVisible(True)
            self.displayLabel.setText("Dxf file: Plot lines with layer named 'lines',rebars with layers named 'bars_1',"
                                      "'bars_2',...")
########################################################################################################################
########################################################################################################################
class DxfFileSectionFiberMesh():
    def __init__(self, filename=None, numArcSeg=20, numSplineSeg=20,numCircleSeg=20,numEllipseSeg=20,outCoverThickness=None,
                 outCoverFiberSize=None,innerCoverThickness=None,innerCoverFiberSize=None,coreFiberSize=0.2,uiInstance=None):
        self.filename = filename
        self.numArcSeg = numArcSeg
        self.numSplineSeg = numSplineSeg
        self.numCircleSeg = numCircleSeg
        self.numEllipseSeg = numEllipseSeg
        self.outCoverThickness = outCoverThickness
        self.outCoverFiberSize = outCoverFiberSize
        self.innerCoverThickness = innerCoverThickness
        self.innerCoverFiberSize = innerCoverFiberSize
        self.coreFiberSize = coreFiberSize
        self.uiInstance = uiInstance
        ##############
        self.doc=None
        self.msp=None

    def layerEntityProcess_lines(self,layerName):
        """"""
        points = []
        eachLineIJCoord = []
        #####################################
        # process spline object
        try:
            splineEntity = self.msp.query(f"""SPLINE[layer=="{layerName}"]""")
            [[pointsList:= [],pointVector:= [eachValue for eachValue in each.flattening(1e8, self.numSplineSeg)],
            [[pointsList.append([round(eachPoints[0], 6), round(eachPoints[1], 6)]),
              points.append([round(eachPoints[0], 6), round(eachPoints[1], 6)])] for eachPoints in pointVector],
              [[startP:= [round(pointsList[i2][0], 6), round(pointsList[i2][1], 6)],
                endP:= [round(pointsList[i2 + 1][0], 6), round(pointsList[i2 + 1][1], 6)],
                eachLineIJCoord.append([startP, endP])] for i2 in range(len(pointsList) - 1)]] for each in splineEntity]
        except:
            pass
        #####################################
        # process ellipse object
        try:
            ellipseEntity = self.msp.query(f"""ELLIPSE[layer=="{layerName}"]""")
            [[pointsList:= [],pointVector:= [eachValue for eachValue in each.flattening(1e8, self.numEllipseSeg)],
              [[pointsList.append([round(eachPoints[0], 6), round(eachPoints[1], 6)]),
                points.append([round(eachPoints[0], 6), round(eachPoints[1], 6)])] for eachPoints in pointVector],
              [[startP:= [round(pointsList[i2][0], 6), round(pointsList[i2][1], 6)],
                endP:= [round(pointsList[i2 + 1][0], 6), round(pointsList[i2 + 1][1], 6)],
                eachLineIJCoord.append([startP, endP])] for i2 in range(len(pointsList))]] for each in ellipseEntity]
        except:
            pass
        #####################################
        # process circle object
        try:
            circleEntity = self.msp.query(f"""CIRCLE[layer=="{layerName}"]""")

            [[centerPoint:= each.dxf.center,radius:= each.dxf.radius,deltaAngle:= 360.0 / float(self.numCircleSeg),
              circlePointList:= [],[[sinValue:= math.sin(i1 * deltaAngle * 3.1415926 / 180.0),
            cosValue:= math.cos(i1 * deltaAngle * 3.1415926 / 180.0),pointY:= centerPoint[0] + radius * cosValue,
            pointZ:= centerPoint[1] + radius * sinValue,circlePointList.append([round(pointY, 6), round(pointZ, 6)]),
            points.append([round(pointY, 6), round(pointZ, 6)])] for i1 in range(self.numCircleSeg)],
              circlePointList.append(circlePointList[0]),points.append(circlePointList[0]),
              [[startP:= [round(circlePointList[i2][0], 6), round(circlePointList[i2][1], 6)],
                endP:= [round(circlePointList[i2 + 1][0], 6), round(circlePointList[i2 + 1][1], 6)],
                eachLineIJCoord.append([startP, endP])] for i2 in range(len(circlePointList) - 1)]] for each in circleEntity]
        except:
            pass
        #####################################
        # process arc object
        try:
            arcEntity = self.msp.query(f"""ARC[layer=="{layerName}"]""")
            [[eachSpline:= each.to_spline(replace=True),pointsList:= [],
              pointVector:= [eachValue for eachValue in eachSpline.flattening(1e8, self.numSplineSeg)],
              [[pointsList.append([round(eachPoints[0], 6), round(eachPoints[1], 6)]),
                points.append([round(eachPoints[0], 6), round(eachPoints[1], 6)])] for eachPoints in pointVector],
              [[startP:= [round(pointsList[i2][0], 6), round(pointsList[i2][1], 6)],
                endP:= [round(pointsList[i2 + 1][0], 6), round(pointsList[i2 + 1][1], 6)],
                eachLineIJCoord.append([startP, endP])] for i2 in range(len(pointsList) - 1)]] for each in arcEntity]
        except:
            pass
        #####################################
        # process LWPOLYLINE object
        try:
            LWPolineEntity = self.msp.query(f"""LWPOLYLINE[layer=="{layerName}"]""")
            for each in LWPolineEntity:
                LWPoints = [items for items in each.vertices_in_wcs()]
                for each1 in LWPoints:
                    points.append([round(each1[0], 6), round(each1[1], 6)])
                if each.dxf.flags == 1:  # polyline is closed
                    for i1 in range(len(LWPoints) - 1):
                        startP = [round(LWPoints[i1][0], 6), round(LWPoints[i1][1], 6)]
                        endP = [round(LWPoints[i1 + 1][0], 6), round(LWPoints[i1 + 1][1], 6)]
                        eachLineIJCoord.append([startP, endP])
                    startP1 = [round(LWPoints[-1][0], 6), round(LWPoints[-1][1], 6)]
                    endP1 = [round(LWPoints[0][0], 6), round(LWPoints[0][1], 6)]
                    eachLineIJCoord.append([startP1, endP1])
                else:
                    for i1 in range(len(LWPoints) - 1):
                        startP = [round(LWPoints[i1][0], 6), round(LWPoints[i1][1], 6)]
                        endP = [round(LWPoints[i1 + 1][0], 6), round(LWPoints[i1 + 1][1], 6)]
                        eachLineIJCoord.append([startP, endP])
        except:
            pass
        #####################################
        # process LINE object
        try:
            lines = self.msp.query(f"""LINE[layer=="{layerName}"]""")
            # for eachLine in lines:
            #     startP = eachLine.dxf.start
            #     endP = eachLine.dxf.end
            #     points.append([round(startP[0], 6), round(startP[1], 6)])
            #     points.append([round(endP[0], 6), round(endP[1], 6)])
            [[startP := eachLine.dxf.start,endP := eachLine.dxf.end,
              points.append([round(startP[0], 6), round(startP[1], 6)]),
              points.append([round(endP[0], 6), round(endP[1], 6)])] for eachLine in lines]
            # for eachLine in lines:
            #     startP = [round(eachLine.dxf.start[0], 6), round(eachLine.dxf.start[1], 6)]
            #     endP = [round(eachLine.dxf.end[0], 6), round(eachLine.dxf.end[1], 6)]
            #     eachLineIJCoord.append([startP, endP])
            [[startP := [round(eachLine.dxf.start[0], 6), round(eachLine.dxf.start[1], 6)],
            endP := [round(eachLine.dxf.end[0], 6), round(eachLine.dxf.end[1], 6)],
              eachLineIJCoord.append([startP, endP])] for eachLine in lines]
        except:
            pass
        #####################################
        filtPoints = []
        # for each1 in points:
        #     if each1 not in filtPoints:
        #         filtPoints.append(each1)
        [filtPoints.append(each1) for each1 in points if each1 not in filtPoints]

        pointsDict = {i1: filtPoints[i1] for i1 in range(len(filtPoints))}
        new_dict = {str(v): k for k, v in pointsDict.items()}
        ##############
        eachLineIJ = []
        # for eachLine in eachLineIJCoord:
        #     PI = new_dict[str(eachLine[0])]
        #     PJ = new_dict[str(eachLine[1])]
        #     eachLineIJ.append([int(PI), int(PJ)])
        [[PI:= new_dict[str(eachLine[0])],PJ:= new_dict[str(eachLine[1])],
          eachLineIJ.append([int(PI), int(PJ)])] for eachLine in eachLineIJCoord]
        ##############
        pointKeys = pointsDict.keys()
        loopList = []
        while (len(eachLineIJ) != 0):
            iterloop = []
            iterloop = [eachLineIJ[0]]
            eachLineIJ.remove(eachLineIJ[0])
            while len(set(list(chain(*iterloop))) & set(list(chain(*eachLineIJ)))) != 0:  # &--sets interaction
                # for each1 in eachLineIJ:
                #     if len(set(list(chain(*iterloop))) & set(each1)) != 0:  # &--sets interaction
                #         iterloop.append(each1)
                #         eachLineIJ.remove(each1)
                [[iterloop.append(each1),eachLineIJ.remove(each1)] for each1 in eachLineIJ
                 if len(set(list(chain(*iterloop))) & set(each1)) != 0]
            loopList.append(iterloop)
        ##############
        loopPointList = []
        # for each in loopList:
        #     eachLoop = list(set(list(chain(*each))))
        #     loopPointList.append(eachLoop)
        [[eachLoop:= list(set(list(chain(*each)))),loopPointList.append(eachLoop)] for each in loopList]
        # anticlock sort points
        antiSortPList = []
        # for i1 in range(len(loopList)):
        #     antiSortP = self._anticlockSortPoint(loopPointList[i1], loopList[i1], pointsDict)
        #     antiSortPList.append(antiSortP)
        [[antiSortP:= self._anticlockSortPoint(loopPointList[i1], loopList[i1], pointsDict),
          antiSortPList.append(antiSortP)] for i1 in range(len(loopList))]
        outSortList, innerSortList = self._outLoopDetermine(antiSortPList, pointsDict)
        ######################
        return outSortList, innerSortList,pointsDict

    def _outLoopDetermine(self,sortedLoopList,pointCoordDict):
        """
        ___Determine the outloop of the section ___
        """
        yMaxMin=[pointCoordDict[i1][0] for i1 in range(len(pointCoordDict))]
        yMax,yMin=max(yMaxMin),min(yMaxMin)
        zMaxMin = [pointCoordDict[i1][1] for i1 in range(len(pointCoordDict))]
        zMax, zMin = max(zMaxMin), min(zMaxMin)
        outSortList=None
        innerSortList=[]
        for each in sortedLoopList:
            eachY= [pointCoordDict[item1][0] for item1 in each]
            eachZ = [pointCoordDict[item1][1] for item1 in each]
            if (yMax in eachY) and (zMax in eachZ):
                outSortList = each
            else:
                innerSortList.append(each)
        return outSortList,innerSortList

    def _anticlockSortPoint(self, setPointList, pointPairList, pointCoordDict):
        """
        ---Anticolck sorting points in a loop---
        setPointList:[0,1,2,3...]
        pointPairList:[[0,1],[1,2],...]
        pointCoordList:{0:[0.123,3.456],1:[45.342,67.897]}
        """
        zValues = [pointCoordDict[each][1] for each in setPointList]
        zMinIndex = zValues.index(min(zValues))
        startP = setPointList[zMinIndex]
        linkTwoP = [each for each in pointPairList if startP in each]
        x0, y0 = pointCoordDict[startP][0], pointCoordDict[startP][1]
        setList = list(set(list(chain(*linkTwoP))))
        linkP = [each for each in setList if each != startP]
        x1, y1 = pointCoordDict[linkP[0]][0], pointCoordDict[linkP[0]][1]
        x2, y2 = pointCoordDict[linkP[1]][0], pointCoordDict[linkP[1]][1]
        angle1 = math.atan2(y1 - y0, x1 - x0)
        angle2 = math.atan2(y2 - y0, x2 - x0)
        if angle1 < 0:
            angle1 = angle1 * 180 / 3.1415926 + 360
        else:
            angle1 = angle1 * 180 / 3.1415926
        if angle2 < 0:
            angle2 = angle2 * 180 / 3.1415926 + 360
        else:
            angle2 = angle2 * 180 / 3.1415926
        if angle1 > angle2:
            nextP = linkP[1]
        else:
            nextP = linkP[0]
        sortedPList = []
        sortedPList.append(startP)
        sortedPList.append(nextP)
        [[select := [each for each in pointPairList if sortedPList[-1] in each],
          finalSelect := [each for each in select if not (set(each).issubset(set(sortedPList)))],
          finalValue := [each2 for each2 in finalSelect[0] if each2 != sortedPList[-1]],
          sortedPList.append(finalValue[0])] for i2 in range(len(setPointList) - 2)]
        return sortedPList

    def _triEleInfo(self, points, triangles):
        """
        Calculate the area and the centroid coordinates of triangle element
        Input：points-vertex of triangel element[[x1,y1,Z1],[x2,y2,Z2]]
            triangles-triangle element list[[I1,J1,K1],[I2,J2,K2]]
        Output：
           inFoList:fiber element information [(xc1,yc1,area1),(xc2,yc2,area2)]
        """
        inFoList = []
        [[I:=each[0],J:=each[1],K:=each[2],x1:= points[I][0],y1:= points[I][1],x2:= points[J][0],
          y2:= points[J][1],x3:= points[K][0],y3:= points[K][1],
          area:= 0.5 * (x1 * y2 - x2 * y1 + x2 * y3 - x3 * y2 + x3 * y1 - x1 * y3),xc:= (x1 + x2 + x3) / 3.0,
          yc:= (y1 + y2 + y3) / 3.0,inFoList.append((xc, yc, area))] for each in triangles]
        return inFoList

    def cadModelProcess(self):
        """"""
        linesList = []
        self.doc = ezdxf.readfile(self.filename)
        self.msp = self.doc.modelspace()
        layerNameList = [eachLayer.dxf.name for eachLayer in self.doc.layers]
        if "lines" in layerNameList:
            self.uiInstance.displayLabel.setStyleSheet("color: black;")
            outSortList, innerSortList,pointsDict=self.layerEntityProcess_lines(layerName="lines")
        else:
            self.uiInstance.displayLabel.setText("Plot the lines of section with layer named 'lines', unit: cm.")
            self.uiInstance.displayLabel.setStyleSheet("color: red;")
            raise ValueError()
        verticesList=[pointsDict[eachTag] for eachTag in outSortList]
        PolygonOffsetInstance=PolygonOffset(verticesList,self.outCoverThickness*100)
        offset_outPolygonCoordsList=PolygonOffsetInstance.returnOffsetPolygonCoordsList()
        innerVerticesList=[]
        innerOffsetList=[]
        [[tempVerticesList := [pointsDict[eachTag] for eachTag in eachList], innerVerticesList.append(tempVerticesList),
          polyinstance := PolygonOffset(tempVerticesList, -self.innerCoverThickness*100),
          innerOffsetList.append(polyinstance.returnOffsetPolygonCoordsList())] for eachList in innerSortList]
        ##########################---Out lines of cover
        outCoverVerticesList = []
        outCoverVerticesList.append([[each[0] * 0.01, each[1] * 0.01, 0] for each in verticesList])
        outCoverVerticesList.append([[float(each[0]) * 0.01, float(each[1]) * 0.01, 0] for each in offset_outPolygonCoordsList])
        ##########################---inner lines of cover
        innerCoverVerticesList = []
        [[innerHole := [[each[0] * 0.01, each[1] * 0.01, 0] for each in innerVerticesList[i1]],
          offsetInnerhole := [[float(each[0]) * 0.01, float(each[1]) * 0.01, 0] for each in innerOffsetList[i1]],
          innerCoverVerticesList.append([offsetInnerhole, innerHole])] for i1 in range(len(innerVerticesList))]
        #########################---core border
        coreVerticesList = []
        coreVerticesList.append(outCoverVerticesList[1])
        [coreVerticesList.append(innerCoverVerticesList[i1][0]) for i1 in range(len(innerCoverVerticesList))]
        ##########################
        ##########################---core fiber discretization
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = self.coreFiberSize
            outPolygon = geom.add_polygon(coreVerticesList[0])
            if len(coreVerticesList) > 1:
                for eachInnerList in coreVerticesList[1:]:
                    inPolygon = geom.add_polygon(eachInnerList)
                    differencePolygon = geom.boolean_difference(outPolygon, inPolygon)
                    outPolygon = differencePolygon
            mesh = geom.generate_mesh()
            corePoints = mesh.points
            coreTriangles = []
            [coreTriangles.extend(cell_block.data) for cell_block in mesh.cells if cell_block.type == 'triangle']
            coreFiberInfo = self._triEleInfo(corePoints, coreTriangles)
        ############################################---inner cover fiber discretization
        innerPoints = []
        innerTriangles = []
        innerFiberInfo = []
        if len(innerCoverVerticesList) > 0:
            for each in innerCoverVerticesList:
                with pygmsh.occ.Geometry() as geom:
                    geom.characteristic_length_max = self.innerCoverFiberSize
                    mainPolygon = geom.add_polygon(each[0])
                    subPolygon = geom.add_polygon(each[1])
                    geom.boolean_difference(mainPolygon, subPolygon)
                    mesh = geom.generate_mesh()
                    tempPoints = mesh.points
                    tempTriangles = []
                    [tempTriangles.extend(cell_block.data) for cell_block in mesh.cells if
                     cell_block.type == 'triangle']
                    tempFiberInfo = self._triEleInfo(tempPoints, tempTriangles)
                innerPoints.append(tempPoints)
                innerTriangles.append(tempTriangles)
                innerFiberInfo.append(tempFiberInfo)
        ############################################---out cover fiber discretization
        outPoints = []
        outTriangles = []
        outFiberInfo = []
        if len(outCoverVerticesList) > 0:
            with pygmsh.occ.Geometry() as geom:
                geom.characteristic_length_max = self.outCoverFiberSize
                mainPolygon = geom.add_polygon(outCoverVerticesList[0])
                subPolygon = geom.add_polygon(outCoverVerticesList[1])
                geom.boolean_difference(mainPolygon, subPolygon)
                mesh = geom.generate_mesh()
                tempPoints = mesh.points
                tempTriangles = []
                [tempTriangles.extend(cell_block.data) for cell_block in mesh.cells if
                 cell_block.type == 'triangle']
                tempFiberInfo = self._triEleInfo(tempPoints, tempTriangles)
            outPoints.append(tempPoints)
            outTriangles.append(tempTriangles)
            outFiberInfo.append(tempFiberInfo)
        ##########################Determine sectional center
        XdAList = []
        YdAList = []
        dAList = []
        [[XdAList.append(float(each[0]) * float(each[2])), YdAList.append(float(each[1]) * float(each[2])),
          dAList.append(float(each[2]))] for each in coreFiberInfo]
        [[[XdAList.append(float(each[0]) * float(each[2])), YdAList.append(float(each[1]) * float(each[2])),
           dAList.append(float(each[2]))] for each in eachHole] for eachHole in innerFiberInfo]
        [[[XdAList.append(float(each[0]) * float(each[2])), YdAList.append(float(each[1]) * float(each[2])),
           dAList.append(float(each[2]))] for each in eachHole] for eachHole in outFiberInfo]
        xCenter = sum(XdAList) / float(sum(dAList))
        yCenter = sum(YdAList) / float(sum(dAList))
        ######################### triangles
        corePoints = np.array(
            [[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])] for each in corePoints])
        innerPoints = [np.array([[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])]
                                 for each in eachHole]) for eachHole in innerPoints]
        outPoints = [np.array([[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])]
                               for each in eachHole]) for eachHole in outPoints]
        ##########################---fiber elements
        coreFiberInfo = [[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])] for each in
                         coreFiberInfo]
        innerFiberInfo = [[[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])]
                           for each in eachHole] for eachHole in innerFiberInfo]
        outFiberInfo = [[[float(each[0] - xCenter), float(each[1] - yCenter), float(each[2])] for each in eachHole]
                        for eachHole in outFiberInfo]
        ###################################################---rebars
        rebarNameList = []
        for eachLayer in layerNameList:
            try:
                rebarName, _ = eachLayer.split('_', 1)
                if rebarName == 'bars':
                    rebarNameList.append(eachLayer)
            except:
                pass
        ######################
        rebarNameList=[f"bars_{int(i1+1)}" for i1 in range(len(rebarNameList))]
        ######################
        barFiberInfo = []
        [[tempList := [], circleEntity := self.msp.query(f"""CIRCLE[layer=="{eachBarLayer}"]"""),
          [[centerPoint := each.dxf.center, radius := each.dxf.radius,
            tempList.append(
                [centerPoint[0] * 0.01 - xCenter, centerPoint[1] * 0.01 - yCenter, np.pi * (radius * 0.01) ** 2])]
           for each in circleEntity], barFiberInfo.append(tempList)] for eachBarLayer in rebarNameList]
        ###################################################################
        barFiberInfoList=[]
        for each in barFiberInfo:
            if len(each)>0:
                barFiberInfoList.append(each)
        barFiberInfo=barFiberInfoList
        rebarNameList=[f"bars_{int(i1+1)}" for i1 in range(len(barFiberInfo))]
        ####################################################################---width to height ratio of the figure
        origalX = [each[0] * 0.01 - xCenter for each in verticesList]
        origalX.append(origalX[0])
        orginalY = [each[1] * 0.01 - yCenter for each in verticesList]
        orginalY.append(orginalY[0])
        minx, maxx = min(origalX), max(origalX)
        miny, maxy = min(orginalY), max(orginalY)
        width = maxx - minx
        height = maxy - miny
        sectionWidthHeightRatio = width / float(height)
        return (coreFiberInfo, innerFiberInfo, outFiberInfo,barFiberInfo,corePoints, innerPoints, outPoints,
                coreTriangles,outTriangles,innerTriangles,sectionWidthHeightRatio,rebarNameList)
########################################################################################################################
########################################################################################################################
class PolygonOffset():
    def __init__(self, polygonCoordsList,offsetValue):
        """
        polygonCoordsList:[[x1,y1],[x2,y2],...]---eg.[(0, 0), (4, 0), (4, 3), (4, 5), (1, 5)]
        offsetValue:Positive means outward Negative means inward
        """
        self.polygonCoordsList = polygonCoordsList
        self.offsetValue = offsetValue

    def line_intersection(self,P1, d1, P2, d2):
        """
        Determine the interact points of two lines
        Line1: P1 + t*d1
        Line2: P2 + s*d2
        If parallel return None
        """
        denom = d1[0] * d2[1] - d1[1] * d2[0]
        if np.abs(denom) < 1e-10:
            return None  # Two lines parallel
        diff = P2 - P1
        t = (diff[0] * d2[1] - diff[1] * d2[0]) / denom
        return P1 + t * d1

    def compute_polygon_area(self,vertices):
        """
        Calculate the area of the polygon to determine the sequence of vetexs (positive: anticlockwise, negtive:clockwise
        """
        area = 0.0
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return area / 2

    def returnOffsetPolygonCoordsList(self):
        """"""
        n = len(self.polygonCoordsList)
        vertices = [np.array(p, dtype=float) for p in self.polygonCoordsList]

        area = self.compute_polygon_area(vertices)
        factor = 1 if area > 0 else -1

        offset_lines = []
        [[P1:=vertices[i],P2:=vertices[(i+1)%n],edge:=P2-P1,normal:=factor * np.array([-edge[1], edge[0]]),
          normal:= normal / np.linalg.norm(normal),offset_point:= P1 + self.offsetValue * normal,
        offset_lines.append((offset_point, edge))] for i in range(n)]

        new_vertices = []
        for i in range(n):
            P1, d1 = offset_lines[i - 1]
            P2, d2 = offset_lines[i]

            inter_pt = self.line_intersection(P1, d1, P2, d2)
            if inter_pt is None:
                inter_pt = (P1 + P2) / 2
            new_vertices.append(inter_pt)
        return new_vertices
########################################################################################################################
########################################################################################################################
class Material():
    def __init__ (self):
        pass
    def barParameter(self, steelTag):
        """
        steelTag --unique material object integer tag
        fy --Yield stress in tension(kPa)
        fu --Ultimate stress in tension(kPa)
        Es--Initial elastic tangent(kPa)
        Esh--Tangent at initial strain hardening(kPa)
        esh--Strain corresponding to initial strain hardening
        eult--Strain at peak stress
        """
        fy = eval("".join(list(filter(str.isdigit, steelTag))))*1000
        Es = 2e8
        Esh = 2e6
        esh = 0.045
        eult = 0.1
        fu = 0.01*Es*(eult-esh)+fy
        barPara = [fy, fu, Es, Esh, esh, eult]
        return barPara

    def coverParameter(self, concreteTag):
        """
        concreteTag --unique material object integer tag
        fc --concrete compressive strength at 28 days(kPa)
        ec --concrete strain at maximum strength
        ecu-- concrete strain at crushing strength
        Ec--initial stiffness(kPa)
        """
        def factor1(R):
            if R<=50:
                return 0.76
            elif R==80:
                return 0.82
            else:
                return 0.76+0.06*(R-50)/30
        def factor2(R):
            if R<40:
                return 1.00
            elif R==80:
                return 0.87
            else:
                return 1-0.13*(R-40)/40
        R = eval("".join(list(filter(str.isdigit, concreteTag))))
        fc = -R*0.88*factor1(R)*factor2(R)*1000
        ec = -0.002
        ecu = -0.004
        Ec = math.sqrt(-fc/1000)*5e6
        coverPara = [fc, ec, ecu, Ec]
        return coverPara

    def coreParameterCircular(self, concreteTag, hoop, d, coverThick, roucc, s, ds, fyh):
        """
        :param concreteTag: Concrete grade
        :param hoop:stirrup type，'Circular'circle stirrup，'Spiral'spiral stirrup
        :param d: Diameter
        :param coverThick: depth of cover concrete
        :param roucc: Longitudinal reinforcement ratio
        :param s: Stirrup space in longitudinal direction
        :param ds: Diameter of stirrup
        :param fyh: Yield stress of stirrup (MPa)
        Outputs:
            1000*fc(float)-Compressive stress of the core concrete (kpa)
            ec(float)-Strain corresponding to the compressive stress
            ecu(float)-Ultimate strain
            Ec(float)-Initial elastic modulus (kPa)
        """
        fco = self.coverParameter(concreteTag)[0]
        Ec = math.sqrt(-fco / 1000) * 5e6
        confinedConcrete = Mander()
        fc, ec, ecu = confinedConcrete.circular(hoop, d, coverThick, roucc, s, ds, fyh, -fco/1000)
        corePara = [float(1000*fc), float(ec), float(ecu), Ec]
        return corePara


    def coreParameterRectangular(self, concreteTag, lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh):
        """
        :param concreteTag: Concrete grade
        :param lx: Sectional width in x direction
        :param ly: Sectional width in y direction
        :param coverThick: Cover depth
        :param roucc: Reinforcement ratio in longitudinal direction
        :param sl: longitudinal rebars space
        :param dsl:Diameter of longitudinal rebars
        :param roux: Stirrup volume ratio in x direction
        :param rouy: Stirrup volume ratio in y direction
        :param st: stirrup space
        :param dst:Stirrup diameter
        :param fyh: yield stress of strirrup (MPa)
        Outputs:
            1000*fc(float)-Compressive stress of core concrete (kpa)
            ec(float)-Strain corresponding to the compressive stress
            ecu(float)-Ultimate strain
            Ec(float)-Initla elastic modulus (kPa)

        """
        fco = self.coverParameter(concreteTag)[0]
        Ec = math.sqrt(-fco / 1000) * 5e6
        confinedConcrete = Mander()
        fc, ec, ecu = confinedConcrete.rectangular(lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh, -fco/1000)
        corePara = [1000*fc, ec, ecu, Ec]
        return corePara
########################################################################################################################
########################################################################################################################
class Mander():
    def __init__ (self):
        self.eco = 0.002 #Strain corresponding to the maximum stress for unconfined concrete
        self.esu = 0.09 #Ultimate strain for strirrup

    def william_warnke(self, sigma1, sigma2, sigma3):
        """
        William-Warnke Concrete constitutive model with 5 parameters
        :param sigma1: First principle stress
        :param sigma2: Second principle stress
        :param sigma3: Third principle stress
        :return: Yield function value
        """
        getcontext().prec = 30
        sigma1, sigma2, sigma3 = Decimal(sigma1), Decimal(sigma2), Decimal(sigma3)
        sigmaa = (sigma1 + sigma2 + sigma3) / Decimal(3)
        taoa = ((sigma1 - sigma2) ** Decimal(2) + (sigma2 - sigma3) ** Decimal(2) + (sigma3 - sigma1) ** Decimal(2)) ** Decimal(0.5) / Decimal(15) ** Decimal(0.5)

        #Parameter values based on experimental results
        #alphat, alphac, kexi, rou1, rou2=Decimal(0.15),Decimal(1.8),Decimal(3.67),Decimal(1.5),Decimal(1.94)
        #a2 = Decimal(9)*(Decimal(1.2)**Decimal(0.5)*kexi*(alphat-alphac)-Decimal(1.2)**Decimal(0.5)*alphat*alphac+rou1*(Decimal(2)*alphac+alphat))/((Decimal(2)*alphac+alphat)*(Decimal(3)*kexi-Decimal(2)*alphac)*(Decimal(3)*kexi+alphat))
        #a1 = (Decimal(2)*alphac-alphat)*a2/Decimal(3)+Decimal(1.2)**Decimal(0.5)*(alphat-alphac)/(Decimal(2)*alphac+alphat)
        #a0 = Decimal(2)*alphac*a1/Decimal(3)-Decimal(4)*alphac**Decimal(2)*a2/Decimal(9)+(Decimal(2)/Decimal(15))**Decimal(0.5)*alphac
        #kexi0 = (-a1-(a1**2-Decimal(4)*a0*a2)**Decimal(0.5))/(Decimal(2)*a2)
        #b2 = Decimal(9)*(rou2*(kexi0+Decimal(1)/Decimal(3))-(Decimal(2)/Decimal(15))**Decimal(0.5)*(kexi0+kexi))/((kexi+kexi0)*(Decimal(3)*kexi-Decimal(1))*(Decimal(3)*kexi0+Decimal(1)))
        #b1 = (kexi+Decimal(1)/Decimal(3))*b2+(Decimal(1.2)**Decimal(0.5)-Decimal(3)*rou2)/(Decimal(3)*kexi-Decimal(1))
        #b0 = -kexi0*b1-kexi0**Decimal(2)*b2
        #r1 = a0+a1*sigmaa+a2*sigmaa**Decimal(2)
        #r2 = b0+b1*sigmaa+b2*sigmaa**Decimal(2)

        # Refer to Schickert-Winkler experimental results
        r1 = Decimal(0.053627)-Decimal(0.512079)*sigmaa-Decimal(0.038226)*sigmaa**Decimal(2)
        r2 = Decimal(0.095248)-Decimal(0.891175)*sigmaa-Decimal(0.244420)*sigmaa**Decimal(2)

        r21 = r2**Decimal(2)-r1**Decimal(2)
        cosxita = (Decimal(2)*sigma1-sigma2-sigma3)/(Decimal(2)**Decimal(0.5)*((sigma1-sigma2)**Decimal(2)+(sigma2-sigma3)**Decimal(2)+(sigma3-sigma1)**Decimal(2))**Decimal(0.5))
        rxita = (Decimal(2)*r2*r21*cosxita+r2*(Decimal(2)*r1-r2)*(Decimal(4)*r21*cosxita**Decimal(2)+Decimal(5)*r1**Decimal(2)-Decimal(4)*r1*r2)**Decimal(0.5))/(Decimal(4)*r21*cosxita**Decimal(2)+(r2-Decimal(2)*r1)**Decimal(2))
        return taoa/rxita-1

    def confinedStrengthRatio(self, confiningStrengthRatio1, confiningStrengthRatio2):
        """
        :param confiningStrengthRatio1: Confined stress ratio in x direction
        :param confiningStrengthRatio2: Confined stress ratio in y direction
        :return: Strength enhancement coefficient for core concrete
        """
        sigma1 = -min(confiningStrengthRatio1, confiningStrengthRatio2)
        sigma2 = -max(confiningStrengthRatio1, confiningStrengthRatio2)
        sigma3Min = -4
        sigma3Max = -1
        while True:
            sigma3Mid = (sigma3Min + sigma3Max) / 2
            fun_min = self.william_warnke(sigma1, sigma2, sigma3Min)
            fun_max = self.william_warnke(sigma1, sigma2, sigma3Max)
            fun_mid = self.william_warnke(sigma1, sigma2, sigma3Mid)
            if abs(fun_mid) < 0.001:
                return -sigma3Mid
                break
            elif fun_min * fun_mid < 0:
                sigma3Max = sigma3Mid
            elif fun_max * fun_mid < 0:
                sigma3Min = sigma3Mid

    def circular(self, hoop, d, coverThick, roucc, s, ds, fyh, fco):
        """
        Calculate the Mander model parater values for circular section
        :param hoop:Stirrup type，Circular: circular stirrup，Spiral: spiral stirrup
        :param d: Diameter
        :param coverThick: Cover depth
        :param roucc: Reinforcement ratio in longtitudinal direction
        :param s: Stirrup space
        :param ds: Stirrup diameter
        :param fyh: Yield strength for stirrup (MPa)
        :param fco: Compressive strength for unconfined concrete(MPa)
        :return:Compressive strength for confined concrete(MPa)、the conresponding strain、ultimate strain
        """
        de = d - 2*coverThick - ds
        if hoop=='Circular':
            ke = (1 - 0.5*s / de) ** 2 / (1 - roucc)
        elif hoop=='Spiral':
            ke = (1 - 0.5*s / de) / (1 - roucc)
        rous = 3.14159*ds**2/(de*s)
        fle = 0.5*ke*rous*fyh
        fcc = fco*(-1.254+2.254*math.sqrt(1+7.94*fle/fco)-2*fle/fco)
        ecc = self.eco*(1+5*(fcc/fco-1))
        ecu = 0.004+1.4*rous*fyh*self.esu/fcc
        print("the ultimate strain for confined conrete is:",ecu)
        return -fcc, -ecc, -ecu

    def rectangular(self, lx, ly, coverThick, roucc, sl, dsl, roux, rouy, st, dst, fyh, fco):
        """
        Calculate the Mander model parameter values for rectangular section
        :param lx: Sectional width in x direction
        :param ly: Sectional width in y direction
        :param coverThick: Cover depth
        :param roucc: Reinforcement ratio in longitudinal direction
        :param sl: Longitudinal rebars space
        :param dsl: Longitudinal rebars diameter
        :param roux: Strirrup volume ratio in x direction
        :param rouy: Strirrup volume ratio in y direction
        :param st: Stirrup space
        :param dst: Strirrup diameter
        :param fyh: Yield strength for stirrup (MPa)
        :param fco: Compressive stress for unconfined concrete (MPa)
        :return:Compressive strength for confined concrete(MPa)、the conresponding strain、ultimate strain
        """
        lxe = lx - 2*coverThick-dst
        lye = ly - 2*coverThick-dst
        nsl = 2*(lxe+lye-4*dsl)*sl
        ke = (1-nsl*sl**2/6)*(1-0.5*st/lxe)*(1-0.5*st/lye)/(1-roucc)
        flxe = ke * roux * fyh
        flye = ke * rouy * fyh
        fcc = fco *self.confinedStrengthRatio(flxe/fco, flye/fco)
        ecc = self.eco*(1+5*(fcc/fco-1))
        ecu = 0.004+1.4*(roux+rouy)*fyh*self.esu/fcc
        return -fcc, -ecc, -ecu
########################################################################################################################
########################################################################################################################
class MC():
    def __init__(self, groupName,dbInstance,loadDir,barMatDict,dbPath):
        """
        :param sectName: section name
        :param dbInstance: a hdf5 database instance
        :param loadDir: calculated direction ('X' or 'Y')
        """
        self.groupName = groupName
        self.dbInstance=dbInstance
        self.direction = loadDir
        self.barMatDict=barMatDict
        self.dbPath = dbPath

    def MCAnalysis(self, axialLoad, moment,numIncr=25):
        """
        Moment curvature analysis for definded section
        :param axialLoad: axial load，negtive implies compression
        :param moment: moment in the other direction
        :param maxMu: target ductility coefficient for analysis
        :param numIncr: number of analysis increments
        """
        if self.direction == 'X':
            flagx = 1
            flagy = 0
        else:
            flagx = 0
            flagy = 1

        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)

        ops.node(1, 0.0, 0.0, 0.0)
        ops.node(2, 0.0, 0.0, 0.0)

        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ops.fix(2, 0, 1, 1, 1, 0, 0) ####---fix all degrees of freedom except axial and bending
        coverParameter=self.dbInstance.getResult(self.dbPath,f"{self.groupName}/coverConcreteMatParas")[0]
        ops.uniaxialMaterial('Concrete04', 7777, coverParameter[0], coverParameter[1], coverParameter[2], coverParameter[3])
        #################################
        coreParameter=self.dbInstance.getResult(self.dbPath,f"{self.groupName}/coreConcreteMatParas")[0]
        ops.uniaxialMaterial('Concrete04', 8888, coreParameter[0], coreParameter[1], coreParameter[2], coreParameter[3])
        ##################################################################################
        barsType=self.barMatDict["bars_type"]
        barsMatNumber=int((len(self.barMatDict)-1)*0.5)
        if barsType=='barGradeType':
            for i1 in range(1):
                matPara=self.barMatDict[f"bars_{i1+1}"]
                barsTag=self.barMatDict[f'bars_{i1 + 1}_number']
                ops.uniaxialMaterial('ReinforcingSteel',barsTag,matPara[0],matPara[1],matPara[2],matPara[3],
                                     matPara[4],matPara[5])
        elif barsType=='userInput':
            [eval(f"ops.{self.barMatDict[f"bars_{i2+1}"]}") for i2 in range(barsMatNumber)]
        ##########################################################################
        ops.section('Fiber', 1, '-GJ', 1E10)
        innerCoverFiberList=self.dbInstance.getResult(self.dbPath,f"fiberMesh/innerCoverFiberInfo")
        #######################################################
        if innerCoverFiberList is not None:
            [ops.fiber(eachCover[1], eachCover[2], eachCover[3],7777) for eachCover in innerCoverFiberList]
        ##################################
        outCoverFiberList=self.dbInstance.getResult(self.dbPath,f"fiberMesh/outCoverFiberInfo")
        [ops.fiber(eachCover[1], eachCover[2], eachCover[3],7777) for eachCover in outCoverFiberList]
        ##########################################################################
        coreFiberList=self.dbInstance.getResult(self.dbPath,f"fiberMesh/coreFiberInfo")
        [ops.fiber(eachCover[1], eachCover[2], eachCover[3],8888) for eachCover in coreFiberList]
        ###############################################################################
        [[barsFiber:=self.dbInstance.getResult(self.dbPath,f"fiberMesh/bars_{i3+1}"),
          fiberMat:=self.barMatDict[f"bars_{i3+1}_number"],[ops.fiber(eachCover[1], eachCover[2], eachCover[3],fiberMat)
                                for eachCover in barsFiber]] for i3 in range(barsMatNumber)]
        ################################################################################
        ################################################################################
        ####---x perperticular the section, y in horizontal, and z vertical
        ops.element('zeroLengthSection', 1, 1, 2, 1, '-orient', 1, 0, 0, 0, 1, 0)
        ################################
        ################################################################################
        # Define constant axial load
        ops.timeSeries('Constant', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(2, axialLoad, 0.0, 0.0, 0.0, moment*flagx, moment*flagy)
        # Define analysis parameters
        ops.integrator('LoadControl', 0.0)
        ops.system('SparseGeneral', '-piv')
        ops.test('NormUnbalance', 1e-6, 10)
        ops.numberer('Plain')
        ops.constraints('Plain')
        ops.algorithm('Newton')
        ops.analysis('Static')

        # Do one analysis for constant axial load
        ops.analyze(1)
        #################################################---record static responses
        node2_dispList=[[ops.getTime(),ops.nodeDisp(2)[int(6-flagy-1)]]]
        dispSaveName=f"{self.groupName}/node2_disp"
        headNameList = ['time','displacement']
        operationIndexStr = 'replace'
        self.dbInstance.saveResult(dispSaveName,node2_dispList, headNameList,operationIndexStr)
        #########################################################################
        [[fiberRespList:=[ops.eleResponse(1,'section','fiber',str(coreFiberList[i1][1]),str(coreFiberList[i1][2]),'stressStrain')],
        coreFiberSaveName:=f"{self.groupName}/coreFiberResp/"+str(coreFiberList[i1][0]),headNameList:= ['stress(kPa)','strain'],
        operationIndexStr:= 'replace',self.dbInstance.saveResult(coreFiberSaveName,fiberRespList, headNameList,operationIndexStr)]
         for i1 in range(len(coreFiberList))]
        #########################################################################
        if innerCoverFiberList is not None:
            [[fiberRespList:= [ops.eleResponse(1, 'section', 'fiber', str(innerCoverFiberList[i1][1]),
                                                 str(innerCoverFiberList[i1][2]),'stressStrain')],
              coverFiberSaveName:=f"{self.groupName}/innerCoverFiberResp/" + str(innerCoverFiberList[i1][0]),
            headNameList:= ['stress(kPa)', 'strain'],operationIndexStr:= 'replace',
              self.dbInstance.saveResult(coverFiberSaveName, fiberRespList, headNameList, operationIndexStr)]
             for i1 in range(len(innerCoverFiberList))]
        #########################################################################
        [[fiberRespList:= [ops.eleResponse(1, 'section', 'fiber', str(outCoverFiberList[i1][1]),
                                             str(outCoverFiberList[i1][2]),'stressStrain')],
        coverFiberSaveName:=f"{self.groupName}/outCoverFiberResp/" + str(outCoverFiberList[i1][0]),
        headNameList:= ['stress(kPa)', 'strain'],operationIndexStr:= 'replace',
          self.dbInstance.saveResult(coverFiberSaveName, fiberRespList, headNameList, operationIndexStr)]
         for i1 in range(len(outCoverFiberList))]
        ############################################################################
        [[barsFiber:=self.dbInstance.getResult(self.dbPath,f"fiberMesh/bars_{i1+1}"),
          [[fiberRespList:= [ops.eleResponse(1, 'section', 'fiber', str(barsFiber[j1][1]),
            str(barsFiber[j1][2]), 'stressStrain')],
            coverFiberSaveName:= f"{self.groupName}/barsResp_{i1+1}/" + str(barsFiber[j1][0]),
            headNameList:= ['stress(kPa)', 'strain'],operationIndexStr:= 'replace',
            self.dbInstance.saveResult(coverFiberSaveName, fiberRespList, headNameList, operationIndexStr)]
           for j1 in range(len(barsFiber))]] for i1 in range(barsMatNumber)]
        #########################################################################
        ###########################################################################
        ###---Compute curvature increment
        if self.direction == 'X':
            ky = self.dbInstance.getResult(self.dbPath,f"{self.groupName}/estimatedYieldCurvature")[0][0]
        else:
            ky = self.dbInstance.getResult(self.dbPath,f"{self.groupName}/estimatedYieldCurvature")[0][1]
        ##############################
        maxMu=self.dbInstance.getResult(self.dbPath,f"{self.groupName}/Mu")[0][0]
        ############################
        maxK = ky * maxMu
        dK = maxK /float(numIncr*2)
        smalldK=ky/float(numIncr*2)
        factors=1.0/numIncr
        dkValueList=([smalldK for i1 in range(numIncr)]+[smalldK+factors*i2*(dK-smalldK) for i2 in range(numIncr)]+
                     [dK for i3 in range(2*numIncr)])
        totalNum=len(dkValueList)
        #########################################################################
        ops.loadConst('-time', 0.0)
        # Define reference moment
        ops.timeSeries('Linear', 2)
        ops.pattern('Plain', 2, 2)
        ops.load(2, 0.0, 0.0, 0.0, 0.0, flagy, flagx)
        # Use displacement control at node 2 for section analysis
        # Do the section analysis
        nodeDispList=[]
        coreFiberDict = {coreFiberList[j1][0]: [] for j1 in range(len(coreFiberList))}
        if innerCoverFiberList is not None:
            innerCoverFiberDict={innerCoverFiberList[j1][0]:[] for j1 in range(len(innerCoverFiberList))}
        outCoverFiberDict={outCoverFiberList[j1][0]:[] for j1 in range(len(outCoverFiberList))}
        barsFiberDictList=[]
        for i2 in range(barsMatNumber):
            barsFiber = self.dbInstance.getResult(self.dbPath, f"fiberMesh/bars_{i2 + 1}")
            temp={barsFiber[j1][0]:[] for j1 in range(len(barsFiber))}
            barsFiberDictList.append(temp)
        for i00 in range(totalNum):
            ops.integrator('DisplacementControl', 2, 6 - flagy, dkValueList[i00])
            ops.analyze(1)
            nodeDispList.append([ops.getTime(),ops.nodeDisp(2)[int(6 - flagy - 1)]])
            #####################
            for i1 in range(len(coreFiberList)):
                tempValue = ops.eleResponse(1, 'section', 'fiber', str(coreFiberList[i1][1]), str(coreFiberList[i1][2]),
                                             'stressStrain')
                coreFiberDict[coreFiberList[i1][0]].append(tempValue)
            ###########################################
            if innerCoverFiberList is not None:
                for i1 in range(len(innerCoverFiberList)):
                    tempValue = ops.eleResponse(1, 'section', 'fiber', str(innerCoverFiberList[i1][1]),
                                                str(innerCoverFiberList[i1][2]),'stressStrain')
                    innerCoverFiberDict[innerCoverFiberList[i1][0]].append(tempValue)
            #############################################
            for i1 in range(len(outCoverFiberList)):
                tempValue = ops.eleResponse(1, 'section', 'fiber', str(outCoverFiberList[i1][1]),
                                            str(outCoverFiberList[i1][2]), 'stressStrain')
                outCoverFiberDict[outCoverFiberList[i1][0]].append(tempValue)
            ################################################
            for i1_1 in range(barsMatNumber):
                barsFiber = self.dbInstance.getResult(self.dbPath, f"fiberMesh/bars_{i1_1 + 1}")
                for i1_2 in range(len(barsFiber)):
                    tempValue = ops.eleResponse(1, 'section', 'fiber', str(barsFiber[i1_2][1]),
                                                str(barsFiber[i1_2][2]), 'stressStrain')
                    barsFiberDictList[i1_1][barsFiber[i1_2][0]].append(tempValue)
            ###################################################################

        ########################################
        dispSaveName =f"{self.groupName}/node2_disp"
        headNameList = ['time', 'displacement']
        operationIndexStr = 'append'
        self.dbInstance.saveResult(dispSaveName, nodeDispList, headNameList, operationIndexStr)
        #########################################
        [[SaveName:=f"{self.groupName}/coreFiberResp/"+str(coreFiberList[i1][0]),
          headNameList:= ['stress(kPa)', 'strain'],RespList:= coreFiberDict[coreFiberList[i1][0]],
        operationIndexStr:= 'append',self.dbInstance.saveResult(SaveName,RespList, headNameList,operationIndexStr)]
         for i1 in range(len(coreFiberList))]
        ##########################################
        if innerCoverFiberList is not None:
            [[SaveName:= f"{self.groupName}/innerCoverFiberResp/" + str(innerCoverFiberList[i1][0]),
            headNameList:= ['stress(kPa)', 'strain'],RespList:= innerCoverFiberDict[innerCoverFiberList[i1][0]],
            operationIndexStr:= 'append',self.dbInstance.saveResult(SaveName, RespList, headNameList, operationIndexStr)]
             for i1 in range(len(innerCoverFiberList))]
        #########################################
        [[SaveName:= f"{self.groupName}/outCoverFiberResp/" + str(outCoverFiberList[i1][0]),
          headNameList:= ['stress(kPa)', 'strain'], RespList:= outCoverFiberDict[outCoverFiberList[i1][0]],
          operationIndexStr:= 'append',self.dbInstance.saveResult(SaveName, RespList, headNameList, operationIndexStr)]
         for i1 in range(len(outCoverFiberList))]
        ###########################################
        [[barsFiber:= self.dbInstance.getResult(self.dbPath, f"fiberMesh/bars_{i0 + 1}"),
          [[SaveName:=f"{self.groupName}/barsResp_{i0 + 1}/" + str(barsFiber[i1][0]),
            headNameList:= ['stress(kPa)', 'strain'],RespList:= barsFiberDictList[i0][barsFiber[i1][0]],
        operationIndexStr:= 'append',self.dbInstance.saveResult(SaveName, RespList, headNameList, operationIndexStr)]
           for i1 in range(len(barsFiber))]] for i0 in range(barsMatNumber)]
        ###########################################
        ops.wipe()
        print('MomentCurvature is OK!')

    def MCCurve(self,mcCurveFigure,mcCurveAx,mcCurveCanvans,dbPath,groupName,instance):
        """"""
        ###################################
        ecu = self.dbInstance.getResult(dbPath, f"{groupName}/coreConcreteMatParas")[0][2]
        try:
            fsy,_,Es,_,_,esu=self.dbInstance.getResult(dbPath,f"{groupName}/barMatParas")[0]
            ey = fsy /float(Es)
        except:
            ey=None
            esu=0.1
        ###################################
        momentCurvature=self.dbInstance.getResult(dbPath,f"{groupName}/node2_disp")
        sectCurvature=[each[1] for each in momentCurvature]
        sectMoment=[each[0] for each in momentCurvature]
        sectCurvature[0]=0.0
        sectMoment[0]=0.0
        ###################################
        ######################################
        barYieldIndexList=[]
        barDataSetsNames=self.dbInstance.partialMatchDataSets(dbPath,"fiberMesh","bars")
        barDataSetsNamesResp=[f"barsResp_{i1+1}" for i1 in range(len(barDataSetsNames))]
        ###---寻找钢筋首次屈服点
        if ey is not None:
            for j1 in range(len(barDataSetsNames)):
                barsList=self.dbInstance.getResult(dbPath,f"fiberMesh/{barDataSetsNames[j1]}")
                barsTagList=[each[0] for each in barsList]
                for eachTag in barsTagList:
                    barStressStrain=self.dbInstance.getResult(dbPath,f"{groupName}/{barDataSetsNamesResp[j1]}/{eachTag}")
                    barStrain=[each[1] for each in barStressStrain]
                    for i11 in range(len(barStrain)):
                        if barStrain[i11]>ey:
                            barYieldIndexList.append(i11)
                            break
            barYieldIndex=min(barYieldIndexList)
            barYieldCurvature=sectCurvature[barYieldIndex]
            barYieldMoment=sectMoment[barYieldIndex]
            print('yieldM,yielde',barYieldMoment,barYieldCurvature)
        #############################################################################################
        #Serach for the point concret crushing or rebar reach ultimate strain
        barCrackIndex = len(sectMoment)-1
        barCrackIndexList = []
        for j1 in range(len(barDataSetsNames)):
            barsList=self.dbInstance.getResult(dbPath,f"fiberMesh/{barDataSetsNames[j1]}")
            barsTagList=[each[0] for each in barsList]
            for eachTag in barsTagList:
                barStressStrain=self.dbInstance.getResult(dbPath,f"{groupName}/{barDataSetsNamesResp[j1]}/{eachTag}")
                barStrain = [each[1] for each in barStressStrain]
                for i22 in range(len(barStrain)):
                    if barStrain[i22] > esu:
                        barCrackIndexList.append(i22)
                        break
                    elif barStrain[i22] <= -esu:
                        barCrackIndexList.append(i22)
                        break
        try:
            barCrackIndex = min(barCrackIndexList)
        except:
            pass
        print("barCrackIndex=", barCrackIndex)
        #######################################################
        coreCrackIndex = len(sectMoment)-1
        coreCrackIndexList = []
        coreStressStrain = self.dbInstance.getResult(dbPath,f"fiberMesh/coreFiberInfo")
        coreFiberTags=[each[0] for each in coreStressStrain]
        for eachTag in coreFiberTags:
            coreStressStrain=self.dbInstance.getResult(dbPath,f"{groupName}/coreFiberResp/{eachTag}")
            coreStain=[each[1] for each in coreStressStrain]
            for i33 in range(len(coreStain)):
                if coreStain[i33]<ecu:
                    coreCrackIndexList.append(i33)
                    break
        try:
            coreCrackIndex=min(coreCrackIndexList)
        except:
            pass
        crackIndex = min(barCrackIndex, coreCrackIndex)
        if crackIndex == len(sectMoment)-1:
            instance.displayLabel.setText("A larger Mu is required!")
            instance.displayLabel.setStyleSheet("color: red;")
            raise ValueError()
        else:
            instance.displayLabel.setText("")
            instance.displayLabel.setStyleSheet("color: black;")
        ##################################################
        ultimateMoment = sectMoment[crackIndex]
        ultimateCurvature = sectCurvature[crackIndex]
        print('ultM,ulte：',ultimateMoment,ultimateCurvature)
        #####################################################
        #Search for the maximum momnet point
        momentMaxMoment = max(sectMoment[:crackIndex+1])
        for i44 in range(len(sectMoment)):
            if sectMoment[i44]==momentMaxMoment:
                momentMaxIndex=i44
                break
        momentMaxCurvature = sectCurvature[:crackIndex+1][momentMaxIndex]
        print('maxM, maxe：',momentMaxMoment,momentMaxCurvature)

        #Calculate effective moment and curvature
        if ey is not None:
            totArea=np.trapz(sectMoment[:crackIndex], sectCurvature[:crackIndex])
            barYieldX=barYieldCurvature
            barYieldY=barYieldMoment
            tanXY=barYieldY/barYieldX

            epsilon=0.001*totArea
            low=0.0
            high=momentMaxMoment
            momentEffictive=(low+high)/2.0
            while abs(momentEffictive*ultimateCurvature-momentEffictive*0.5*momentEffictive/float(tanXY)-totArea)>=epsilon:
                if momentEffictive*ultimateCurvature-momentEffictive/float(tanXY)*momentEffictive*0.5<totArea:
                    low=momentEffictive
                else:
                    high=momentEffictive
                momentEffictive=(high+low)/2.0

            curvatureEffective=momentEffictive/float(tanXY)
            blinerX=[0,curvatureEffective,ultimateCurvature]
            blinerY=[0,momentEffictive,momentEffictive]
            print('effM, effe：', momentEffictive, curvatureEffective)
            #####################################################################
            mcYieldIndex=None
            mcEffectiveIndex=None
            mcMaximumIndex=None
            mcUltimateIndex=None
            for i11 in range(len(sectCurvature)):
                if sectCurvature[i11]>=barYieldCurvature:
                    mcYieldIndex=i11
                    break
            for i11 in range(len(sectCurvature)):
                if sectCurvature[i11]>=curvatureEffective:
                    mcEffectiveIndex=i11
                    break
            for i11 in range(len(sectCurvature)):
                if sectCurvature[i11]>=momentMaxCurvature:
                    mcMaximumIndex=i11
                    break
            for i11 in range(len(sectCurvature)):
                if sectCurvature[i11]>=ultimateCurvature:
                    mcUltimateIndex=i11
                    break
            ####################################
            if mcMaximumIndex is None:
                mcMaximumIndex=len(sectCurvature)-1
            if mcUltimateIndex is None:
                mcUltimateIndex=len(sectCurvature)-1
            ####################################
            pointsIndexList=[[mcYieldIndex,mcEffectiveIndex,mcMaximumIndex,mcUltimateIndex]]
            indexSaveName = f"{groupName}/pointsIndex"
            headNameList = ['yieldIndex', 'effectiveIndex','maximumIndex','ultimateIndex']
            operationIndexStr = 'replace'
            self.dbInstance.saveResult(indexSaveName, pointsIndexList, headNameList, operationIndexStr)
        #####################################################################
        mcCurveAx.clear()
        sectName=self.dbInstance.getResult(dbPath,f"{groupName}/caseName")[0][0]
        mcCurveFigure.suptitle(f"Moment-curvature curve for section-{sectName}")
        mcCurveAx.set_xlabel("curvature")
        mcCurveAx.set_ylabel("moment(kN.m)")
        mcCurveAx.set_xlim(0,max(sectCurvature[:crackIndex])*1.1)
        mcCurveAx.set_ylim(0,max(sectMoment[:crackIndex])*1.2)
        mcCurveAx.grid(True,linestyle='--', color='gray',linewidth=0.2)
        #############
        mcCurveAx.plot(sectCurvature[:crackIndex], sectMoment[:crackIndex], c='r', linestyle='--', linewidth=1)
        ###########
        if ey is not None:
            points = [(barYieldCurvature,barYieldMoment), (curvatureEffective,momentEffictive),
                      (momentMaxCurvature,momentMaxMoment), (ultimateCurvature,ultimateMoment)]
            colors = ['green','blue','purple','red']
            labels = ['yield point', 'effective point', 'maximum point', 'ultimate point']
            #########################################
            ###########################################
            mcCurveAx.plot(blinerX,blinerY,c='k',linewidth=1)
            [mcCurveAx.scatter(x,y,color=color,label=label,s=100) for (x,y),color,label in zip(points,colors,labels)]
            mcCurveAx.legend()
        mcCurveCanvans.draw()
########################################################################################################################
########################################################################################################################

########################################################################################################################
########################################################################################################################
class MCAnalysisResultDB(object):
    """Save the moment curvature analysis results to HDF5 database"""
    def __init__(self,dbPath,sectName):
        """"""
        self.dbPath = dbPath
        self.sectName = sectName
        resultPath = self.dbPath + "/MCAnalysisResult/"
        self.resultFileName = resultPath + sectName+".h5"

    def initDB(self):
        """Initialize the database"""
        resultPath=self.dbPath+"/MCAnalysisResult/"
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        if os.path.exists(self.resultFileName):
            os.remove(self.resultFileName)
        with h5py.File(self.resultFileName, 'w') as f:
            pass

    @classmethod
    def dataSetsInGroup(cls,dbPath,groupName):
        """"""
        with h5py.File(dbPath, 'r') as f:
            if groupName in f:
                group=f[groupName]
                datasets=list(group.keys())
                return datasets
            else:
                print(f"Group {groupName} does not exist.")
                return None
    @classmethod
    def partialMatchGroups(cls,dbPath,partialGroupName):
        """"""
        with h5py.File(dbPath, 'r') as f:
            matching_groups = []
            for group_name in f.keys():
                partialName=f"{partialGroupName}*"
                if fnmatch.fnmatch(group_name,partialName):
                    matching_groups.append(group_name)
            return matching_groups

    @classmethod
    def partialMatchDataSets(cls,dbPath,groupName,partialDataSetName):
        """"""
        with h5py.File(dbPath, 'r') as f:
            group = f[groupName]
            partial_name = f'{partialDataSetName}*'
            matching_datasets = []
            for name, item in group.items():
                if isinstance(item, h5py.Dataset):
                    if fnmatch.fnmatch(name, partial_name):
                        matching_datasets.append(name)
            return matching_datasets

    @classmethod
    def deleteData(cls,dbPath,dataSetName):
        """"""
        with h5py.File(dbPath, 'a') as f:
            if dataSetName in f:
                del f[dataSetName]

    def saveResult(self,dataName,resultsList,headNameList,operationIndexStr='replace'):
        """
        ---A general save template for hdf5 database ---
        Save results to database, resultsList=[[result0_0,result0_1,],[],...]
        headNameList=[headName_0,headName_1,...]
        dataName(str)
        operationIndexStr='replace' or 'append'
                          'replace' means replace the data, 'append' means append data after the last row
        """
        if len(resultsList)>0:
            list0 = resultsList[0]
            saveTypeList = []
            typeDict = {"int": "np.int32", "float": "np.float32", "str": "h5py.string_dtype(encoding='utf-8')"}
            saveTypeList=[typeDict["int"] if isinstance(eachValue, (int,np.int64,np.uint64)) else
                typeDict["float"] if isinstance(eachValue, (float, np.float64)) else
                typeDict["str"] if isinstance(eachValue, str) else None  for eachValue in list0]

            dtypeStr = "np.dtype(["
            dtypeStr += ''.join([f"('{headNameList[i1]}',{saveTypeList[i1]})," for i1 in range(len(list0) - 1)])
            dtypeStr += f"('{headNameList[-1]}',{saveTypeList[-1]})])"
            dtype = eval(dtypeStr)
            structured_data = np.zeros(len(resultsList), dtype=dtype)
            for i2 in range(len(headNameList)):
                structured_data[headNameList[i2]] = [each[i2] for each in resultsList]

            with h5py.File(self.resultFileName, 'a') as f:
                dataset = f.get(dataName)
                if dataset is None:
                    dataset = f.create_dataset(dataName, shape=(0,), maxshape=(None,), dtype=dtype,chunks=True,
                                               compression='gzip',compression_opts=9,shuffle=True)
                    new_size = len(resultsList)
                    dataset.resize(new_size, axis=0)
                    dataset[0:new_size] = structured_data
                else:
                    if operationIndexStr == 'replace':
                        del f[dataName]
                        dataset = f.create_dataset(dataName, shape=(0,), maxshape=(None,), dtype=dtype,chunks=True,
                                               compression='gzip',compression_opts=9,shuffle=True)
                        new_size = len(resultsList)
                        dataset.resize(new_size, axis=0)
                        dataset[0:new_size] = structured_data
                    elif operationIndexStr == 'append':
                        original_size = dataset.shape[0]
                        new_size = original_size + len(resultsList)
                        dataset.resize(new_size, axis=0)
                        dataset[original_size:new_size] = structured_data

    @classmethod
    def getResult(cls,dbPath,dataName):
        """
        dataName(str)---multi-level data table name,eg. 'group/dataSetName'
        """
        with h5py.File(dbPath, 'r') as f:
            dataSet = f.get(dataName)
            if dataSet is not None:
                returnList=[]
                [[tempList:=[],[tempList.append(each.decode("utf-8")) if isinstance(each,bytes) else
                                tempList.append(float(each)) if isinstance(each,(np.float32,np.float64)) else
                                tempList.append(int(each)) if isinstance(each,np.int32) else None
                                for  each in eachRow],returnList.append(tempList)]   for eachRow in dataSet[:]]
                return returnList
            else:
                print(f'''table {dataName} doesn't exitst!''')
                return None
########################################################################################################################
########################################################################################################################
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    sectMCInstance=Auxiliary_sectMCAnalyses(None)
    sectMCInstance.show()
    sys.exit(app.exec())