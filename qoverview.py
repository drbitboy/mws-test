""" 
overview.py

S. Sackett 8/31/2018

Overview shows all of the data for a range of Sols.  It is used as a visualization aid and to
select the center of the 1/3 Sol data range displayed in the Data Selector

"""
import traceback
import numpy as np
import bqplot as bq
import ipywidgets as wg

import qconfig as c
import qdataselector as ds
import qdb_module as db_module
from qSELECTOR_SERIES import SELECTOR_SERIES
from qutilities import setTimeValues, updateErrorMsg, takeClosestIndex, do_mws_log_actions


########################################################################
def initOverview():

    # global brushOv, xScaleOv, figOv, bFirstCall
    global brushOv, figOv, bFirstCall

    bFirstCall = True  # Flag used by on_bnFetchSolRange to tell if this the first call after initialization

    # Instantiate all Data Selector plot series'
    dtOverviewSeries = {}
    c.xScaleOv = bq.LinearScale()

    # Size and shape of Overview figure
    loFigOv = wg.Layout(display='flex',
                        height = '80px',
                        width='auto',
                        margin='0px 0px 0px 0px',
                        padding='0px 0px 0px 0px'
                        )

    # Margins around Overview plot
    margOv = {'top': 5, 'bottom': 0, 'right': 0, 'left': 0}


    # The Overview Plot Figure
    figOv = bq.Figure(layout=loFigOv,
                      fig_margin=margOv,
                      min_aspect_ratio=.01,
                      max_aspect_ratio=100,
                      background_style={'fill': 'aliceblue'}
                      )

    tbFigOv = bq.Toolbar(figure=figOv)

    return figOv, tbFigOv

########################################################################
def initTimeLabelsOv():
    # Overview Panel time range display labels
    # Used to show the span of time selected by the Overview Brush
    #

    # Size, shape and style of display segments
    loTimeDisplayOv = wg.Layout(display='flex',
                                align_items='stretch',
                                width='auto',
                                height='auto',
                                margin='0px 0px 0px 0px',
                                padding='2px 10px 2px 10px'
                                )

    return dict([(k,wg.HTML(value=k, layout=loTimeDisplayOv),) for k in c.kTimeKeys])


########################################################################
def initOverviewControls(dtDataFileDirectory):

    global txCurrentRange, txAvailableRange, bitSpan, bitDecimation
    global dtOverviewButtons, ddFileSelector, bnFetchSolRange, bitSpan

    loBit = wg.Layout(display='flex',
                        width='140px',
                        height='auto',
                        margin='5px 0px 5px 0px',
                        padding='0px 0px 0px 0px'
                        )


    # Decimation factor selector
    #
    # Data returned from the database will be decimated by this factor
    bitDecimation = wg.BoundedIntText(
        value=c.decimationFactor,
        min=1,
        max=99,
        step=1,
        description='Decimation:',
        disabled=False,
        layout=loBit
    )

    # The number of Sols beginning with the initial Sol
    bitSpan = wg.BoundedIntText(
        value=1,
        min=1,
        max=99,
        step=1,
        description='Sols:',
        disabled=False,
        layout=loBit
    )

    # Dropdown selector for the initial Sol in the span
    # Size and shape of Sol file selector dropdown
    loDdSol = wg.Layout(display='flex',
                        width='150px',
                        height='auto',
                        margin='5px 0px 5px 0px',
                        padding='0px 0px 0px 0px'
                        )

    # Most recent Sol first
    ltSolList = sorted(list(dtDataFileDirectory.keys()), reverse=True)
    ddFileSelector = wg.Dropdown(index=0, description="Final Sol:", options=ltSolList, layout=loDdSol)


    # Size and shape of range text widgets
    loTxRange = wg.Layout(display='flex',
                          width='210px',
                          height='auto',
                          margin='5px 10px 5px 0px',
                          padding='0px 0px 0px 0px'
                          )

    # Text widget to show range of Sols available
    txAvailableRange = wg.Text(description="Available:", placeholder="000000 : 000000", disabled=True, layout=loTxRange)
    displaySolRange(dtDataFileDirectory)



    # Text widget to show current range of Sols selected
    txCurrentRange = wg.Text(description="Current:", placeholder="000000 : 000000", disabled=True, layout=loTxRange)

    # Size and shape of Buttons
    loBnLoad = wg.Layout(display='flex', justify_content='center', width="70px", height='auto',
                         border='solid lightgray', margin='2px 20px 2px 10px')


    # Button to execute Sol range query
    bnFetchSolRange = wg.Button(description='Load',
                                disabled=False,
                                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                                tooltip='Execute Sol Range Query',
                                layout=loBnLoad
                            )


    dtOverviewButtons = {'load': bnFetchSolRange
                        }

    loLbSource = wg.Layout(margin='0px 5px 0px 5px')
    lbSourceLabel = wg.Label(value='Source:\n{}'.format(c.globalDbName), layout=loLbSource)

    return ddFileSelector, bitSpan, bitDecimation, txAvailableRange, txCurrentRange, dtOverviewButtons, lbSourceLabel


