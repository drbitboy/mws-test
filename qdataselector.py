import os
import sys
import numpy
import traceback
import bqplot as bq
import pandas as pd
from enum import Enum
import ipywidgets as wg
from collections import OrderedDict
from traitlets.utils.bunch import Bunch

import qconfig as c
import qoverview as ov
import qanalysispanel as ap
from qSELECTOR_SERIES import SELECTOR_SERIES
from qutilities import setTimeValues, updateErrorMsg, takeClosestIndex, do_mws_log_actions

doDebug = "DEBUG" in os.environ

########################################################################
class EMPTY(object):
    def __init__(self): pass


########################################################################
def on_bn95s(change):
    """
    Callback for green [<] and [>] buttons that shift DS brush by
    95% of its width

    """
    do_mws_log_actions(dict(change=change))
    global brushDs
    try:

        dt = dict(brushDs_keys=isinstance(brushDs,bq.interacts.BrushIntervalSelector) and vars(brushDs).keys() or None)

        ### Ensure brushDs is a brush and its .selected is a
        ### numpy.ndarray of length 2
        if not (isinstance(brushDs,bq.interacts.BrushIntervalSelector)
            and isinstance(brushDs.selected,numpy.ndarray)
               ):
            try: dt['brushDs_selected'] = brushDs.selected
            except: dt['brushDs_selected'] = 'UNKNOWN'
            updateErrorMsg('on_bn95s: {}'.format(str(dt)))
            if doDebug: print('on_bn95s exiting:  brushDs is not a BrushIntervalSelector or brushDs.selected is not an ndrarray\n  {}'.format(str(dt)))
            return

        if len(brushDs.selected) != 2:
            if doDebug: print('on_bn95s exiting:  brushDs.selected length is not 2\n  {}'.format(str(dt)))
            return

        sclkMinOrig = sclkMin = brushDs.selected.min()
        sclkMaxOrig = sclkMax = brushDs.selected.max()
        sclk_length = sclkMax - sclkMin
        sclk_shift = 0.95 * sclk_length

        dt = dict(sclk_length=round(sclk_length,2),sclkMinOrig=round(sclkMin,2))

        if sclk_length <= 0.0:
            updateErrorMsg('on_bn95s: {}'.format(str(dt)))
            if doDebug: print('on_bn95s exiting:  brushDs non-positive length\n  {}'.format(str(dt)))
            return

        lt_or_gt = change._trait_values['description']

        if lt_or_gt == '<':
            sclkMin -= sclk_shift
            sclkMax -= sclk_shift
        elif lt_or_gt == '>':
            sclkMin += sclk_shift
            sclkMax += sclk_shift
        else:
            if doDebug: print('on_bn95s exiting:  Button has unknown description\n  {}'.format(str(dt)))
            return

        dt.update(dict(lt_or_gt=lt_or_gt))

        ovSclkMin = c.brushOv.selected.min()
        ovSclkMax = c.brushOv.selected.max()

        if ovSclkMin > sclkMin:
            sclkMin = ovSclkMin
            sclkMax = sclkMin + sclk_length
        elif ovSclkMax < sclkMax:
            sclkMax = ovSclkMax
            sclkMin = sclkMax - sclk_length

        if sclkMin==sclkMinOrig and sclkMax==sclkMaxOrig:
            if doDebug: print('on_bn95s exiting:  No change\n  {}'.format(str(dt)))
            return

        # Fake a brush callback to trigger display of Analysis Panel plots
        #enableBrushDsCallback(enable=False)

        do_mws_log_actions(dict(before='brushDs.brushing=True'))
        brushDs.brushing = True
        do_mws_log_actions(dict(after='brushDs.brushing=True'))
        brushDs.selected = [sclkMin,sclkMax]
        #brushDs.brushing = False

        #change = Bunch({'owner': brushDs})
        #on_brushDs(change,force=dt)


    except Exception as e:
        import traceback
        traceback.print_exc()
        import pprint
        pprint.pprint(vars(brushDs))
        dt.update(dict(e=str(e)))
        updateErrorMsg('on_bn95s: {}'.format(str(dt)))

    finally:
        try:
            do_mws_log_actions(dict(finally_before='brushDs.brushing=False'))
            #enableBrushDsCallback(enable=True)
            brushDs.brushing = False
            do_mws_log_actions(dict(finally_after='brushDs.brushing=False'))
        except:
            do_mws_log_actions(dict(finally_failed='brushDs.brushing=False'
                                   ,traceback=traceback.format_exc()
                                   ))

    if doDebug: print('Normal exit\n  {}'.format(str(dt)))
    do_mws_log_actions(dict(leaving=None))
    return

