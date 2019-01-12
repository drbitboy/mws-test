import ipywidgets as wg
import qconfig as c

########################################################################
def initUserSurface():
    ################ Begin User Display Surface ####################
    #
    # The display surface contains the various Figures (plots) and controls
    # the comprise the user interface.  The layout and placement of the
    # visual elements is managed using the Flexbox model.
    ##################################################################

    # File Selector label
    lbFileSelector = wg.Label('Select Sol: ', layout=c.wglo(**c.dtLoFaa0))

    ########################
    # Analysis Panel
    #

    # Make a container for the Analysis Panel Time display
    hbTimeAp = wg.HBox([c.dtTimeLabelsAp[c.kSCLK]
                       ]
                      , layout=c.wglo(display='flex',
                                      justify_content='space-between',
                                      width='auto',
                                      height='auto',
                                      margin='0px 0px 10px 0px')
                      )
    # VBox to contain the full set of Analysis Panel subplots.
    vbSubplotsAp = wg.VBox(children=[c.dtSubplotsAp[ksp] for ksp in c.kSubplotKeys]
                           , layout=c.wglo(**c.dtLoFaa0, align_content='stretch'))

    # Make a container for the Analysis Panel Time Display and Subplots
    vbTimeSubplotAp = wg.VBox(children=[hbTimeAp, vbSubplotsAp], layout=c.wglo(**c.dtLoFaa0, border='solid lightblue'))

    # Make container for all Analysis Panel Elements
    hbAnalysisPanelAp = wg.HBox(children=[vbTimeSubplotAp], layout=c.wglo(**c.dtLoFaa0))

    # End Analysis Panel
    ########################


    ########################
    # Overview Panel
    #
    # Make container for Overview panel
    vbVerticalSpacer = wg.VBox(layout=c.wglo(height='auto', width='2px', border='2px solid lightblue'))
    hbTimeOv = wg.HBox(
        [c.dtTimeLabelsOv[c.kSCLK], c.dtTimeLabelsOv[c.kLMST], c.dtTimeLabelsOv[c.kUTC]],
        layout=c.wglo(width='auto', justify_content='space-between'))

    hbOvControls = wg.HBox(children=[c.lbSourceLabel, c.bitSpan, c.ddFileSelector, c.dtOverviewButtons['load'], vbVerticalSpacer, c.bitDecimation, c.txCurrentRange])

    vbFigOv = wg.VBox(children=[hbTimeOv, c.figOv, hbOvControls],
                      layout=c.wglo(display='flex', width='auto', border='solid lightblue'))

    hbOverviewPanel = wg.HBox(children=[vbFigOv],layout=c.wglo(display='flex', width='auto'))
    # End Overview Panel
    ########################


    ########################
    # Data Selector
    #
    # Make a container for the Data Selector Checkboxes, to select which
    # series are to displayed in the Data Selector
    hbCheckboxesDs = wg.HBox(children=[], layout=c.wglo(width='875px', flex_flow='row wrap'))

    # Make a container for the Data Selector Time display.
    hbTimeDs = wg.HBox(
        [c.dtTimeLabelsDs[c.kSCLK], c.dtTimeLabelsDs[c.kLMST], c.dtTimeLabelsDs[c.kUTC]],
        layout=c.wglo(width='auto', justify_content='space-between'))

    vbFigDs = wg.VBox(children=[hbTimeDs, c.figDs, hbCheckboxesDs],
                      layout=c.wglo(display='flex', width='auto', border='solid lightblue'))


    vbButtonsDs = wg.VBox(children=[c.cbMarkDs, c.lbWaitDs, c.bn95sHBoxDs]
                         , layout=c.wglo(display='flex'
                                        , width='100px'
                                        , height='auto'
                                        , margin='0px 0px 0px 0px'
                                        , padding='0px 0px 0px 0px'
                                        , border='solid lightblue'
                                        , justify_content='center'
                                        )
                         )


    hbDataSelector = wg.HBox(children=[vbFigDs, vbButtonsDs]
                            ,layout = c.wglo(display='flex', width='auto')
                            )
    # End Data Selector
    ########################


    vbRegionSpacer = wg.VBox(layout=c.wglo(height='10px', width='auto'))#, border='5px solid lightblue'))

    c.lbErrorMsg = wg.Label(c.globalErrorMsg, layout=c.wglo(**c.dtLoFaa0))
    c.lbErrorTitle = wg.Label('Messages:', layout=wg.Layout(display='flex', width='10em'))
    hbErrorMsg = wg.HBox(children=[c.lbErrorTitle, c.lbErrorMsg], layout=wg.Layout(display='flex', border='solid salmon'))

    # Make a container for the User Display Surface that contains both the
    # Analysis Panel and Data Selector visual elements
    vbUserSurface = wg.VBox(children=[hbErrorMsg, vbRegionSpacer,
                                      hbOverviewPanel, vbRegionSpacer,
                                      hbDataSelector, vbRegionSpacer,
                                      hbAnalysisPanelAp], layout=c.wglo(**c.dtLoFaa0))


    ############### End User Display Surface ######################
    ###############################################################

    return vbUserSurface, hbCheckboxesDs