########################################################################

def displaySolRange(dtDataFileDirectory):
    global txAvailableRange

    # Update Overview Panel available Sol range indicator
    solsAvailable = dtDataFileDirectory.keys()
    # Display the range of available Sols
    txAvailableRange.value="{} : {}".format(min(solsAvailable), max(solsAvailable))


########################################################################

def hilightRange(start, limit, range):
    """
    hilightRange()

    Use brushOv to highlight the region of the Overview Panel graphic
    that corresponds to the Data Selector graphic.

    This routine is normally entered through a callback from brushOv and as such
    the value of "start" may be any SCLK value within the Overview Panel graphic.
    It is possible that "start + range" will extend past the data represented in
    the Overview graphic, if this happens the left edge of the highlight is adjusted
    so that the entire "range" is within the graphic.


    start  -  Initial SCLK value
    limit  -  Final SCLK value
    range  -  The number of seconds representing the span of the highlight

    returns - SCLK values at the edges of the highlighted region
    """

    global brushOv

    hilightStart = hilightEnd = None

    # Keep the hilight within the span of the data
    if start + range > limit:
        hilightStart = limit - range
        hilightEnd = limit
    else:
        hilightStart = start
        hilightEnd = start + range

    brushOv.selected = np.array([hilightStart, hilightEnd])

    return hilightStart, hilightEnd



# ########################################################################
brushOv = None
def enableBrushOvCallback(b = True):

    global brushOv

    if brushOv:
        try:
            if b:
                brushOv.observe(on_brushOv, names=['brushing'])
            else:
                brushOv.unobserve(on_brushOv, names=['brushing'])
        except Exception as e:
            updateErrorMsg('enableBrushOvCallback: {}'.format(str(e)))



########################################################################
obo = 0
def on_brushOv(change,force=False):
    do_mws_log_actions(dict(change=change,force=force))

    global dtInstrumentOverview
    global last_xSclk_hi, last_xSclk_lo
    global figOv

    # Overview Brush interaction callback
    #
    # This is the source of the data shown in the Data Selector and Analysis Panels, it is entered
    # as a callback for the brushOv in response to user input.
    #
    # This is called each time the Overview Panel brush range changes.
    # The variable 'change' is a dictionary of information about the brush.
    # change['owner'] points to the brush and the attribute 'selected' of the brush contains
    # the value of the SCLK range.
    #

    b = change.owner  # The Calling brush, in this case it is always brushOv

    global obo
    # obo += 1
    # print("on_brushOv: Count: {} Old: {} New: {} Type: {} Name: {} Brushing: {}".format(obo, change.old, change.new,
    #                                                                                     change.type, change.name,
    #                                                                                     b.brushing))


    if force or not b.brushing:
        # Skip out of range errors that can occur when the brush area is very small.
        # Below we obtain information about the data under the Brush from the Overview Figure
        # and use it to set the midpoint for the range of data shown in the Data Selector
        # Even if the user brushes a range we are only interested in the minimum value of
        # the range.  This means that a click on the plot results in the minimum value
        # becoming the midpoint of the range of data shown in the Data Selector.  A highlight
        # is shown on the Overview Plot to indicate the range shown in the Data Selector


        # Exit if the Overview figure does not contain any plots
        if len(figOv.marks) < 1:
            return


        # Update Data Selector time range display
        try:
            # global obo
            # obo += 1
            # print("on_brushOv: Count: {} Old: {} New: {} Type: {} Name: {} Brushing: {}".format(obo, change.old, change.new, change.type, change.name, b.brushing))

            # Update Data Selector and Analysis Panel labels
            if b.selected is None: return
            if len(b.selected) < 1: return

            manage_bnFetchSolRange(disable=True)

            xSclk_lo = b.selected[0]  # Minimum value in the range
            xSclk_hi = b.selected[-1]  # Minimum value in the range


            if last_xSclk_lo == xSclk_lo and last_xSclk_hi == xSclk_hi:
                return   # Nothing to do, this is a redundant callback
            else:
                last_xSclk_lo = xSclk_lo
                last_xSclk_hi = xSclk_hi
                setTimeValues(c.dtTimeLabelsOv, xSclk_lo, xSclk_hi)

            # Fetch data for use in the Data Selector and Analysis Panel
            c.dtTimeData['SCLK'] = [xSclk_lo, xSclk_hi]
            for kdata in dtInstrumentOverview:
                c.dtInstrumentData[kdata] = dtInstrumentOverview[kdata].loc[xSclk_lo:xSclk_hi]

            ds.populateDataSelectorDs(c.dtTimeData
                                     , c.dtInstrumentData
                                     , compress_to=c.compress_to
                                     )
        except Exception as e:
            updateErrorMsg('on_brushOv:  {}'.format(str(e)))
            traceback.print_exc()
        finally:
            manage_bnFetchSolRange(disable=False)

