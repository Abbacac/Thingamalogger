import sys, os, json
from enum import Enum, Flag, auto
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QPixmap, QCloseEvent
from PyQt6.QtCore import Qt, QTimer, QTime, QSize, QSettings
from pygame import mixer




# Enmums and Flag
ORGANIZATION_NAME = 'Abbacac'
APP_NAME = 'Eternity Egg ID Cataloger'

FILENAME_PLAYERSTATEJSON = 'PlayerState.json'
FILENAME_HEADERJSON = 'Header.json'
FILENAME_WORLDSTATEJSON = 'WorldState.json'

FILENAME_CONFIG_JSON = 'config.json'


ARGS_RESET_SETTINGS = '--reset_settings'

SETTINGS_GEOMETRY = 'geometry'
SETTINGS_TOGGLED_BUTTONS = 'toggledButtons'

KEY_NAME = 'name'
KEY_ID = 'id'
KEY_DESCRIPTION = 'description'

FILEPATH_IDENTIFIERS = 'identifiers.json'

CURRENT_CONFIG_VERSION = '1.0'
CONFIG_VERSION = 'version'
CONFIG_GAME_SAVE_DIRECTORY = 'gameSaveDirectory'
CONFIG_VOLUME = 'volume'
CONFIG_AUTOSCROLL = 'autoscroll'
CONFIG_REFRESH_INTERVAL = 'refreshInterval'

STRING_TRUE = 'True'
STRING_FALSE = 'False'

class JsonCategory(Enum):
    ITEMS = 'itemIds'
    CHECKPOINTS = 'visitedCheckpointIds'
    CHAOS_CORES = 'collectedChaosCoreIds'
    FAIRYS = 'collectedFairyIds'
    PARASITES = 'collectedEntropicParasiteIds'
    DEMON_HEARTS = 'collectedDemonHeartIds'
    
    NPCS = 'npcIds'
    ENEMIES = 'enemyIds'
    
    CHECKPOINT_NAME = 'activeCheckpointName'
    LOCATION_NAME = 'activeLocationName'

    INIT = 'init' # currently only used to get a file path


# Functions
def categoryToImagePath(category: JsonCategory) -> Path:
    match category:            
        case JsonCategory.INIT:
            return Path('icons/Init.png')
        case JsonCategory.ITEMS:
            return Path('icons/Item.png')
        case JsonCategory.CHECKPOINTS:
            return Path('icons/Checkpoint.png')
        case JsonCategory.CHAOS_CORES:
            return Path('icons/ChaosCore.png')
        case JsonCategory.FAIRYS:
            return Path('icons/Fairy.png')
        case JsonCategory.PARASITES:
            return Path('icons/EntropicParasite.png')
        case JsonCategory.DEMON_HEARTS:
            return Path('icons/DemonHeart.png')
        case JsonCategory.NPCS:
            return Path('icons/NPC.png')
        case JsonCategory.ENEMIES:
            return Path('icons/Enemy.png')
            
        case _:
            print(f'categoryToImagePath: Type {category} is invalid!')
            return Path('icons/WIP.png')


def categoryToImageLabel(category: JsonCategory, parent:QWidget = None) -> QLabel:
    pixmap = QPixmap(str(categoryToImagePath(category)))
    label = QLabel(parent)
    label.setPixmap(pixmap.scaled(32, 32))
    return label


def categoryDescription(category: JsonCategory) -> str:
    match category:
        case JsonCategory.INIT:
            return 'Initialized on Load'
        case JsonCategory.ITEMS:
            return 'Demon Heart'
        case JsonCategory.CHECKPOINTS:
            return 'Entropic Parasite'
        case JsonCategory.CHAOS_CORES:
            return 'Chaos Core'
        case JsonCategory.FAIRYS:
            return 'Fairy'
        case JsonCategory.PARASITES:
            return 'Item'
        case JsonCategory.DEMON_HEARTS:
            return 'Checkpoint'
        case JsonCategory.NPCS:
            return 'NPC'
        case JsonCategory.ENEMIES:
            return 'Enemy'
        case _:
            print(f'categoryDescription: Type {category} is invalid!')
            return 'Unknown'


