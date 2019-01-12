import sys
import bqplot as bq
import pandas as pd
import ipywidgets as wg

import qconfig as c
import qdataselector as ds
from qINSTRUMENT import INSTRUMENT
from qutilities import updateErrorMsg, takeClosestIndex, setTimeValues, do_mws_log_actions


########################################################################
def initAnalysisPanel():
    """Initialize Analysis Panel subplots"""
    global dtPlotsAp

    list(c.kDataColumnKeys)
    dtPlotsAp = {}
    for kdata in list(c.kDataColumnKeys):
        series = pd.Series()
        dtPlotsAp[kdata] = INSTRUMENT(series, c.xScaleAp, kdata, c.dtPlotColors[kdata])

    return dtPlotsAp


########################################################################
def initSubplotsAp(dtPlotsAp):

    ########### This controls the height of the subplots in the Analysis Panel ###########
    loSpContainerAp = wg.Layout(display='flex', width='auto', height='90px')

    # Subplot Display Zones
    dtSubplotsAp = dict([(ksp,wg.HBox(layout=loSpContainerAp),) for ksp in c.kSubplotKeys])

    # Child lists for subplots
    #
    dtSubplotChildrenAp = {}

    # Subplot Display Zones initial figure assignments,
    # with Subplot selector Dropdown to its left
    
    for key in dtPlotsAp:
        # Add the plot and controls to this subplot dictionary
        p = dtPlotsAp[key]
        dtSubplotChildrenAp[key] = addSubplotChildrenAp(p.lbValue, p.figure, [p.cbMark, p.cbBrush])

    count = 0
    for ksp,kdata in c.kSubplotDataColumnKeys:
        key = c.ltStartupSubplots[count]

        # Select the subplot to show in this position of the Analysis Panel
        idx = c.ltDropdownsOptionsAp.index(key)  #Get the index of this key in the dropdown options list.
        c.dtDropdownsAp[ksp].index = idx    #Show the subplot represented by the key in the dropdown

        # The dropdowns are added in this manner rather than by including it in dtSubplotChildrenAp because
        # the dropdowns have a fixed vertical position in the Analysis Panel (sp0, sp1, ..., spN), in contrast the other Analysis Panel
        # children can move to any vertical position as well as being visible in multiple positions.
        dtSubplotsAp[ksp].children = dtSubplotChildrenAp[key] + [wg.HBox(children=[c.dtDropdownsAp[ksp]])]
        count += 1

    return dtSubplotsAp, dtSubplotChildrenAp


########################################################################
def initDropdownsAp(options):
    # Dropdowns to control selection of Figures for displayed in Analysis Panel subplots (Sp)

    # Size and shape of Analysis Plot Dropdowns
    loDdAp = wg.Layout(display='flex',
                       width='5em',
                       height='auto',
                       margin='5px 5px 0px 0px',
                       padding='0px 0px 0px 0px'
                       )

    dtDropdownsAp = {}
    for i in range(len(c.kSubplotKeys)):
        dtDropdownsAp.update({c.kSubplotKeys[i]: wg.Dropdown(index=i, options=options, layout=loDdAp)})

    return dtDropdownsAp


########################################################################
def initTimeLabelsAp():
    # Analysis Panel time range display
    # Shows the span of time selected by the Analysis Panel Brush

    # Size, shape and style of display segments
    loTimeDisplayAp = wg.Layout(display='flex',
                                align_items='stretch',
                                #border='solid lightgray',
                                width='auto',
                                height='auto',
                                margin='0px 0px 0px 0px',
                                padding='2px 10px 2px 10px'
                                )

    return dict([(k, wg.HTML(value=k, layout=loTimeDisplayAp),) for k in c.kTimeKeys])