########################################################################
def manage_bnFetchSolRange(disable=False, message=''):

    global dtOverviewButtons

    for key in dtOverviewButtons:
        dtOverviewButtons[key].disabled = disable

    b = dtOverviewButtons['load']
    if disable:
        b.description = "Wait"
        b.button_style = "danger"
    else:
        b.description = 'Load'
        b.button_style = 'success'


########################################################################
def on_bnFetchSolRange(button):
    """ on_bnFetchSolRange

    This is the source for the data shown in the Overview Panel,
    it is also the source of the initial data shown in the Data Selector, it is entered
    as a callback for the bnFetchSolRange in response to user input.

    Input: None
    Output: None
    """
    do_mws_log_actions(dict(button=button))

    global dtTimeOverview
    global dtInstrumentOverview
    global brushOv
    global last_xSclk_hi, last_xSclk_lo
    global bitSpan, bitDecimation, txCurrentRange
    global figOv
    global dtOverviewSeries
    global bFirstCall

    manage_bnFetchSolRange(disable=True, message="\non_bnFetchSolRange")

    # Update Overview Panel Sol range indicators
    displaySolRange(c.dtDataFileDirectory)

    # Display the range of sols currently requested
    finalSol = c.ddFileSelector.value
    initialSol = finalSol - bitSpan.value +1
    txCurrentRange.value="{} : {}".format(initialSol, finalSol)

    ### Decimate data based on the number of Sols requested and supplied
    ### decimation factor, IFF supplied factor is greater than unity
    decimation = max([1,bitDecimation.value > 1 and (bitSpan.value * bitDecimation.value) or 1])

    # Fetch data to show in the Overview Panel
    dtTimeOverview, dtInstrumentOverview = db_module.select_by_sol((initialSol, finalSol), c.globalDbName, decimation=decimation, required_keys=c.kDataColumnKeys)

    # Instantiate all Data Selector plot series'
    c.xScaleOv.min = dtTimeOverview['SCLK'][0]
    c.xScaleOv.max = dtTimeOverview['SCLK'][-1]

    dtOverviewSeries = {}

    for kdata in dtInstrumentOverview:
       ds.replaceSelector(kdata, dtInstrumentOverview, dtOverviewSeries, c.xScaleOv, compress_to=c.compress_to)

    # Initialize data to show in Overview plots
    ltMarks = [dtOverviewSeries[kdata].line for kdata in dtOverviewSeries]
    # for m in ltMarks:
    #     m.visible = True

    enableBrushOvCallback(False)
    c.brushOv = brushOv = bq.interacts.BrushIntervalSelector(marks=ltMarks,
                                                 scale=c.xScaleOv,
                                                 color='Firebrick',
                                                 continuous_update=False)

    figOv.marks=ltMarks   # Show data in Overview Panel

    figOv.interaction=brushOv

    # Set highlight and return SCLK value at brushOv edges
    dsr = min([(dtTimeOverview['SCLK'][-1] - dtTimeOverview['SCLK'][0])/24.0, c.dataSelectorRange_default_on_load])
    xSclk_lo, xSclk_hi = hilightRange(dtTimeOverview['SCLK'][0], dtTimeOverview['SCLK'][-1], dsr)
    setTimeValues(c.dtTimeLabelsOv, xSclk_lo, xSclk_hi)

    # Fetch data for use in the Data Selector and Analysis Panel based on the SCLK range of the Overview brush.
    # Populate Data Selector with data under the Overview brush.
    c.dtTimeData['SCLK'] = [xSclk_lo, xSclk_hi]
    for kdata in dtInstrumentOverview:
        c.dtInstrumentData[kdata] = dtInstrumentOverview[kdata].loc[xSclk_lo:xSclk_hi]

    # On the first call set the visible plots in the Data Selector to match the default Analysis Panel subplots
    if bFirstCall:
        ds.populateDataSelectorDs(c.dtTimeData
                                 , c.dtInstrumentData
                                 , c.ltStartupSubplots
                                 , compress_to=c.compress_to
                                 )
        bFirstCall = False

    # For all other calls make visible the set of plots selected by the user with the Data Selector checkboxes
    else:
        ds.bEnableBrushDsLast,ds.brushDs = False,None
        ds.populateDataSelectorDs(c.dtTimeData
                                 , c.dtInstrumentData
                                 , compress_to=c.compress_to
                                 )

    last_xSclk_hi = xSclk_hi
    last_xSclk_lo = xSclk_lo

    manage_bnFetchSolRange(disable=False, message="on_bnFetchSolRange\n\n")

    enableBrushOvCallback()



########################################################################
def updateOverviewVisibility(key):

    # Change the visibility of Overview plots to match corresponding Data Selector plots

    global dtOverviewSeries

    if key in dtOverviewSeries and key in c.dtSelectorDs:
        line = dtOverviewSeries[key].line
        line.visible = c.dtSelectorDs[key].cbShow.value