# Widget Classes
class SortingButton(QPushButton):
    def __init__(self, parent, category:JsonCategory=None):
        super().__init__(parent)
        
        self.category = category
        
        BUTTON_SIZE = 64
        ICON_SIZE = 64

        self.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self.setCheckable(True)
        self.setChecked(True)
        self.setIcon(QIcon(str(categoryToImagePath(self.category))))
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.setToolTip(categoryDescription(self.category))



class ListIDItemWidget(QWidget):
    modificationsMade = False
    amountBeingEdited = 0
    
    def __init__(self, category: JsonCategory, id: str, name: str, description:str, initFlag: bool):
        super().__init__()

        # Variables
        self.category = category
        self.id = id
        self.name = name
        self.date = QTime.currentTime().toString('hh:mm:ss')
        self.description = description
        self.frame = MainWindow.frameCount
        self.initFlag = initFlag
        
        # Widgets
        self.imageLabel = categoryToImageLabel(self.category, parent = self)
        self.idLabel = QLabel(self.id, self)
        self.nameLabel = QLabel(self.name, self)
        self.nameLineEdit = QLineEdit(self.name, self)
        self.descriptionLabel = QLabel(self.description, self)
        self.descriptionLineEdit = QLineEdit(self.description, self)
        self.createdLabel = QLabel(self.date + (' INIT' if initFlag else ''))
        
        # Styling
        self.nameLineEdit.hide()
        self.descriptionLineEdit.hide()

        # Layout
        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        mainLayout.addWidget(self.imageLabel)
        
        labelLayout = QVBoxLayout()
        labelLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        labelLayout.addWidget(self.idLabel)
        labelLayout.addWidget(self.nameLabel)
        labelLayout.addWidget(self.nameLineEdit)
        labelLayout.addWidget(self.descriptionLabel)
        labelLayout.addWidget(self.descriptionLineEdit)
        labelLayout.addWidget(self.createdLabel)
        mainLayout.addLayout(labelLayout)

        self.setLayout(mainLayout)
        
        # Connections
        self.nameLineEdit.returnPressed.connect(self.finishedEditing)
        self.descriptionLineEdit.returnPressed.connect(self.finishedEditing)
        
    def showLineEdits(self):
        ListIDItemWidget.amountBeingEdited += 1
        
        self.nameLabel.hide()
        self.descriptionLabel.hide()
        self.nameLineEdit.show()
        self.descriptionLineEdit.show()
        
    def hideLineEdits(self):
        ListIDItemWidget.amountBeingEdited -= 1
        
        self.nameLabel.show()
        self.descriptionLabel.show()
        self.nameLineEdit.hide()
        self.descriptionLineEdit.hide()
        
        
    def mouseDoubleClickEvent(self, a0):
        super().mouseDoubleClickEvent(a0)
        if not self.nameLineEdit.isHidden(): return
        self.showLineEdits()
        
    def finishedEditing(self):
        if self.nameLineEdit.isHidden(): return
        
        self.name = self.nameLineEdit.text()
        self.description = self.descriptionLineEdit.text()
        
        self.nameLabel.setText(self.name)
        self.descriptionLabel.setText(self.description)
        
        ListIDItemWidget.modificationsMade = True
        self.hideLineEdits()
        
        
