from dash import dcc
from dash import html
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import evaluation_semantics.base as base


class MeasurementCountEvaluation(base.EvaluationSemanticsBase):
    def __init__(self, reader, mode="notebook"):
        super().__init__(reader, mode)

    def get_info_text(self):
        return html.P("Simple plot to show how many measurements are available per sample.")

    def get_name(self):
        return "Measurement Count"

    def get_figure(self):
        number_of_echoes = np.array([len(x) for x in self.adapter.echoes])
        number_of_points = np.array([len(x) for x in self.adapter.points])

        x_echoes = np.arange(len(number_of_echoes))
        x_reflex_points = np.arange(len(number_of_points))

        assert len(x_echoes) == len(x_reflex_points)
        MAX_SAMPLES_PER_PLOT = 500
        number_of_subplots = int(np.ceil(len(number_of_echoes) / MAX_SAMPLES_PER_PLOT))

        figure = make_subplots(rows=number_of_subplots, cols=1)

        for i in range(number_of_subplots):
            start = i * MAX_SAMPLES_PER_PLOT
            end = i * MAX_SAMPLES_PER_PLOT + MAX_SAMPLES_PER_PLOT
            figure.append_trace(
                go.Bar(
                    x=x_echoes[start:end],
                    y=number_of_echoes[start:end],
                    marker={"color": base.UNIFIED_COLOR_SCHEME[0]},
                    name="Subplot {i}: Echoes".format(i=i),
                ),
                row=i + 1,
                col=1,
            )
            figure.append_trace(
                go.Bar(
                    x=x_reflex_points[start:end],
                    y=number_of_points[start:end],
                    marker={"color": base.UNIFIED_COLOR_SCHEME[3]},
                    name="Subplot {i}: Reflex Points".format(i=i),
                ),
                row=i + 1,
                col=1,
            )

        figure.update_layout(
            barmode="stack",
            title="Number of valid measurements per sample - mean(echoes) = {me:.2f}, mean(reflex_points) = {mrp:.2f}".format(
                me=np.mean(number_of_echoes), mrp=np.mean(number_of_points)
            ),
        )
        figure.update_yaxes(title_text="[N] measurements", title_standoff=0)
        figure.update_xaxes(title_text="[N] received packages", title_standoff=0)

        if self.mode == "dashboard":
            figure.update_layout(autosize=False, width=base.DASHBOARD_WIDTH, height=base.PLOT_HEIGHT)
            base.unify_layout(figure)
            return dcc.Graph(figure=figure)
        elif self.mode == "notebook":
            figure.update_layout(autosize=False, width=base.NOTEBOOK_WIDTH, height=base.PLOT_HEIGHT)
            return figure
