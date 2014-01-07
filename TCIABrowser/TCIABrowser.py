import urllib2, urllib,sys, os
import string, json, zipfile, os.path
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# TCIABrowser
#

class TCIABrowser:
  def __init__(self, parent):
    parent.title = "TCIABrowser" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Jean-Christophe Fillion-Robin (Kitware), Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.  and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['TCIABrowser'] = self.runTest

  def runTest(self):
    tester = TCIABrowserTest()
    tester.runTest()

#
# qTCIABrowserWidget
#

class TCIABrowserWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
      
    self.previousCollectionsIndex = -1
    self.previousPatientsIndex = -1
    self.previousStudiesIndex = -1

    # setup API key
    keyFile = open('C://Projects//tcia_api_key.txt','r')
    self.apiKey= keyFile.readline()[:-1]
    item = qt.QStandardItem()

    # setup the TCIA client
  
  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "TCIABrowser Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Connect Button
    #
    self.connectButton = qt.QPushButton("Connect")
    self.connectButton.toolTip = "Connect to TCIA Server."
    self.connectButton.enabled = True
    parametersFormLayout.addRow(self.connectButton)

    # 
    # Collections Tree View
    #
    self.collectionsTreeView = qt.QTreeView()
    self.collectionsModel = qt.QStandardItemModel()
    collectionsTreeHeaderLabels = ['Collection Name','Body Part Examined','Modalities','Manufacturers']
    self.collectionsModel.setHorizontalHeaderLabels(collectionsTreeHeaderLabels)
    #header = self.collectionsTreeView.horizontalHeader()
    #header.setStretchLastSection(True)
    self.collectionsTreeView.setModel(self.collectionsModel)
    self.collectionsTreeView.expandAll()
    self.collectionsTreeView.resizeColumnToContents(1)
    parametersFormLayout.addRow(self.collectionsTreeView)
    self.collectionsTreeSelectionModel = self.collectionsTreeView.selectionModel()
    
    
    #self.studyTable = ItemTable(self.parent,headerName='Study Name')
    #self.layout.addWidget(self.studyTable.widget)
    # 
    # Patients Tree View
    #
    self.patientsTreeView = qt.QTreeView()
    self.patientsModel = qt.QStandardItemModel()
    # patientsTreeHeaderLabels = ['Patient ID','Patient Name','Patient BirthDate','Patient Sex','Ethnic Group','Collection']
    self.patientsTreeHeaderLabels = ['Patient ID','Patient Name','Patient BirthDate','Patient Sex','Ethnic Group']
    self.patientsModel.setHorizontalHeaderLabels(self.patientsTreeHeaderLabels)
    self.patientsTreeView.setModel(self.patientsModel)
    self.patientsTreeView.expandAll()
    self.patientsTreeView.resizeColumnToContents(1)
    parametersFormLayout.addRow(self.patientsTreeView)
    self.patientsTreeSelectionModel = self.patientsTreeView.selectionModel()

    # 
    # Studies Tree View
    #
    self.studiesTreeView = qt.QTreeView()
    self.studiesModel = qt.QStandardItemModel()
    self.studiesTreeHeaderLabels = ['Study Instance UID','Study Date','Study Description','Admitting Diagnosis Descrition','Study ID','Patient Age','Series Count']
    self.studiesModel.setHorizontalHeaderLabels(self.studiesTreeHeaderLabels)
    self.studiesTreeView.setModel(self.studiesModel)
    self.studiesTreeView.expandAll()
    self.studiesTreeView.resizeColumnToContents(1)
    parametersFormLayout.addRow(self.studiesTreeView)
    self.studiesTreeSelectionModel = self.studiesTreeView.selectionModel()

    # 
    # Series Tree View
    #
    self.seriesTreeView = qt.QTreeView()
    self.seriesModel = qt.QStandardItemModel()
    self.seriesTreeHeaderLabels = ['Series Instance UID','Modality','Protocol Name','Series Date','Series Description','Body Part Examined','Series Number','Annotation Flag','Manufacturer','Manufacturer Model Name','Software Versions','Image Count']
    self.seriesModel.setHorizontalHeaderLabels(self.seriesTreeHeaderLabels)
    self.seriesTreeView.setModel(self.seriesModel)
    self.seriesTreeView.expandAll()
    self.seriesTreeView.resizeColumnToContents(1)
    parametersFormLayout.addRow(self.seriesTreeView)
    self.seriesTreeSelectionModel = self.studiesTreeView.selectionModel()

    #
    # Request Button
    #
    self.requestButton = qt.QPushButton("Request")
    self.requestButton.toolTip = "Request the selected items from server."
    self.requestButton.enabled = True
    parametersFormLayout.addRow(self.requestButton)

    #
    # Load Button
    #
    self.loadButton = qt.QPushButton("Download and Load")
    self.loadButton.toolTip = "Download the selected sereies and load in Slicer scene."
    self.loadButton.enabled = True
    parametersFormLayout.addRow(self.loadButton)

    # connections
    self.connectButton.connect('clicked(bool)', self.onConnectButton)
    self.requestButton.connect('clicked(bool)', self.onRequestButton)
    self.loadButton.connect('clicked(bool)', self.onLoadButton)
    # collectionsTreeSelectionModel.connect('selectionChanged(const QItemSelection & selected, const QItemSelection & deselected)',self.onSelectionChanged)
    # self.retrieveButton.connect('clicked(bool)', self.onRetrieveButton)
    

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onConnectButton(self):
    logic = TCIABrowserLogic()
    # Instantiate TCIAClient object
    self.tcia_client = TCIAClient(self.apiKey, baseUrl = "https://services.cancerimagingarchive.net/services/TCIA/TCIA/query")  # Set the API-Key
    try:    
      response = self.tcia_client.get_collection_values()
      # self.tcia_client.printServerResponse(response)
      responseString = response.read()[:]
      self.populateCollectionsTreeView(responseString)
    except urllib2.HTTPError, err:
      print "Error executing program:\nError Code: ", str(err.code) , "\nMessage: " , err.read()

  def onRequestButton(self):
    print "onRequestButton"
    currentCollectionsIndex = self.collectionsTreeSelectionModel.currentIndex().row() 
    currentPatientsIndex = self.patientsTreeSelectionModel.currentIndex().row() 
    currentStudiesIndex = self.studiesTreeSelectionModel.currentIndex().row() 
    
    if self.previousCollectionsIndex != currentCollectionsIndex:
      self.previousCollectionsIndex = currentCollectionsIndex
      print "populate patient"
      selectedCollection = self.collectionsItems[currentCollectionsIndex].text()
      try:    
        response = self.tcia_client.get_patient(collection = selectedCollection)
        # self.tcia_client.printServerResponse(response)
        responseString = response.read()[:]
        self.populatePatientsTreeView(responseString)
      except urllib2.HTTPError, err:
        print "Error executing program:\nError Code: ", str(err.code) , "\nMessage: " , err.read()
    elif self.previousPatientsIndex != currentPatientsIndex:
      self.previousPatientsIndex = currentPatientsIndex
      print "populate studies"
      selectedPatient = self.patientsIDs[currentPatientsIndex].text()
      try:    
        response = self.tcia_client.get_patient_study(patientId = selectedPatient)
        # self.tcia_client.printServerResponse(response)
        responseString = response.read()[:]
        self.populateStudiesTreeView(responseString)
      except urllib2.HTTPError, err:
        print "Error executing program:\nError Code: ", str(err.code) , "\nMessage: " , err.read()
    elif self.previousStudiesIndex != currentStudiesIndex:
      self.previousStudiesIndex = currentStudiesIndex
      print "populate series"
      selectedStudy = self.studyInstanceUIDs[currentStudiesIndex].text()
      try:    
        response = self.tcia_client.get_series(studyInstanceUID = selectedStudy)
        # self.tcia_client.printServerResponse(response)
        responseString = response.read()[:]
        self.populateSeriesTreeView(responseString)
      except urllib2.HTTPError, err:
        print "Error executing program:\nError Code: ", str(err.code) , "\nMessage: " , err.read()

  def onLoadButton(self):
    print "onLoadButton"
    currentSeriesIndex = self.seriesTreeSelectionModel.currentIndex().row() 
    selectedSeries = self.seriesInstanceUIDs[currentSeriesIndex].text()
    # Get Image request
    dicomAppWidget = ctk.ctkDICOMAppWidget()
    databaseDirectory = dicomAppWidget.databaseDirectory
    tempPath = databaseDirectory + "/incoming/"
    fileName = tempPath + str(selectedSeries) + ".zip"
    imagesDirectory = tempPath + str(selectedSeries)
    try:
      response = self.tcia_client.get_image(seriesInstanceUid = selectedSeries );
      # Save server response as images.zip in current directory
      if response.getcode() == 200:
        print "\n" + str(response.info())
        bytesRead = response.read()
        fout = open(fileName, "wb")
        fout.write(bytesRead)
        fout.close()
        print "\nDownloaded file %s.zip from the server" %fileName
      else:
        print "Error : " + str(response.getcode) # print error code
        print "\n" + str(response.info())
    except urllib2.HTTPError, err:
      print "Error executing program:\nError Code: ", str(err.code) , "\nMessage: " , err.read()

    # Unzip the data
    self.unzip(fileName,imagesDirectory)
    # Import the data into dicomAppWidget and open the dicom browser
    dicomAppWidget.onImportDirectory(imagesDirectory)
    slicer.util.selectModule('DICOM')

  def unzip(self,source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
      for member in zf.infolist():
        words = member.filename.split('/')
        path = dest_dir
        for word in words[:-1]:
          drive, word = os.path.splitdrive(word)
          head, word = os.path.split(word)
          if word in (os.curdir, os.pardir, ''): continue
          path = os.path.join(path, word)
        zf.extract(member, path)

  def populateCollectionsTreeView(self,responseString):
    collections = json.loads(responseString)
    root = self.collectionsModel.invisibleRootItem()
    n = 0
    self.collectionsItems =[]
    for collection in collections:
      item = qt.QStandardItem(str(collections[n]['Collection']))
      self.collectionsItems.append(item)
      root.appendRow(item)
      n +=1

  def populatePatientsTreeView(self,responseString):
    self.clearPatientsTreeView()
    self.clearStudiesTreeView()
    self.clearSeriesTreeView()
    model = self.patientsModel
    # patientsTreeHeaderLabels = ['Patient ID','Patient Name','Patient Sex','Collection']
    model.setHorizontalHeaderLabels(self.patientsTreeHeaderLabels)
    self.studiesModel.setHorizontalHeaderLabels(self.studiesTreeHeaderLabels)
    self.seriesModel.setHorizontalHeaderLabels(self.seriesTreeHeaderLabels)
    patients = json.loads(responseString)
    
    n = 0
    for patient in patients:
      keys = patient.keys()
      for key in keys:
        if key == 'PatientID':
          patientID = qt.QStandardItem(str(patient['PatientID']))
          self.patientsIDs.append(patientID)
          model.setItem(n,0,patientID)
        if key == 'PatientName':
          patientName = qt.QStandardItem(str(patient['PatientName']))
          self.patientNames.append(patientName)
          model.setItem(n,1,patientName )
        if key == 'PatientBirthDate':
          patientBirthDate= qt.QStandardItem(str(patient['PatientBirthDate']))
          self.patientBirthDates.append(patientBirthDate)
          model.setItem(n,2,patientBirthDate)
        if key == 'PatientSex':
          patientSex = qt.QStandardItem(str(patient['PatientSex']))
          self.patientSexes.append(patientSex)
          model.setItem(n,3,patientSex)
        if key == 'EthnicGroup':
          ethnicGroup= qt.QStandardItem(str(patient['EthnicGroup']))
          self.ethnicGroups.append(ethnicGroup)
          model.setItem(n,4,ethnicGroup)
      n += 1

  def populateStudiesTreeView(self,responseString):
    self.clearStudiesTreeView()
    self.clearSeriesTreeView()
    model = self.studiesModel
    model.setHorizontalHeaderLabels(self.studiesTreeHeaderLabels)
    self.seriesModel.setHorizontalHeaderLabels(self.seriesTreeHeaderLabels)
    studies = json.loads(responseString)
    n = 0
    for study in studies:
      keys = study.keys()
      for key in keys:
        if key == 'StudyInstanceUID':
          studyInstanceUID= qt.QStandardItem(str(study['StudyInstanceUID']))
          self.studyInstanceUIDs.append(studyInstanceUID)
          model.setItem(n,0,studyInstanceUID)
        if key == 'StudyDate':
          studyDate = qt.QStandardItem(str(study['StudyDate']))
          self.studyDates.append(studyDate)
          model.setItem(n,1,studyDate)
        if key == 'StudyDescription':
          studyDescription = qt.QStandardItem(str(study['StudyDescription']))
          self.studyDescriptions.append(studyDescription)
          model.setItem(n,2,studyDescription)
        if key == 'AdmittingDiagnosesDescriptions':
          admittingDiagnosesDescription= qt.QStandardItem(str(study['AdmittingDiagnosesDescriptions']))
          self.admittingDiagnosesDescriptions.append(admittingDiagnosesDescription)
          model.setItem(n,3,admittingDiagnosesDescription)
        if key == 'StudyID':
          studyID= qt.QStandardItem(str(study['StudyID']))
          self.studyIDs.append(studyID)
          model.setItem(n,4,studyID)
        if key == 'PatientAge':
          patientAge = qt.QStandardItem(str(study['PatientAge']))
          self.patientAges.append(patientAge)
          model.setItem(n,5,patientAge)
        if key == 'SeriesCount':
          seriesCount = qt.QStandardItem(str(study['SeriesCount']))
          self.seriesCounts.append(seriesCount)
          model.setItem(n,6,seriesCount)
      n += 1

  def populateSeriesTreeView(self,responseString):
    self.clearSeriesTreeView()
    model = self.seriesModel
    model.setHorizontalHeaderLabels(self.seriesTreeHeaderLabels)
    seriesCollection = json.loads(responseString)
    n = 0
    for series in seriesCollection:
      keys = series.keys()
      for key in keys:
        if key == 'SeriesInstanceUID':
          print "key found"
          seriesInstanceUID = qt.QStandardItem(str(series['SeriesInstanceUID']))
          self.seriesInstanceUIDs.append(seriesInstanceUID)
          print seriesInstanceUID
          model.setItem(n,0,seriesInstanceUID)
        if key == 'Modality':
          modality = qt.QStandardItem(str(series['Modality']))
          self.modalities.append(modality)
          model.setItem(n,1,modality)
        if key == 'ProtocolName':
          protocolName = qt.QStandardItem(str(series['ProtocolName']))
          self.protocolNames.append(protocolName)
          model.setItem(n,2,protocolName)
        if key == 'SeriesDate':
          seriesDate = qt.QStandardItem(str(series['SeriesDate']))
          self.seriesDates.append(seriesDate)
          model.setItem(n,3,seriesDate)
        if key == 'SeriesDescription':
          seriesDescription = qt.QStandardItem(str(series['SeriesDescription']))
          self.seriesDescriptions.append(seriesDescription)
          model.setItem(n,4,seriesDescription)
        if key == 'BodyPartExamined':
          bodyPartExamined = qt.QStandardItem(str(series['BodyPartExamined']))
          self.bodyPartsExamined.append(bodyPartExamined)
          model.setItem(n,5,bodyPartExamined)
        if key == 'SeriesNumber':
          seriesNumber = qt.QStandardItem(str(series['SeriesNumber']))
          self.seriesNumbers.append(seriesNumber)
          model.setItem(n,6,seriesNumber)
        if key == 'AnnotationsFlag':
          annotationsFlag = qt.QStandardItem(str(series['AnnotationsFlag']))
          self.annotationsFlags.append(annotationsFlag)
          model.setItem(n,7,annotationsFlag)
        if key == 'Manufacturer':
          manufacturer = qt.QStandardItem(str(series['Manufacturer']))
          self.manufacturers.append(manufacturer)
          model.setItem(n,8,manufacturer)
        if key == 'ManufacturerModelName':
          manufacturerModelName = qt.QStandardItem(str(series['ManufacturerModelName']))
          self.manufacturerModelNames.append(manufacturerModelName )
          model.setItem(n,9,manufacturerModelName)
        if key == 'SoftwareVersions':
          softwareVersions = qt.QStandardItem(str(series['SoftwareVersions']))
          self.softwareVersionsCollection.append(softwareVersions )
          model.setItem(n,10,softwareVersions)
        if key == 'ImageCount':
          imageCount = qt.QStandardItem(str(series['ImageCount']))
          self.imageCounts.append(imageCount )
          model.setItem(n,11,imageCount )
      n += 1

  def clearPatientsTreeView(self):
    model = self.patientsModel
    # patientsTreeHeaderLabels = ['Patient ID','Patient Name','Patient Sex','Collection']
    model.setHorizontalHeaderLabels(self.patientsTreeHeaderLabels)
    self.patientsIDs =[]
    self.patientNames = []
    self.patientBirthDates = []
    self.patientSexes = []
    self.ethnicGroups = []
    #self.collections = []
    model.clear()

  def clearStudiesTreeView(self):
    model = self.studiesModel
    model.setHorizontalHeaderLabels(self.studiesTreeHeaderLabels)
    self.studyInstanceUIDs =[]
    self.studyDates = []
    self.studyDescriptions = []
    self.admittingDiagnosesDescriptions = []
    self.studyIDs = []
    self.patientAges = []
    self.seriesCounts = []
    model.clear()

  def clearSeriesTreeView(self):
    model = self.seriesModel
    model.setHorizontalHeaderLabels(self.seriesTreeHeaderLabels)
    self.seriesInstanceUIDs= []
    self.modalities = []
    self.protocolNames = []
    self.seriesDates = []
    self.seriesDescriptions = []
    self.bodyPartsExamined = []
    self.seriesNumbers =[]
    self.annotationsFlags = []
    self.manufacturers = []
    self.manufacturerModelNames = []
    self.softwareVersionsCollection = []
    self.imageCounts = []
    #self.collections = []
    model.clear()

  def onReload(self,moduleName="TCIABrowser"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer
    import urllib2, urllib,sys, os
    import string, json
    import zipfile, os.path


    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

  def onReloadAndTest(self,moduleName="TCIABrowser"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# TCIABrowserLogic
#

class TCIABrowserLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == -1:
      # full window
      widget = slicer.util.mainWindow()
    elif type == slicer.qMRMLScreenShotDialog().FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog().ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog().Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog().Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog().Green:
      # green slice window
      widget = lm.sliceWidget("Green")

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self,inputVolume,outputVolume,enableScreenshots=0,screenshotScaleFactor=1):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('TCIABrowser-Start','Start',-1)

    return True


class TCIABrowserTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TCIABrowser1()

  def test_TCIABrowser1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TCIABrowserLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')



#
# Refer https://wiki.cancerimagingarchive.net/display/Public/REST+API+Usage+Guide for complete list of API
#
class TCIAClient:
    GET_IMAGE = "getImage"
    GET_MANUFACTURER_VALUES = "getManufacturerValues"
    GET_MODALITY_VALUES = "getModalityValues"
    GET_COLLECTION_VALUES = "getCollectionValues"
    GET_BODY_PART_VALUES = "getBodyPartValues"
    GET_PATIENT_STUDY = "getPatientStudy"
    GET_SERIES = "getSeries"
    GET_PATIENT = "getPatient"
    
    def __init__(self, apiKey , baseUrl):
        self.apiKey = apiKey
        self.baseUrl = baseUrl
        
    def execute(self, url, queryParameters={}):
        # pop up progress dialog to prevent user from messing around
        self.progress = qt.QProgressDialog(slicer.util.mainWindow())
        self.progress.minimumDuration = 0
        self.progress.show()
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        self.progress.setCancelButton(0)
        self.progress.setWindowModality(2)
        self.progress.setLabelText('Communicating with TCIA Server')
        slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
        self.progress.repaint()
        
        queryParameters = dict((k, v) for k, v in queryParameters.iteritems() if v)
        headers = {"api_key" : self.apiKey }
        queryString = "?%s" % urllib.urlencode(queryParameters)
        requestUrl = url + queryString
        request = urllib2.Request(url=requestUrl , headers=headers)
        resp = urllib2.urlopen(request)
        
        self.progress.close()
        return resp
    
    def get_modality_values(self,collection = None , bodyPartExamined = None , modality = None , outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_MODALITY_VALUES
        queryParameters = {"Collection" : collection , "BodyPartExamined" : bodyPartExamined , "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    
    def get_manufacturer_values(self,collection = None , bodyPartExamined = None , modality = None , outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_MANUFACTURER_VALUES
        queryParameters = {"Collection" : collection , "BodyPartExamined" : bodyPartExamined , "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
        
    def get_collection_values(self,outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_COLLECTION_VALUES
        queryParameters = { "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
        
    def get_body_part_values(self,collection = None , bodyPartExamined = None , modality = None , outputFormat = "csv" ):
        serviceUrl = self.baseUrl + "/" + self.GET_BODY_PART_VALUES
        queryParameters = {"Collection" : collection , "BodyPartExamined" : bodyPartExamined , "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    def get_patient_study(self,collection = None , patientId = None , studyInstanceUid = None , outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_PATIENT_STUDY
        queryParameters = {"Collection" : collection , "PatientID" : patientId , "StudyInstanceUID" : studyInstanceUid , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    def get_series(self,collection = None , patientId = None , studyInstanceUID = None, modality = None , outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_SERIES
        queryParameters = {"Collection" : collection , "PatientID" : patientId ,"StudyInstanceUID": studyInstanceUID, "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    def get_patient(self,collection = None , outputFormat = "json" ):
        serviceUrl = self.baseUrl + "/" + self.GET_PATIENT
        queryParameters = {"Collection" : collection , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    def get_image(self , seriesInstanceUid):
        serviceUrl = self.baseUrl + "/" + self.GET_IMAGE
        queryParameters = { "SeriesInstanceUID" : seriesInstanceUid }
        resp = self.execute( serviceUrl , queryParameters)
        return resp

    def printServerResponse(self, response):
      if response.getcode() == 200:
        print "Server Returned:\n"
        print response.read()
        print "\n"
      else:
        print "Error : " + str(response.getcode) # print error code