class Sidebar(QWidget):
    def __init__(self, parent, config:dict):
        super().__init__(parent)
        
        # Enums
        OPTIONS_TITLE_SPACING = 30
        OPTIONS_SEPERATOR_SPACING = 10
        VOLUME_SLIDER_MAX_HEIGHT = 100
        VOLUME_SLIDER_MIN = 0
        VOLUME_SLIDER_MAX = 100
        
        # Widgets
        self.optionsLabel = QLabel('Options', self)
        self.volumeLabel = QLabel('Volume', self)
        self.volumeSlider = QSlider(self)
        self.refreshintervalLabel = QLabel('Json Refresh Interval', self)
        self.refreshintervalSpinBox = QSpinBox(self)
        self.autoscrollButton = QPushButton('Toggle Autoscrolling', self)
                
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.optionsLabel)
        layout.addSpacing(OPTIONS_TITLE_SPACING)
        layout.addWidget(self.volumeLabel)
        layout.addWidget(self.volumeSlider)
        layout.addSpacing(OPTIONS_SEPERATOR_SPACING)
        layout.addWidget(self.refreshintervalLabel)
        layout.addWidget(self.refreshintervalSpinBox)
        layout.addSpacing(OPTIONS_SEPERATOR_SPACING)
        layout.addWidget(self.autoscrollButton)
        layout.addStretch()     # adds spacing so everythings stuck to the top area
        self.setLayout(layout)
        self.config = config
        
        # Styling
        self.hide()
        self.optionsLabel.setStyleSheet("""
        font-size: 16px;
        font-weight: bold;
                                        """)
        self.volumeSlider.setFixedHeight(VOLUME_SLIDER_MAX_HEIGHT)
        self.volumeSlider.setRange(VOLUME_SLIDER_MIN, VOLUME_SLIDER_MAX)
        self.volumeSlider.setSliderPosition(int(self.config[CONFIG_VOLUME]))
        self.refreshintervalSpinBox.setValue(int(self.config[CONFIG_REFRESH_INTERVAL]))
        self.autoscrollButton.setCheckable(True)
        self.autoscrollButton.setChecked(
            True if self.config[CONFIG_AUTOSCROLL] == STRING_TRUE else False
        )
        
        # Connections
        self.volumeSlider.sliderMoved.connect(self.volumeChanged)
        self.autoscrollButton.clicked.connect(self.autoscrollButtonClicked)
        
        
    def volumeChanged(self):
        self.config[CONFIG_VOLUME] = str(self.volumeSlider.value())
        mixer.music.set_volume(round(int(self.config[CONFIG_VOLUME]) / 100, 1))
        
    def autoscrollButtonClicked(self):
        if self.autoscrollButton.isChecked():
            self.config[CONFIG_AUTOSCROLL] = STRING_TRUE
        else:
            self.config[CONFIG_AUTOSCROLL] = STRING_FALSE
        
        


