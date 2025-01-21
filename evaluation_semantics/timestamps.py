from dash import dcc
from dash import html
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import evaluation_semantics.base as base


def _difference_to_last(index, container):
    if index == 0:
        return 0
    if index >= len(container):
        return 0
    return container[index] - container[index - 1]


def _get_offset(data):
    return data[data > 0.0][0]


class TimestampEvaluation(base.EvaluationSemanticsBase):
    def __init__(self, reader, mode="notebook"):
        super().__init__(reader, mode)

    def get_info_text(self):
        infos = list()
        infos.append(
            html.P(
                "This section is to get a quick overview of the different timestamps we have available in the example data."
            )
        )
        infos.append(
            html.P(
                "Header timestamp: only used in fusion (i.e. plugin_runnable.h) to determine if data are in sequential order. "
            )
        )
        infos.append(
            html.P(
                "Echoes/Reflex point timestamp: Functional timestamp that will be used inside the sensor plugin (i.e. for the association). "
                "Note that echoes and reflex point timestamps might not be available in every step as it requires at least one valid data point. "
                "As it is quite normal to have no reflex point available at a particular time, the number of timestamp ticks in the plot are "
                "less than for the header timestamp. Those values are filled with zeros resulting in gaps in the plots."
            )
        )
        return infos

    def get_name(self):
        return "Timestamps"

    def get_figure(self):
        timestamps_echoes = np.array(self.adapter.timestamps)

        # Get the relative difference to the previous timestamp. This makes it easier to detect
        # out of sequence measurements in the plots.
        difference = [_difference_to_last(i, timestamps_echoes) for i in range(len(timestamps_echoes))]

        # Subtract the first element from all elements since one wouldn't see a difference in the plots.
        # Make sure that we don't subtract anything from the zero-padded values where no valid echo/reflex point
        # was available.
        offset = _get_offset(timestamps_echoes)
        timestamps_echoes[timestamps_echoes > 0] -= offset

        figure = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                "Out-of-sequence timestamps",
                "Echo timestamps",
            ),
        )
        figure.append_trace(
            go.Bar(
                y=difference,
                marker={"color": base.UNIFIED_COLOR_SCHEME[0]},
                name="Difference to previous header timestamp",
            ),
            row=1,
            col=1,
        )
        figure.append_trace(
            go.Bar(
                y=timestamps_echoes,
                marker={"color": base.UNIFIED_COLOR_SCHEME[0]},
                name="Echo timestamps",
            ),
            row=2,
            col=1,
        )

        if self.mode == "dashboard":
            base.unify_layout(figure)
            figure.update_layout(autosize=False, width=base.DASHBOARD_WIDTH, height=base.PLOT_HEIGHT)
            return dcc.Graph(figure=figure)
        elif self.mode == "notebook":
            figure.update_layout(autosize=False, width=base.NOTEBOOK_WIDTH, height=base.PLOT_HEIGHT)
            return figure
