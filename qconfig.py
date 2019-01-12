import copy

globalErrorMsg = ''

dtInstrumentData = {}
dtTimeData  = {}
dtFilters  = {}
dtPlotColors  = {}
dtPlotsAp  = {}
dtDropdownsAp  = {}
dtFilterFiles = {}
dtSubplotsAp = {}
dtSubplotChildrenAp = {}
dtTimeLabelsAp = {}
dtTimeLabelsDs = {}
dtTimeLabelsOv = {}
dtSelectorDs = {}
dtOverviewButtons = {}
dtTickMarks = {}
dtNightMarks = {}

lbSourceLabel = None

channels_issensor = []

lbChannelsPlus = None
lbRequestType = None
lbErrorMsg = None
lbErrorTitle = None
hbCheckboxesDs = None

#Layouts
wglo = None
dtLoFaa0 = None
dtLoFaa0Border = None

# Subplot keys
kSubplotKeys = ['sp{}'.format(ch) for ch in '012345']

# Data column keys
# Ensure strings that will be concatenated end
(kHWS, kPE5DHZ, kWD, kMAT, kPAT, kPRE
,) = kDataColumnKeys = """
PRE HWS PE5DHZ WD MAT PAT
""".strip().split()

kDataColumnKeySet = set(kDataColumnKeys)

kSubplotDataColumnKeys = list(zip(kSubplotKeys, kDataColumnKeys))

#These are the initial plots shown in the Overview Panel, Data Selector and Analysis Panel.
# Overview Panel - The plots in this list are the only ones shown.
# Data Selector - The plots in this list are the only ones shown and the corresponding checkboxes are checked
# Analysis Panel - The dropdowns show the plots in the list from top to bottom and the corresponding plots are shown.
ltStartupSubplots = kDataColumnKeys[:]
ltVisibleSubplots = copy.copy(ltStartupSubplots)

kDataSourceLabel = 'Source'

### Controls re-sampling for OP and DS plots
compress_to=1000

(kUTC, kLMST, kSCLK,) = kTimeKeys = 'UTC LMST SCLK'.split()


# N.B. k4Times excludes kSCLK, so kSCLK must be last above
kTimeKeysExceptSCLK = kTimeKeys[:-1]

dtPlotColors = {kHWS: 'Red'
               ,kWD: 'Blue'
               ,kMAT: 'Lime'
               ,kPAT: 'SteelBlue'
               ,kPRE: 'Fuchsia'
               ,kPE5DHZ: 'darkgray'
               }


vbFigDs = None
figDs = None
bn95sHBoxDs = None
cbMarkDs = None
lbWaitDs = None
userSurfaceId = None
xScaleOv = None
xScaleDs = None
xScaleAp = None

# Number of seconds of data displayed in the Data Selector plot (1/24 Sol)
dataSelectorRange_default_on_load = int(88775.244/24.0)
decimationFactor = 1              # The amount to decimate the Overview Panel by for each Sol in the range.
figOv = None
brushOv = None
tbFigOv = None

# Marker is a shape that is used to mark data points on a plot series
dataPointSize = 15  # Size of the marker in px
dataPointShape = 'circle'  # Shape of the marker

bitSpan = None
bitDecimation = None
ddFileSelector = None
# txCurrentRange = None
# txAvailableRange = None
bnFetchSolRange = None

bBrushPresentAp = False