########################################################################
count=0
last_operation = False
def registerPlotsApCallbacks(dtPlotsAp,doregister=True):
    """
    registerPlotsApCallbacks()

    This is used to both register (enable) and disable callbacks for controls (widgets)
    used with the Analysis Panel subplots.

    :param dtPlotsAp:  Dict containing subplots keyed by filter name
    :param doregister: True = Enable, False = Disable
    :return: Nothing
    """
    global count, last_operation
    # caller = sys._getframe(1).f_code.co_name
    # print('\n{} {} doregister: {} last_operation: {}'.format(caller, count, doregister, last_operation))
    # count += 1

    # Reject consecutive calls requesting the same operation
    if last_operation == doregister: return

    last_operation = doregister
    for key in dtPlotsAp:
        p = dtPlotsAp[key]
        #print(key)

        if doregister:
            p.cbMark.observe(on_MarkCheckboxesAp, names='value')
            p.cbBrush.observe(on_BrushCheckboxesAp, names='value')
            p.brush.observe(on_brushesAp, names=['brushing'])
        else:
            p.cbMark.unobserve(on_MarkCheckboxesAp, names='value')
            p.cbBrush.unobserve(on_BrushCheckboxesAp, names='value')
            p.brush.unobserve(on_brushesAp, names=['brushing'])


########################################################################
def on_brushesAp(change):
    do_mws_log_actions(dict(change=change))

    #global bBrushPresentAp

    # This routine has two purposes, to synchronize the Analysis Panel brushes and
    # to display the data values located at the edges of the brushes.

    b = change.owner  # The calling brush

    # Update display only after brushing stops
    if b.brushing: return

    # Synchronize all brushes by setting them to the selected range of the calling brush
    # Each subplot has its own brush and the one being manipulated by the user is the one
    # that generated the call back.  So that the brushes will appear as a single column
    # with the same width on each subplot we set them all to the range selected by the user.
    # This also allows the user to manipulate which ever brush he wants and maintain the
    # appearance of the column while recovering Y-values from each individual subplot.

    # Do nothing if this brush is non-existent
    if b.selected is None or 1 > len(b.selected):
        c.bBrushPresentAp = False
        return
    else:
        c.bBrushPresentAp = True

    for kdata in c.dtPlotsAp:
        cb = c.dtPlotsAp[kdata].brush
        if cb is not b:
            cb.selected = b.selected + 1
            cb.selected = b.selected


    # Recover Y-values at the edges of the brush and display value strings
    postInstrumentValues()

    # Update Analysis Panel time range display
    #
    try:
        bSelLo,bSelHi = [b.selected[i] for i in [0,-1]]
        setTimeValues(c.dtTimeLabelsAp, bSelLo, bSelHi)


    except IndexError as e:
        updateErrorMsg('on_brushesAp:  {}'.format(str(e)))
    # except Exception as e:
    #     updateErrorMsg('on_brushesAp:  {}'.format(str(e)))


########################################################################
def on_MarkCheckboxesAp(change):
    do_mws_log_actions(dict(change=change))
    # Analysis Panel Marker checkbox callback
    #
    # This activates or deactivates the marker of the
    # associated subplot based on the state of the checkbox.
    # dtSubplotChildrenAp[key][2].children[0]  - This is the mark checkbox for the subplot
    # dtSubplotChildrenAp[key][1].children[0].marks[0].marker  - This is the marker property for the subplot figure
    #
    co = change.owner  # This is the calling mark checkbox

    for kdata in c.dtPlotsAp:
        p = c.dtPlotsAp[kdata]
        if co == p.cbMark:
            p.line.marker = co.value and c.dataPointShape or None
            break


########################################################################
def on_BrushCheckboxesAp(change):
    do_mws_log_actions(dict(change=change))
    # Analysis Panel Brush checkbox callback
    #
    # This activates or deactivates the brush
    # of the associated subplot based on the state of the checkbox.

    co = change.owner  # This is the calling brush checkbox
    for kdata in c.dtPlotsAp:
        p = c.dtPlotsAp[kdata]
        if co is p.cbBrush:
           p.figure.interaction = co.value and p.brush or None
           break