########################################################################
def initDataSelector():

    # The Data Selector is used to chose a subset of data for viewing in
    # the Analysis Panel.  The Data Selector contains a Figure that displays
    # every data series. A subset range of data values from these series
    # can be selected by using the Data Selector Brush to cover the range of interest
    #


    global brushDs, figDs, cbMarkDs, lbWaitDs

    loBn95 = wg.Layout(display='flex', justify_content='center', width="auto", height='auto'
                      ,border='solid lightgray', margin='0px 0px px 0px')

    bn95s = [wg.Button(description='<>'[iBn]
                      ,disabled=False
                      ,button_style='success' # 'success', 'info', 'warning', 'danger' or ''
                      ,tooltip='Shift data selector brush 95% to the {}'.format(('left','right',)[iBn])
                      ,margin='0px 0px 0px 0px'
                      ,padding='0px 0px 0px 0px'
                      )
            for iBn in [0,1]
            ]
    for bn in bn95s: bn.on_click(on_bn95s)
    bn95sHBoxDs = wg.HBox(children=bn95s,layout=loBn95)

    # Size and shape of cbMarkDs
    loCbDs = wg.Layout(display='flex',
                             width='auto',
                             height='auto',
                             margin='20px 0px 0px 10px',
                             padding='0px 0px 0px 0px'
                             )
    cbMarkDs = wg.Checkbox(value=False, description='Mark',
                                  indent=False, layout=loCbDs)
    cbMarkDs.observe(on_cbMarkDs, names='value')

    lbWaitDs = wg.HTML(value='<span>&nbsp;</span>',
                       layout=wg.Layout(display='flex',margin='0px 0px 0px 10px',padding='0px 0px 0px 0px'))


    # Size and shape of Data Selector figure
    loFigDs = wg.Layout(display='flex',
                        width='878px',
                        height='80px',
                        margin='0px 0px 0px 0px',
                        padding='0px 0px 0px 0px'
                        )

    # Margins around Data Selector plot
    margDs = {'top': 5, 'bottom': 0, 'right': 0, 'left': 0}

    figDs = bq.Figure(layout=loFigDs,
                      fig_margin=margDs,
                      min_aspect_ratio=.01,
                      max_aspect_ratio=100,
                      background_style={'fill': 'aliceblue'})

    tbFigDs = bq.Toolbar(figure=figDs)


    return figDs, tbFigDs, bn95sHBoxDs, cbMarkDs, lbWaitDs



########################################################################
def initTimeLabelsDs():
    # Data Selector time range display labels
    # Used to show the span of time selected by the Data Selector Brush
    #

    # Size, shape and style of display segments
    loTimeDisplayDs = wg.Layout(display='flex',
                                align_items='stretch',
                                #border='solid lightgray',
                                width='auto',
                                height='auto',
                                margin='0px 0px 0px 0px',
                                padding='2px 10px 2px 10px'
                                )

    #return dict([(k,wg.HTML(value=k, layout=loTimeDisplayDs),) for k in c.kTimeKeys + [c.kDataSourceLabel]])
    return dict([(k,wg.HTML(value=k, layout=loTimeDisplayDs),) for k in c.kTimeKeys])


########################################################################
def populateDataSelectorDs(dtTimeData
                          , dtInstrumentData
                          , ltVisiblePlots = []
                          , compress_to = 0
                          ):
    """updateDataSelectorDs

    Update the data displayed in the Data Selector

    dtTime  - Range of time values indexed by time standard
                dtTime["SCLK"][0] = Low time value in SCLK format
                dtTime["SCLK"][1] = High time value in SCLK format

    dtInstrument - Instrument data in a bqplot.series indexed by instrument type

    returns - Nothing
    """
    global dtCheckboxState

    showWait()

    #Disable Analysis Panel Subplot callbacks
    if c.dtPlotsAp:
        ap.registerPlotsApCallbacks(c.dtPlotsAp, doregister=False)

    # Instantiate all Data Selector plot series'
    c.xScaleDs = bq.LinearScale()

    ov.manage_bnFetchSolRange(disable=True, message="populateDataSelectorDs")

    enableCheckboxesCallback(enable=False)

    #Save checkboxes state
    dtCheckboxState = {}
    for kdata in c.dtSelectorDs:
        dtCheckboxState[kdata] = c.dtSelectorDs[kdata].cbShow.value

    for kdata in dtInstrumentData:
        replaceSelector(kdata
                       , dtInstrumentData
                       , c.dtSelectorDs
                       , c.xScaleDs
                       ,compress_to=compress_to
                       )

    # Restore checkboxes
    for kdata in dtInstrumentData:
        # If ltVisiblePlots contains values use them as keys to set the visibility of the plots and checkbox state
        #  ltVisiblePlots in an input parameter and is normally used to display an initial set of plots
        if len(ltVisiblePlots) > 0:
            c.dtSelectorDs[kdata].line.visible = c.dtSelectorDs[kdata].cbShow.value = kdata in ltVisiblePlots

        # Else restore the plot visibility and checkbox state to what the user has selected
        elif kdata in dtCheckboxState:
            c.dtSelectorDs[kdata].line.visible = c.dtSelectorDs[kdata].cbShow.value = dtCheckboxState[kdata]

        ov.updateOverviewVisibility(kdata)  # Set visibility of corresponding trace in the Data Selector

    ov.manage_bnFetchSolRange(disable=False, message="populateDataSelectorDs")

    # Among other things this updates brushDs.marks
    updateDataSelector()

    enableCheckboxesCallback()

    #Enable Analysis Panel Subplot callbacks
    if c.dtPlotsAp:
        ap.registerPlotsApCallbacks(c.dtPlotsAp, doregister=True)

    showWait(show=False)


