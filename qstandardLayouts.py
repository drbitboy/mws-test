import ipywidgets as wg

def initStandardLayouts():
    """Initialize some standard layouts"""
    wglo = wg.Layout
    dtLoFaa0 = dict(display='flex'
                   ,width='auto'
                   ,height='auto'
                   ,margin='0px 0px 0px 0px'
                   )
    dtLoFaa0Border = dict(border='solid lightgray')
    dtLoFaa0Border.update(dtLoFaa0)

    return wglo, dtLoFaa0, dtLoFaa0Border