########################################################################
def on_DropdownsAp(change):
    do_mws_log_actions(dict(change=change))

    ss_debug = False

    # Analysis Panel subplot Selector Drowdown callback functions
    # Each of the six subplots has a dropdown associated with it that contains
    # keys to a dictionary of Figures and associated widgets
    # This routine is entered when the user selects a new Figure for display from the dropdown.
    #
    # change.owner - is the dropdown object, it is used to identify the subplot requesting a
    #                   new Figure
    # change.new   - is the new value and the key to the dictionary containing Figure object and associated widgets
    #                   to show in the subplot
    # change.old   - is the old value and the key to the dictionary containing Figure object and associated widgets
    #                   to show in the subplot
    #
    #
    if ss_debug: print('\non_DropdownsAp - c.ltVisibleSubplots: {} len:{}\nc.kSubplotKeys: {}'.format(c.ltVisibleSubplots, len(c.ltVisibleSubplots), c.kSubplotKeys))

    for ksp in c.kSubplotKeys:
        if ss_debug: print('on_DropdownsAp - ksp: {}'.format(ksp))
        if change.owner is c.dtDropdownsAp[ksp]:

            # Set Subplot HBox children to new value and show the calling Dropdown to its right.
            #
            #  Below an HBox is created to hold the Dropdown object that called us and it is added
            #  to the new subplot's children.
            #  This has the effect of attaching the Dropdown to the new subplot but having
            #  it retain its position on the User Interface.  For example when we replace the first
            #  subplot the Dropdown that was previously
            #  associated with the old first subplot retains its place on the page.
            c.dtSubplotsAp[ksp].children = c.dtSubplotChildrenAp[change.new] + [wg.HBox(children=[change.owner])]  # Replacement content

            #break

            #print('on_DropdownsAp A - {} old:{} new:{}'.format(c.ltVisibleSubplots, change.old, change.new))

            # Update list of visible subplots
            # for n, i in enumerate(c.ltVisibleSubplots):
            #     if i == change.old:
            #         c.ltVisibleSubplots[n] = change.new
            c.ltVisibleSubplots[int(ksp[-1])] = change.new

            #print('on_DropdownsAp B - {}'.format(c.ltVisibleSubplots))

            break

    ds.updateSubplots(change.new)


########################################################################
def addSubplotChildrenAp(valueLabel, figure, checkboxes):

    loSpValuesAp = wg.Layout(display='flex', flex='1', justify_content='center')
    loSpPlotsAp = wg.Layout(display='flex', flex='8')
    loSpControlsAp = wg.Layout(display='flex', flex='1')

    ltChildren = [wg.HBox(children=[valueLabel], layout=loSpValuesAp),
                    wg.HBox(children=[figure], layout=loSpPlotsAp),
                    wg.VBox(children=checkboxes, layout=loSpControlsAp)]

    return ltChildren


########################################################################
def postInstrumentValues():
    # Recover the data Y-values from the Analysis Panel subplots
    # where the brush intersects the plot on the left and right

    for kdata in c.dtPlotsAp:
        br = c.dtPlotsAp[kdata].brush
        try:
            if br.selected is None or 1 > len(br.selected): continue
            # Read X values from brushes and find the closest valid key
            # This is necessary because the X values returned from the
            # brushes are not necessarilly valid keys in to the data dictionary
            leftIndex = takeClosestIndex(c.dtInstrumentData[kdata].index, br.selected[0])
            rightIndex = takeClosestIndex(c.dtInstrumentData[kdata].index, br.selected[-1])

            if leftIndex==rightIndex:
                if leftIndex: leftIndex -= 1
                else        : rightIndex += 1

            # Fetch the Y-values from the data dictionary that correspond
            # to the X-values obtained from the brushes and format them
            # for display.  Next post the values to the text area associated with
            # the subplot.
            c.dtPlotsAp[kdata].lbValue.value = '<p style="color: red">' + kdata + '</p>' \
                                           + '<p style="margin: 0px 0px 0px 0px; line-height : 1em;">' \
                                           + "{0:.3f}".format(c.dtInstrumentData[kdata].values[leftIndex]) + '<br />' \
                                           + "{0:.3f}".format(c.dtInstrumentData[kdata].values[rightIndex]) + '</p>'
            #updateErrorMsg('postInstrumentValues entered ' + dtPlotsAp[kdata].lbValue.value )

        except IndexError as e:
            updateErrorMsg('postInstrumentValues:  {}'.format(str(e)))
        except Exception as e:
            updateErrorMsg('postInstrumentValues:  {}'.format(str(e)))


########################################################################
bEnableDropdownLast = False
def enableDropdownApCallback(b=True):

    global bEnableDropdownLast

    if b == bEnableDropdownLast: return

    bEnableDropdownLast = b
    if(b):
        for ksp in c.dtDropdownsAp:
            c.dtDropdownsAp[ksp].observe(on_DropdownsAp, names='value')
    else:
        for ksp in c.dtDropdownsAp:
            c.dtDropdownsAp[ksp].unobserve(on_DropdownsAp, names='value')