#####################
### Global values related to DS brush
bEnableBrushDsLast, brushDs = False, None

def updateDataSelector():

    global brushDs, bEnableBrushDsLast
    global cbMarkDs
    do_mws_log_actions(dict(check=brushDs is c.figDs.interaction))

    ov.manage_bnFetchSolRange(disable=True, message="updateDataSelector")

    ### Save selected range IFF brushDs is a BrushIntervalSelector
    if isinstance(brushDs,bq.interacts.BrushIntervalSelector):
        selected = brushDs.selected
        enableBrushDsCallback(enable=False)
    else:
        selected = []

    bEnableBrushDsLast, brushDs = False, None

    # Add checkboxes to Data Selector
    ltCheckboxesDs = [c.dtSelectorDs[kdata].cbShow for kdata in c.kDataColumnKeys]
    ltMarks = []
    for kdata in c.dtSelectorDs:
        # Add plots to data selector; register Checkbox callbacks
        ltMarks.append(c.dtSelectorDs[kdata].line)
        c.dtSelectorDs[kdata].cbShow.observe(on_cbCheckboxesDs, names='value')

        # Add checkbox if not already a child in checkbutton list
        if kdata in c.kDataColumnKeySet: continue
        ltCheckboxesDs.append(c.dtSelectorDs[kdata].cbShow)

    # Manage Data Selector Checkboxes
    xLo, xHi = c.dtTimeData['SCLK'][0], c.dtTimeData['SCLK'][-1]
    setTimeValues(c.dtTimeLabelsDs, xLo, xHi)
    c.xScaleDs.min = xLo
    c.xScaleDs.max = xHi

    (bEnableBrushDsLast,brushDs,) = (False
      , bq.interacts.BrushIntervalSelector(marks=ltMarks
                                          ,scale=c.xScaleDs
                                          ,color='Firebrick'
                                          ,continuous_update=False
                                          )
      ,)
    c.figDs.interaction=brushDs

    #Update Data Selector
    c.hbCheckboxesDs.children = ltCheckboxesDs
    c.figDs.marks = ltMarks

    ### Mung selected DS brush within DS plot range, if selected exists
    if 2==len(selected):
        dSel = selected[-1] - selected[0]
        if selected[-1] <= xLo: selected[0:2] = [xLo, xLo+dSel]
        if selected[0] >= xHi : selected[0:2] = [xHi-dSel, xHi]
        if selected[-1] >= xHi: selected[0:2] = [selected[0], xHi]
        if selected[0] <= xLo:  selected[0:2] = [xLo, selected[1]]

    manageBrushHighlight(selected, xLo, xHi)

    markPlotsDs(bMark = cbMarkDs.value)
    ov.manage_bnFetchSolRange(disable=False, message="updateDataSelector")

    # Fake a brush callback to trigger display of Analysis Panel plots
    change = Bunch({'owner': brushDs})
    on_brushDs(change,force=True)

    enableBrushDsCallback(enable=True)
    #enableCheckboxesCallback()
    #
    # #Enable Analysis Panel Subplot callbacks
    # if c.dtPlotsAp:
    #     ap.registerPlotsApCallbacks(c.dtPlotsAp, doregister=True)
    #
    #

########################################################################
def replaceSelector(kdata, dtData, dtSelector, xScale, compress_to=0):

    if kdata in dtSelector: del c.dtSelectorDs[kdata]  # Delete existing SelectorSeries
    data_series = dtData[kdata]

    dtSelector[kdata] = SELECTOR_SERIES(data_series, kdata, xScale, c.dtPlotColors[kdata],compress_to=compress_to)


