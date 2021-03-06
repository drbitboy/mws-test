import bqplot as bq
import ipywidgets as wg
import qconfig as c

class SUBPLOT:
    """
    subplot.py
    S. Sackett 3/25/2018

    Subplot is a super class to Filter and Instruments
    It is used to hold the attributes required to produce a
    subplot in the Analysis Panel of MWS_Analyst.

    Subplot is initialized by one of its subclasses (Filter or Instrument),
    Some of its properties are generated by the subclass.
    """

    def __init__(self):
        self.series = self.filter()  # Get series from subclass
        self._yScale = bq.LinearScale()  # Y axis scale, used for autoranging

        # Size and shape of Analysis Panel Recovered Values Lables
        self._loLbAp = wg.Layout(display='flex',
                                 align_content='center',
                                 width='70px',
                                 height='auto',
                                 margin='0px 0px 0px 10px',
                                 padding='0px 0px 0px 0px'
                                 )
        #self.lbValue = wg.HTML(value=self.name, layout=self._loLbAp)
        self.lbValue = wg.HTML(value='<p style="color: red">' + self.name + '</p>', layout=self._loLbAp)

        # Size and shape of Analysis Plot Checkboxes
        self._loCbAp = wg.Layout(display='flex',
                                 width='auto',
                                 height='auto',
                                 margin='0px 0px 0px 5px',
                                 padding='0px 0px 0px 0px'
                                 )
        self.cbBrush = wg.Checkbox(value=False, description='Brush',
                                   indent=False, layout=self._loCbAp)
        self.cbMark = wg.Checkbox(value=False, description='Mark',
                                  indent=False, layout=self._loCbAp)

         #Setup line object for Analysis Plot figure
        self.line = bq.Lines(x=self.series.index, y=self.series.values,
                             scales={'x': self.xScale, 'y': self._yScale},
                             labels=[self.name], colors=[self.plotColor],
                             marker_size=c.dataPointSize,
                             marker=None,
                             tooltip=bq.Tooltip(fields=['y'], formats=['.2f'], show_labels=False))

        #self.ltLtstMarks = []

        # Size and shape of Analysis Plot figure
        self._loAp = wg.Layout(display='flex',
                               flex='10',
                               height='auto',
                               margin='0px 0px 0px 0px',
                               padding='0px 0px 0px 0px'
                               )

        # Axis, Controls tick marks and grid for Analysis Plot figure
        self._axis = bq.Axis(orientation='vertical', side='left', scale=self._yScale,
                             num_ticks=5, grid_lines='solid', grid_color='Bisque')
        self._margAp = {'top': 6, 'bottom': 6, 'right': 6, 'left': 40}  # Margins around Analysis subplots figures
        self.figure = bq.Figure(marks=[self.line],
                                 axes=[self._axis],
                                 layout=self._loAp,
                                 min_aspect_ratio=.01,
                                 max_aspect_ratio=100,
                                 fig_margin=self._margAp,
                                 #title = self.name,
                                 background_style={'fill': 'aliceblue'})

        self.brush = bq.interacts.BrushIntervalSelector(scale=self.xScale,
                                                         marks=[self.line],
                                                         color='Firebrick')

    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
