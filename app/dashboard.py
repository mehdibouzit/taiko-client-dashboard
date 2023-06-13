import panel as pn, holoviews as hv 

from utils.node import Node
from utils.prover import Prover
from utils.proposer import Proposer

pn.config.sizing_mode = 'stretch_width'
hv.extension('bokeh', logo=False)
hv.renderer('bokeh').theme = 'caliber'

node = Node()
prover = Prover()
proposer = Proposer()

prover_status = pn.indicators.BooleanStatus(width=10, height=10, value=True, color='success')
proposer_status = pn.indicators.BooleanStatus(width=10, height=10, value=True, color='warning')
status = pn.GridBox('', '', ncols=2)
status.extend(('Prover', prover_status))
status.extend(('Proposer', proposer_status))


pn.template.FastListTemplate(
    site="Panel", 
    title="Taiko Client Dashboard", 
    logo='doc/taiko-icon-mono.png',
    favicon='doc/taiko-icon-wht.png',
    accent_base_color='#ff00ff',
    header_neutral_color='#ff00ff',
    neutral_color ='#ff00ff',
    header_background ='#ff00ff',
    header_accent_base_color ='#ff00ff',
    sidebar=[*status], 
    main=[
        pn.Tabs(
            ('Node', node.view),
            ('Prover', prover.view),
            ('Proposer', proposer.view),
        )
    ]
).servable();