########################################################################
def manageBrushHighlight(selected, xLo, xHi):

    # Get SCLK range of the Overview brush
    sclkMinOv = c.brushOv.selected[0]
    sclkMaxOv = c.brushOv.selected[-1]
    sclkRangeOv = sclkMaxOv - sclkMinOv

    # Keep brush highlight within the Data Selector plot
    if len(selected) == 2:

        selectedMin = selected[0]
        selectedMax = selected[-1]
        selectedRange = min([selectedMax - selectedMin,sclkRangeOv])

        # Check if the previous brush selection is within the range of the updated data
        if sclkMinOv < selectedMin and sclkMaxOv > selectedMax:
            brushDs.selected = selected  # Yes, restore the old selection

        elif sclkMinOv >= selectedMin:
            # Brush is off the left side
            # Move selection to beginning of Data Selector
            brushDs.selected = [sclkMinOv, sclkMinOv + selectedRange]

        elif sclkMaxOv <= selectedMax:
            # Brush is off the right side
            # Move selection to the end of the Data Selector
            brushDs.selected = [sclkMaxOv - selectedRange, sclkMaxOv]

        else:
            ### Execution should never get here
            pass

    else:
        ### No usable previous selection, use default:
        ### - one-twelfth of brushOv width
        brushDs.selected = [xLo, (xLo*11. + xHi) / 12.0 ]


########################################################################
def on_cbMarkDs(change):
    """
    Callback for DS [Mark] button to turn on plotting data points as
    circles, in addition to lines

    """
    do_mws_log_actions(dict(change=change))
    global cbMarkDs, lbWaitDs

    showWait()
    markPlotsDs(bMark=change.owner.value)
    showWait(show=False)


########################################################################
def showWait(show=True):

    s = None
    if show:
        s = '<span style="color:red;">Wait...</span>'
    else:
        s = '<span>&nbsp;</span>'

    lbWaitDs.value = s

########################################################################
def markPlotsDs(bMark = False, dsKey = ''):
    global figDs

    caller = sys._getframe(1).f_code.co_name
    try:
         for m in figDs.marks:
            key = m.labels[0]

            if len(dsKey) > 0 and key != dsKey: continue

            # If this is a plot and it is currently visible
            if key in c.kDataColumnKeys and c.dtSelectorDs[key].cbShow.value:
                if bMark:
                    m.marker = c.dataPointShape
                else:
                    m.marker = None
    except Exception as e:
        updateErrorMsg('markPlotsDs: {} bMark: {} dsKey: {} caller: {}'.format(str(e), bMark, dsKey, caller))


########################################################################
def on_cbCheckboxesDs(change):
    """
    Callback for series' visibility Checkboxes that toggle the
    visibility of the series plotted in the DS and OP

    """
    do_mws_log_actions(dict(change=change))
    global cbMarkDs
    co = change.owner

    for kdata in c.dtSelectorDs:
        sr = c.dtSelectorDs[kdata]
        if co is sr.cbShow:
            # Set visibility of corresponding trace in the DS, and
            # in the OP
            sr.line.visible = change.new
            ov.updateOverviewVisibility(kdata)
            markPlotsDs(bMark=(cbMarkDs.value and change.new), dsKey=kdata)

            break


########################################################################
# Register checkbox callback for Data Selector
bLastEnableCb = False
def enableCheckboxesCallback(enable=True):

    global bLastEnableCb

    if bLastEnableCb == enable: return

    bLastEnableCb = enable
    for kdata in c.dtSelectorDs:
        if enable == True:
            c.dtSelectorDs[kdata].cbShow.observe(on_cbCheckboxesDs, names='value')
        else:
            c.dtSelectorDs[kdata].cbShow.unobserve(on_cbCheckboxesDs, names='value')


########################################################################
def enableBrushDsCallback(enable=True):
    global brushDs, bEnableBrushDsLast

    do_mws_log_actions(dict(brushDs_=brushDs
                           ,bEnableBrushDsLast=bEnableBrushDsLast
                           ,enable_arg=enable
                           ,caller=sys._getframe(1).f_code.co_name
                           ))

    if not isinstance(brushDs,bq.interacts.BrushIntervalSelector): return

    # enCount += 1
    if enable == bEnableBrushDsLast: return

    bEnableBrushDsLast = enable
    if enable:
        brushDs.observe(on_brushDs, names=['brushing'])
    else:
        brushDs.unobserve(on_brushDs, names=['brushing'])


