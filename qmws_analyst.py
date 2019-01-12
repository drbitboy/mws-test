# S. Sackett, Lacthmoor Services
# mws_analyst.py
# 3/11/2018

# In this library there are two major graphic elements these are the Data Selector
# and the Analysis Panel.  As a convention variables and objects that pertain to the Data Selector
# have the sufix Ds appended to their names and those pertaining to the Analysis Panel have Ap appended.
# Variables and objects with no suffix on their names have no special affinity for either graphic.
#
# Examples:
#
#       dfTwins     - No affinity
#       scHwsDs     - Data Selector
#       scHwsAp     - Analysis Panel
#
# Prefixes on variable and object names generally indicate the type of the object.
# Examples:
#
#       lHwsDs      - Is a bqplot Line object
#       loTimeDisplayDs  - Is a bqplot Layout object
#       figDs       - Is a bqplot Figure object
#       dtTimeData  - Is a dictionary
#       ltDataFiles - Is a list
#       kXYZ        - Is a key, string 'XYZ', into a dictionary
#
# Relative to bq plot package the word Mark is used in two ways.  One is that in bqplot terminoloty
# a Mark is a graphic
# representation of a data series. For example an XY line graph uses a Lines Mark. The other use
# is a reference to a shape used to identify data points.  For example a circle or triangle Mark.
#
# bqplot glossary:
#    Figure      - A container for the graphic representation of data.
#    Mark        - A specific object type used to provide a visual representation of data. eg. Lines, Bars, Histograms.
#    Lines       - A Mark used to present data as a Cartesian plot.
#
# The Analysis Panel contains six zones for displaying Figures and associated information,
# these zones are called Subplots.  The user can assign a given Figure to any or all subplots.
# This allows for the set of Figures to contain more than six members with any six of them
# being displayed simultaneously.
#
# The GUI is named the User Surface.  The User Surface visual elements are formated using Flexbox,
# and are contained in a group of interrelated VBox and HBox elements.  Most of the visual
# elements are assigned to their respective VBox or HBox elements in initUserSurface() but
# there are occasions where the assignments are made in other functions.
#
# ipywidgets are used extensively as visual elements such as Checkboxes and Dropdowns,
# also ipywidgets form the underpinning of the bqplot package.
#
from datetime import datetime

import bqplot as bq
from IPython.display import display

import qconfig as c

from qutilities import updateErrorMsg, do_mws_log_actions
from qanalysispanel import initTimeLabelsAp \
                          ,initAnalysisPanel \
                          ,initDropdownsAp \
                          ,initSubplotsAp \
                          ,registerPlotsApCallbacks \
                          ,enableDropdownApCallback

from qdataselector import on_cbCheckboxesDs, on_brushDs, initDataSelector, initTimeLabelsDs, enableBrushDsCallback
from qusersurface import initUserSurface
from qstandardLayouts import initStandardLayouts
from qoverview import initOverview, initTimeLabelsOv, initOverviewControls, on_bnFetchSolRange


########################################################################
##### Beginning of program main()
########################################################################

do_mws_log_actions(dict(real_caller=__file__,action='initializing MWS Analyst'))

c.globalDbName = 'test_q'  ### for Quick mws; MySQL is not used 

# X-scale for Data Selector and Analysis Panel plots
c.xScaleDs = bq.LinearScale()
c.xScaleAp = bq.LinearScale()

c.sclkOffset = 0.0

# Initialize various controls
c.dtTimeLabelsOv = initTimeLabelsOv()
c.dtTimeLabelsDs = initTimeLabelsDs()
c.dtTimeLabelsAp = initTimeLabelsAp()

c.dtDataFileDirectory = dict([(sol,(sol,'q',),) for sol in range(1,11)])

# Initialize Overview panel
c.figOv, c.tbFigOv = initOverview()

# Initialize Overview Panel controls
(c.ddFileSelector, c.bitSpan, c.bitDecimation, c.txAvailableRange
,c.txCurrentRange, c.dtOverviewButtons, c.lbSourceLabel
,) = initOverviewControls(c.dtDataFileDirectory)

# Initialize Data Selector
c.figDs, c.tbFigDs, c.bn95sHBoxDs, c.cbMarkDs, c.lbWaitDs = initDataSelector()

#
# # Initialize Analysis Panel subplot selector dropdowns
c.ltDropdownsOptionsAp = list(c.kDataColumnKeys)
c.dtDropdownsAp = initDropdownsAp(c.ltDropdownsOptionsAp)
#
# # Initialize Analysis Panel
#c.dtPlotsAp = initAnalysisPanel(c.dtInstrumentData)
c.dtPlotsAp = initAnalysisPanel()
#
# # Initialize Analysis Panel Subplots
c.dtSubplotsAp, c.dtSubplotChildrenAp = initSubplotsAp(c.dtPlotsAp)



# Initialize Layouts
c.wglo, c.dtLoFaa0, c.dtLoFaa0Border = initStandardLayouts()

# Initialize User Surface
c.vbUserSurface, c.hbCheckboxesDs = initUserSurface()

updateErrorMsg('*** INFO: PROGRAM SUCCESSFULLY INITIALIZED AT {} UTC ***'.format(datetime.utcnow()))

# Display the User Surface
c.userSurfaceId = display(c.vbUserSurface, display_id=True)



# Register Callbacks


# # Register checkbox callback for Data Selector
# for kdata in c.dtSelectorDs:
#     c.dtSelectorDs[kdata].cbShow.observe(on_cbCheckboxesDs, names='value')

# Register callbacks for Mark and Brush checkboxes for Raw data
registerPlotsApCallbacks(c.dtPlotsAp)

# Register dropdowns with callback function
# for ksp in c.dtDropdownsAp:
#     c.dtDropdownsAp[ksp].observe(on_DropdownsAp, names='value')
enableDropdownApCallback()

# Register Overview brush callback
#enableBrushOvCallback()

# Register Overview Go button
c.dtOverviewButtons['load'].on_click(on_bnFetchSolRange)