class MainWindow(QMainWindow):
    frameCount = 0
    editing = False
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Thingamalogger: Eternity Egg ID Cataloger')
        self.setWindowIcon(QIcon('icons/appIcon.ico'))
        
        # SFX
        mixer.init()
        SOUND_NEWID = 'sfx/Well.wav'
        mixer.music.load(SOUND_NEWID)
        
        # Variables
        self.playerStateJson: Path = None
        self.headerJson: Path = None
        self.worldStateJson: Path = None
        self.loadedDirectoryFrame = 0
        self.identifiers = self.loadIdentifiers()
        self.config = None
        self.loadConfig()

        self.checkpoint: str = None
        self.location: str = None

        self.ids: dict[JsonCategory, list] = {
            JsonCategory.ITEMS.value: [],
            JsonCategory.CHECKPOINTS.value: [],
            JsonCategory.CHAOS_CORES.value: [],
            JsonCategory.FAIRYS.value: [],
            JsonCategory.PARASITES.value: [],
            JsonCategory.DEMON_HEARTS.value: []
        }
        
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        
        
        # Timers
        self.frameCountTimer = QTimer()
        FRAME_COUNT_UPDATE_INTERVAL = 10
        self.frameCountTimer.start(FRAME_COUNT_UPDATE_INTERVAL)
        def incrementFrameCount():
            MainWindow.frameCount += 1
        self.frameCountTimer.timeout.connect(incrementFrameCount)
        
        self.jsonUpdateInverval = int(self.config[CONFIG_REFRESH_INTERVAL])
        self.jsonUpdateTimer = QTimer()
        self.jsonUpdateTimer.timeout.connect(self.updateList)
        
        self.updateIntervalCrashcheckTimer = QTimer()
        def writeRefreshInterval():
            refreshInterval = str(self.sidebar.refreshintervalSpinBox.value())
            self.config[CONFIG_REFRESH_INTERVAL] = refreshInterval
            self.updateIntervalCrashcheckTimer.stop()
            print('new refresh interval is sane!')
        self.updateIntervalCrashcheckTimer.timeout.connect(writeRefreshInterval)
        
        
        # SFX Volume update
        mixer.music.set_volume(round(int(self.config[CONFIG_VOLUME]) / 100, 1))
        
        
        # Widgets
        self.sortInitButton = SortingButton(self, JsonCategory.INIT)
        self.sortDemonHeartsButton = SortingButton(self, JsonCategory.DEMON_HEARTS)
        self.sortEntropicParasitesButton = SortingButton(self, JsonCategory.PARASITES)
        self.sortChaosCoresButton = SortingButton(self, JsonCategory.CHAOS_CORES)
        self.sortFariesButton = SortingButton(self, JsonCategory.FAIRYS)
        self.sortItemsButton = SortingButton(self, JsonCategory.ITEMS)
        self.sortCheckpointsButton = SortingButton(self, JsonCategory.CHECKPOINTS)
        self.sortNpcsButton = SortingButton(self, JsonCategory.NPCS)
        self.sortEnemiesButton = SortingButton(self, JsonCategory.ENEMIES)
        self.sortButtons:tuple[SortingButton] = (
            self.sortInitButton,
            self.sortDemonHeartsButton,
            self.sortEntropicParasitesButton,
            self.sortChaosCoresButton,
            self.sortFariesButton,
            self.sortItemsButton,
            self.sortCheckpointsButton,
            self.sortNpcsButton,
            self.sortEnemiesButton
        )

        self.idList = QListWidget()
        self.saveButton = QPushButton('Save Identifiers')
        self.loadDirectoryButton = QPushButton('Load Save Directory')
        self.loadPreviousDirectoryButton = QPushButton('Load Previous Save Directory')
        
        self.showOptionsButton = QPushButton('Toggle Options Sidebar')
        self.sidebar = Sidebar(self, self.config)
        
        # Styling
        if not self.config[CONFIG_GAME_SAVE_DIRECTORY]:
            self.loadPreviousDirectoryButton.setEnabled(False)
        self.initLayout()
        

        # Connections
        self.loadDirectoryButton.clicked.connect(self.loadDirectory)
        self.saveButton.clicked.connect(self.saveIdentifiers)
        self.loadPreviousDirectoryButton.clicked.connect(self.loadPreviousDirectory)
        
        for button in self.sortButtons:
            button.clicked.connect(self.updateFilters)
            
        self.showOptionsButton.clicked.connect(self.toggleOptionsSidebar)
        
        self.sidebar.refreshintervalSpinBox.valueChanged.connect(self.refreshIntervalChanged)
        
            
            
    def initLayout(self):
        mainLayout = QHBoxLayout()
        
        catalogerLayout = QVBoxLayout()

        sortingButtonsLayout = QHBoxLayout()
        sortingButtonsLayout.addWidget(self.sortInitButton)
        sortingButtonsLayout.addWidget(self.sortDemonHeartsButton)
        sortingButtonsLayout.addWidget(self.sortEntropicParasitesButton)
        sortingButtonsLayout.addWidget(self.sortChaosCoresButton)
        sortingButtonsLayout.addWidget(self.sortFariesButton)
        sortingButtonsLayout.addWidget(self.sortItemsButton)
        sortingButtonsLayout.addWidget(self.sortCheckpointsButton)
        sortingButtonsLayout.addWidget(self.sortNpcsButton)
        sortingButtonsLayout.addWidget(self.sortEnemiesButton)
        catalogerLayout.addLayout(sortingButtonsLayout)
        
        catalogerLayout.addWidget(self.idList)
        
        bottomButtonBarLayout = QHBoxLayout()
        bottomButtonBarLayout.addWidget(self.saveButton)
        bottomButtonBarLayout.addWidget(self.loadDirectoryButton)
        bottomButtonBarLayout.addWidget(self.loadPreviousDirectoryButton)
        catalogerLayout.addLayout(bottomButtonBarLayout)
        
        catalogerLayout.addWidget(self.showOptionsButton)
        
        mainLayout.addLayout(catalogerLayout)
        mainLayout.addWidget(self.sidebar)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)
        
        self.readQSettings()
        
            
    def toggleOptionsSidebar(self):
        if self.sidebar.isHidden():
            self.sidebar.show()
        else:
            self.sidebar.hide()
            
            
    def refreshIntervalChanged(self):
        self.jsonUpdateTimer.stop()
        self.jsonUpdateTimer.start(self.sidebar.refreshintervalSpinBox.value())
        FRAMES_TIL_SAFETY = 20000
        self.updateIntervalCrashcheckTimer.start(FRAMES_TIL_SAFETY)
                    
        
    def getListWidgetItems(self) -> list[QListWidgetItem]:
        return [self.idList.item(i) for i in range(self.idList.count())]
        
    def getListIDItemWidgets(self) -> list[ListIDItemWidget]:
        listWidgets = self.getListWidgetItems()
        widgets: list[ListIDItemWidget] = [self.idList.itemWidget(w) for w in listWidgets]
        return widgets

        
    def getBlankIdentifierDict(self) -> dict[JsonCategory:list]:
        return {
            JsonCategory.ITEMS.value: [],
            JsonCategory.CHECKPOINTS.value: [],
            JsonCategory.CHAOS_CORES.value: [],
            JsonCategory.FAIRYS.value: [],
            JsonCategory.PARASITES.value: [],
            JsonCategory.DEMON_HEARTS.value: [],
            JsonCategory.NPCS.value: [],
            JsonCategory.ENEMIES.value: []
        }
        
    def saveIdentifiers(self):
        loadedIdentifiers = self.getBlankIdentifierDict()
        widgets = self.getListIDItemWidgets()
        
        for widget in widgets:
            idInfo = {
                KEY_ID: widget.id,
                KEY_NAME: widget.name,
                KEY_DESCRIPTION: widget.description
            }
            loadedIdentifiers[widget.category.value].append(idInfo)


        for category, identifierList in self.identifiers.items():
            for identifierDict in identifierList:
                if not identifierDict[KEY_ID] in [d[KEY_ID] for d in loadedIdentifiers[category]]:
                    loadedIdentifiers[category].append(identifierDict)


        with open(FILEPATH_IDENTIFIERS, 'w', encoding='utf-8') as file:
            json.dump(loadedIdentifiers, file, indent=1)

        ListIDItemWidget.modificationsMade = False
        
        
    def loadIdentifiers(self) -> dict[JsonCategory:list]:
        identifierPath = Path(FILEPATH_IDENTIFIERS)
        if not identifierPath.is_file():
            with open(identifierPath, 'x') as file:
                identifiers = self.getBlankIdentifierDict()
                json.dump(identifiers, file, indent=1)
        
        with open(identifierPath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
        
        
    def loadConfig(self) -> dict:
        if not Path(FILENAME_CONFIG_JSON).is_file(): self.resetConfig()
        
        with open(FILENAME_CONFIG_JSON, 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        
    def resetConfig(self):
        with open(FILENAME_CONFIG_JSON, 'w', encoding='utf-8') as file:
            defaultConfigDict = {
                CONFIG_VERSION: CURRENT_CONFIG_VERSION,
                CONFIG_GAME_SAVE_DIRECTORY: '',
                CONFIG_VOLUME: '75',
                CONFIG_AUTOSCROLL: STRING_TRUE,
                CONFIG_REFRESH_INTERVAL: '10'
            }
            json.dump(defaultConfigDict, file, indent=1)
                
    def saveConfig(self):
        self.config[CONFIG_VOLUME] = '100' if self.config[CONFIG_VOLUME] == '99' else self.config[CONFIG_VOLUME]    # dont ask
        
        if not Path(FILENAME_CONFIG_JSON).is_file(): self.resetConfig()
        
        with open(FILENAME_CONFIG_JSON, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=1)
            
            
    def writeQSettings(self):
        self.settings.setValue(SETTINGS_GEOMETRY, self.saveGeometry())
        toggledButtons:list[JsonCategory] = [button.category for button in self.sortButtons if button.isChecked()]
        self.settings.setValue(SETTINGS_TOGGLED_BUTTONS, toggledButtons)
                
    
    def readQSettings(self):
        if ARGS_RESET_SETTINGS in sys.argv: return
        
        geometry = self.settings.value(SETTINGS_GEOMETRY)
        if geometry: self.restoreGeometry(geometry)
        toggledButtons:list[JsonCategory] = self.settings.value(SETTINGS_TOGGLED_BUTTONS)
        for button in self.sortButtons:
            if not button.category in toggledButtons: button.setChecked(False)
            


    def getGameJsons(self, path: Path):
        for file in path.iterdir():
            if file.name == FILENAME_PLAYERSTATEJSON: self.playerStateJson = file
            elif file.name == FILENAME_HEADERJSON: self.headerJson = file
            elif file.name == FILENAME_WORLDSTATEJSON: self.worldStateJson = file
                    
                    
                    
        couldntFind:list[str] = []
        if not self.playerStateJson:
            couldntFind.append(FILENAME_PLAYERSTATEJSON)
        if not self.headerJson:
            couldntFind.append(FILENAME_HEADERJSON)
        if not self.worldStateJson:
            couldntFind.append(FILENAME_WORLDSTATEJSON)
            
        allIsWell:bool = True if len(couldntFind) <= 0 else False
                
        if not allIsWell:
            messageBox = QMessageBox(self)
            messageBox.setWindowTitle('Directory Error')
            messageBox.setIcon(QMessageBox.Icon.Warning)
            errorText = "Could not find the following files in the given directory:"
            for fileName in couldntFind:
                errorText += f"\n{fileName}"
            messageBox.setText(errorText)
            messageBox.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Abort)
            messageBox.setDefaultButton(QMessageBox.StandardButton.Abort)
            
            result = messageBox.exec()
            if result == QMessageBox.StandardButton.Retry:
                return self.getGameJsons(path)
            else:
                return
            
            
        
        self.jsonUpdateTimer.start(self.jsonUpdateInverval)
        self.loadedDirectoryFrame = self.frameCount
        self.config[CONFIG_GAME_SAVE_DIRECTORY] = str(path)
        self.loadPreviousDirectoryButton.setEnabled(True)

    def loadDirectory(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setDirectory(self.config[CONFIG_GAME_SAVE_DIRECTORY] or None)
        if not dialog.exec(): return
        
        saveDirectory = Path(dialog.selectedFiles()[0])
        self.getGameJsons(saveDirectory)
        
    def loadPreviousDirectory(self):
        if self.config[CONFIG_GAME_SAVE_DIRECTORY]: 
            self.getGameJsons(Path(self.config[CONFIG_GAME_SAVE_DIRECTORY]))
        
        
        
        
    def updateFilters(self) -> list[JsonCategory]:
        shownCategories:list[JsonCategory] = [
                JsonCategory.ITEMS,
                JsonCategory.CHECKPOINTS,
                JsonCategory.CHAOS_CORES,
                JsonCategory.FAIRYS,
                JsonCategory.PARASITES,
                JsonCategory.DEMON_HEARTS,
                JsonCategory.NPCS,
                JsonCategory.ENEMIES
        ]
        initChecked = self.sortInitButton.isChecked()
        
        if not self.sortDemonHeartsButton.isChecked(): shownCategories.remove(JsonCategory.DEMON_HEARTS)
        if not self.sortEntropicParasitesButton.isChecked(): shownCategories.remove(JsonCategory.PARASITES)
        if not self.sortChaosCoresButton.isChecked(): shownCategories.remove(JsonCategory.CHAOS_CORES)
        if not self.sortFariesButton.isChecked(): shownCategories.remove(JsonCategory.FAIRYS)
        if not self.sortItemsButton.isChecked(): shownCategories.remove(JsonCategory.ITEMS)
        if not self.sortCheckpointsButton.isChecked(): shownCategories.remove(JsonCategory.CHECKPOINTS)
        if not self.sortNpcsButton.isChecked(): shownCategories.remove(JsonCategory.NPCS)
        if not self.sortEnemiesButton.isChecked(): shownCategories.remove(JsonCategory.ENEMIES)
        
        for listItem in self.getListWidgetItems():
            widget: ListIDItemWidget = self.idList.itemWidget(listItem)
            showCategory = widget.category in shownCategories
            showInit = False if not initChecked and widget.initFlag else True
            if showCategory and showInit:
                listItem.setHidden(False)
            else:
                listItem.setHidden(True)
                
        return shownCategories
                
        


    def generateName(self, category: JsonCategory) -> str:
        location = self.location or 'Unknown Location'
        checkpoint = self.checkpoint or 'Unknown Checkpoint'
        
        if category == JsonCategory.CHECKPOINTS: return checkpoint
        else: return f"{location}/{checkpoint}"
        
    
    def generateDescription(self, category: JsonCategory) -> str:
        location = self.location or 'Unknown Location'
        checkpoint = self.checkpoint or 'Unknown Checkpoint'
        
        if category == JsonCategory.CHECKPOINTS:
            return f"Checkpoint in {location}"
        else:
            return f"Found in {location} at checkpoint {checkpoint}"
        


    def newListItem(self, category: JsonCategory, id: str):
        listItem = QListWidgetItem()
        
        INIT_FRAME_WINDOW = 150
        initFlag = True if self.frameCount <= self.loadedDirectoryFrame + INIT_FRAME_WINDOW else False
        
        # Try getting from identifiers        
        name:str = None
        description:str = None
        catalogedGameItems:list[dict] = [x for x in self.identifiers[category.value]]
        for gameItem in catalogedGameItems:
            if id == gameItem[KEY_ID]:
                name = gameItem[KEY_NAME]
                description = gameItem[KEY_DESCRIPTION]
            
        # Make the list item
        widget = ListIDItemWidget(
            category = category,
            id = id,
            name = name or self.generateName(category),
            description = description or self.generateDescription(category),
            initFlag = initFlag
        )
        
        listItem.setSizeHint(widget.sizeHint())
        self.idList.addItem(listItem)
        self.idList.setItemWidget(listItem, widget)
        
        shownCategories = self.updateFilters()
        if not category in shownCategories: return
        
        CONFIG_SOUND = True
        if not initFlag and CONFIG_SOUND:
            mixer.music.play()
            
        if ListIDItemWidget.amountBeingEdited <= 0 and self.config[CONFIG_AUTOSCROLL] == STRING_TRUE:
            self.idList.setCurrentItem(listItem)


    def updateList(self):
        # Error Handeling
        if not self.playerStateJson:
            return print('Could not find playerStateJson')
        elif not self.headerJson:
            return print('Could not find headerJson')
        elif not self.worldStateJson:
            return print('Could not find worldStateJson')


        try:
            with open(self.headerJson, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.checkpoint = data[JsonCategory.CHECKPOINT_NAME.value]
                self.location = data[JsonCategory.LOCATION_NAME.value]


            with open(self.playerStateJson, 'r', encoding='utf-8') as file:
                data = json.load(file)
    
                widgets = self.getListIDItemWidgets()
                existingIds: list[str] = [s.id for s in widgets]
                
                
                # Get Category pointers
                idListPointers = {
                    JsonCategory.ITEMS: [],
                    JsonCategory.CHECKPOINTS: [],
                    JsonCategory.CHAOS_CORES: [],
                    JsonCategory.FAIRYS: [],
                    JsonCategory.PARASITES: [],
                    JsonCategory.DEMON_HEARTS: [],
                    JsonCategory.NPCS: [],
                    JsonCategory.ENEMIES: []
                }
                
                collectablesCategories = (
                    JsonCategory.CHAOS_CORES,
                    JsonCategory.FAIRYS,
                    JsonCategory.PARASITES,
                    JsonCategory.DEMON_HEARTS
                )
                for category in collectablesCategories:
                    idListPointers[category] += data['collectables'][category.value]
                
                idListPointers[JsonCategory.ITEMS] += data['playerInventory'][JsonCategory.ITEMS.value]
                idListPointers[JsonCategory.CHECKPOINTS] += data['playerCheckpoints'][JsonCategory.CHECKPOINTS.value]
                    
                
            with open(self.worldStateJson, 'r', encoding='utf-8') as file:
                data = json.load(file)
                idListPointers[JsonCategory.NPCS] += data['encounteredNPCs'][JsonCategory.NPCS.value]
                idListPointers[JsonCategory.ENEMIES] += data['encounteredEnemies'][JsonCategory.ENEMIES.value]
                    
            for category, idList in idListPointers.items():
                for id in idList:
                    if not id in existingIds:
                        self.newListItem(category, id)
                
        except PermissionError:
            print('MainWindow.updateList: Couldnt get the permission to write... fuck!')
        except FileNotFoundError:
            print('Something went HORRIBLY WRONG!!! just kidding')
            
                        
                
                        
                        
                        
    def closeEvent(self, a0):
        if len(self.getListWidgetItems()) > 0 and ListIDItemWidget.modificationsMade:
            messageBox = QMessageBox(self)
            messageBox.setText("If you quit now, you could loose your identifiers! Are you sure about this?")
            messageBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            messageBox.setDefaultButton(QMessageBox.StandardButton.No)
            result = messageBox.exec()
            if result == QMessageBox.StandardButton.No: return a0.ignore()
        
        self.saveConfig()
        self.writeQSettings()
        return super().closeEvent(a0)

        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) # pyqt6 changed this so you dont need to use .exec_ since i think python 3 stopped using it?