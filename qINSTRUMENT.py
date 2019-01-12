from qSUBPLOT import SUBPLOT

class INSTRUMENT(SUBPLOT):
    """S. Sackett 3/26/2018
    instrument.py

    This class is a companion to the Filter class.  It is essentially
    an null-filter that is used to plot data taken directly from
    the input stream.

    Data is provided in the dtInstrumentData dictionary.
    The contents of dtInstrumentData is a set of Pandas Series keyed by
    a mnemonic for the data type, the keys are:
        HWS     - Horizontal wind speed
        VWS     - Vertical wind speed
        WD      - Wind direction
        AT      - Air temperature
        PRE     - Pressure
        PTMP    - Pressure Temperature

        Example, to access the Pandas Series containing Wind Direction use:
            dtInstrumentData[kWD]
    """

    # Initialize the Instrument Class
    # Constructor parameters:
    #   series            - A Pandas Series containing instrument data
    #   xScale            - the bqplot.Scale object to use as the X-scale
    #   name              - The key into dtInstrumentData that retrieves the Pandas Series we are using.
    #   plotColor         - The color used to plot the data.
    #
    def __init__(self, series, xScale, name, plotColor):
        self._inputSeries = series
        self.xScale = xScale
        self.name = name
        self.plotColor = plotColor

        SUBPLOT.__init__(self)  # Initialize superclass

    # Define null filter for this data
    def filter(self):
        self._inputSeries.name = self.name
        return self._inputSeries

