import bqplot as bq
import pandas as pd
import ipywidgets as wg

import qconfig as c


########################################################################
def compress_four(lt):
    if not lt: return lt
    x0,xlo,xhi,x1 = lt
    if xlo==xhi: return lt[:1]
    if x0==xhi: lt.pop(2)
    elif x0==xlo: lt.pop(1)
    if x1==lt[-1]: lt.pop()
    return lt


########################################################################
def compress_series(series,xScale,compress_to=0):
    """
    Compress a pandas.Series to plot in [compress_to] pixel columns

    """

    ### Do nothing unless compress_to i a positive integer
    if (not isinstance(compress_to,int)) or compress_to < 1: return series

    ### If series is already smallter than compress_to, return it as is
    if len(series)<=compress_to: return series

    try:
        ### Get the xScale limits
        xmin,xmax = xScale.min,xScale.max
        if (xmin is None) or (xmax is None):
            xmin,xmax = series.index.min(), series.index.max()
    except:
        import traceback
        traceback.print_exc()
        return series

    ### Set the step size:  width per column over compress_to columns
    ### between xmin and xmax; return original series if xmax<=xmin
    step = (xmax - xmin) / float(compress_to)
    if step <= 0.0: return series

    ### halfstep:  distence from column boundary to center of column
    ### sub_series:  series subset between xmin and xmax
    halfstep = step / 2.0
    sub_series = series.loc[xmin:xmax]

    ### Initialize output index and values as empty lists
    idxs,vals = list(),list()


    ### Loop initialization:
    ### - Set upper boundary of first column below xmin; boundary will
    ###   be incremented as needed
    ### - Set four_vals to False; will become 4-element list within loop
    ###   - four_vals:  vEntrance, vLow, vHigh, vExit; within column
    xtop = xmin - step
    four_vals = list()

    ### Loop over indices and values in series subset
    for idx,val in sub_series.iteritems():

        if four_vals and idx < xtop:
            ### Value less than upper limit of column; add to four_vals
            ### - As exit value
            four_vals[3] = val
            ### - As minimum value if it is such
            if val < four_vals[1]: four_vals[1] = val
            ### - Or as maximum value if it is such
            elif val > four_vals[2]: four_vals[2] = val
            ### Continue to next item in series subset
            continue

        if four_vals:
            ### idx is >= xtop; add four_vals to overall list
            compressed_vals = compress_four(four_vals)
            vals.extend(compressed_vals)
            ### Use centerline of column for corresponding indices
            idxs.extend([xtop-halfstep] * len(compressed_vals))

        ### Incrment xtop by step until is exceeds current value
        while idx >= xtop: xtop += step
        ### Add current value four times to four_vals (entrance to exit)
        four_vals = [val]*4

    if four_vals:
        ### Add last four_vals to overall list and indies
        compressed_vals = compress_four(four_vals)
        vals.extend(compressed_vals)
        idxs.extend([xtop-halfstep] * len(compressed_vals))

    ### Return compressed list
    return pd.Series(data=vals,index=idxs)


########################################################################
class SELECTOR_SERIES:
    """
    S. Sackett 3/26/2018
    selectorSeries.py

    SelectorSeries represents a single data series to be used in conjunction with the
    DataSelector.
    """
    def __init__(self, series, name, xScale, plotColor,compress_to=0):
        self._yScale = bq.LinearScale()  # Y axis scale, used for autoranging
        self.series = series
        self.name = name
        self.xScale = xScale
        self.plotColor = plotColor

        self._loCbDs = wg.Layout(display='flex',
                                 width='auto',
                                 height='auto',
                                 margin='10px 0px 5px 5px',
                                 padding='0px 5px 0px 5px',
                                 border='double '+plotColor,
                                 border_width='1px'
                                 )

        self.cbShow = wg.Checkbox(value=False, description=self.name,
                                  indent=False, layout=self._loCbDs)

        ### Reduce the number of points, compress-to is positive
        compressed_series = compress_series(self.series
                                           ,self.xScale
                                           ,compress_to=compress_to
                                           )

        self.line = bq.Lines(x=compressed_series.index, y=compressed_series.values,
                             scales={'x': self.xScale, 'y': self._yScale},
                             labels=[self.name], colors=[self.plotColor],
                             name=self.name, visible=False,
                             marker_size=c.dataPointSize,
                             marker=None)

    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