########################################################################
def on_brushDs(change,force=False):
    """
    Callback for DS brush activities, mostly mouse drags.
    N.B. Does nothing if [brush].brushing is True (start of drag) unless
         force keyword argument is True.  Normal callback events will
         never always have force==False; force keyword is used for
         programmatic callers of this calback routine.

    """
    do_mws_log_actions(dict(change=change,force=force
                           ,caller=sys._getframe(1).f_code.co_name
                           ))

    # Data Selector Brush interaction callback
    # This is called each time the Brush range changes.
    # The variable 'change' is a dictionary of information about the brush.
    # change['owner'] points to the brush and the attribute 'selected' of the brush contains
    # the value of the SCLK range.
    #
    # The user selects a range of X-values using the brush.  This routine fills the Analysis Panel
    # subplots by filling them with X-values under the brush and zooming the Y-Values to fill the subplot
    #
    # xScaleAp is global and on exit from this routine contains the plot scale derived from brushDs
    #'brushing', 'color', 'marks', 'scale', 'selected'

    ### The Calling brush, in this case it is always brushDs
    b = change.owner

    if force or not b.brushing:

        # Skip out of range errors that can occur when the brush area is very small.
        # Below we obtain information about the data under the Brush from the Data Selector Figure
        # and use it to set properties in the Analysis Panel Figures.

        ### Flags for finally: actions
        local_did_wait = False
        local_ap_callbacks = False

        # Update Data Selector time range display
        try:
            if not isinstance(b.selected,numpy.ndarray): return
            if len(b.selected) != 2: return

            bSelLo,bSelHi = [b.selected[i] for i in [0,-1]]
            if bSelLo == None or bSelHi == None: return

            showWait()
            local_did_wait = True

            # Update Data Selector and Analysis Panel labels
            setTimeValues(c.dtTimeLabelsDs, bSelLo, bSelHi)
            setTimeValues(c.dtTimeLabelsAp, bSelLo, bSelHi)
            c.xScaleAp.min, c.xScaleAp.max = bSelLo, bSelHi

            # Using r0 and r1 we have access to the range of X- and
            # Y-values under the Brush.  This is used to fill the
            # Analysis Panel plots with the data under the Data Selector
            # Brush, effectively zooming in on the region of the Data
            # Selector covered by the brush

            # Disable Analysis Panel Subplot callbacks
            ap.registerPlotsApCallbacks(c.dtPlotsAp, doregister=False)
            local_ap_callbacks = True

            for kdata in c.dtSelectorDs:
                updateSubplots(kdata, bSelLo, bSelHi)

        except IndexError as e:
            updateErrorMsg('on_brushDs[IndexError0]:  {}'.format(str(e)))
            traceback.print_exc()

        except Exception as e:
            updateErrorMsg('on_brushDs:  {}'.format(str(e)))

        finally:

            # Re-enable Analysis Panel Subplot callbacks
            if local_ap_callbacks:
                ap.registerPlotsApCallbacks(c.dtPlotsAp, doregister=True)

            if local_did_wait: showWait(show=False)


########################################################################
last_bSelLo = 0.0
last_bSelHi = 0.0
def updateSubplots(kdata, bSelLo=None, bSelHi=None):

    global last_bSelHi, last_bSelLo
    #caller = sys._getframe(1).f_code.co_name

    # Update only visible subplots
    if kdata in c.ltVisibleSubplots:

        # If caller specifies None then use the previous values
        if bSelLo is None or bSelHi is None:
            bSelLo, bSelHi = last_bSelLo, last_bSelHi
        else:
            last_bSelLo, last_bSelHi = bSelLo, bSelHi

        cdid = c.dtInstrumentData[kdata]

        ### Create a faux cdid with X and Y data if the cdid assigned
        ### above, of type pandas.Series, has no data
        if len(cdid) < 1: cdid = pd.Series(data=[0.],index=[bSelLo-1.])

        r0 = takeClosestIndex(cdid.index, bSelLo)
        r1 = takeClosestIndex(cdid.index, bSelHi)

        # Ensure there is at least 1 datum, even if beyond the brush
        if r0 == r1:
            if r0:
                r0 -= 1
            else:
                r1 += 1

        # Remove all non-data type marks
        ltM = []
        for m in c.dtPlotsAp[kdata].figure.marks:
            if m.labels[0] in c.kDataColumnKeys:
                ltM.append(m)

        c.dtPlotsAp[kdata].figure.marks = ltM

        # Size the plot to equal the span of the DS brush
        cdid = cdid.iloc[r0:r1]
        c.dtPlotsAp[kdata].line.x = cdid.index
        c.dtPlotsAp[kdata].line.y = cdid.values
