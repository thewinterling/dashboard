from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.graph_objects as go
import numpy as np

import evaluation_semantics.base as base


class EchoPropertyHistogramEvaluation(base.EvaluationSemanticsBase):
    def __init__(self, reader, mode="notebook"):
        super().__init__(reader, mode)

        self.xlabel_mapping = {
            "echo_distance": "Echo distance[m]",
            "significance": "Significance",
            "amplitude": "Amplitude [?]",
        }

        self.xtick_text_mapping = {
            "echo_distance": None,
            "significance": ["LOW", "MEDIUM", "HIGH", "VERY_HIGH", "UNKNOWN"],
            "amplitude": None,
        }

    def get_info_text(self):
        return html.P("Show a histogram for the echo distances received over the whole file.")

    def get_name(self):
        return "Echo Property Histogram"

    def get_figure(self, echo_property_args):
        echo_property = echo_property_args[0]
        echoes = self.adapter.echoes
        columns = self.adapter.echoes.columns

        if echo_property not in columns:
            return list()

        tick_text = self.xtick_text_mapping[echo_property]
        layout = go.Layout(
            xaxis_rangeslider_visible=True,
            xaxis_rangeslider_thickness=0.05,
            xaxis_title="{tt}".format(tt=self.xlabel_mapping[echo_property]),
            yaxis_title="[N] measurements",
        )
        if tick_text:
            layout.update(
                xaxis_tickmode="array",
                xaxis_tickvals=np.arange(len(tick_text)),
                xaxis_ticktext=tick_text,
            )
            figure = go.Figure(
                data=[
                    go.Histogram(
                        x=echoes[echo_property],
                        nbinsx=len(tick_text),
                        marker={"color": base.UNIFIED_COLOR_SCHEME[0]},
                    ),
                ],
                layout=layout,
            )
        else:
            figure = go.Figure(
                data=[
                    go.Histogram(
                        x=echoes[echo_property],
                        marker={"color": base.UNIFIED_COLOR_SCHEME[0]},
                    )
                ],
                layout=layout,
            )

        if self.mode == "dashboard":
            base.unify_layout(figure)
            figure.update_layout(autosize=False, width=base.DASHBOARD_WIDTH)
            return dcc.Graph(figure=figure)
        elif self.mode == "notebook":
            figure.update_layout(autosize=False, width=base.NOTEBOOK_WIDTH)
            return figure

    def create_html(self, element):
        columns = self.adapter.echoes.columns
        options = [{"value": c, "label": c} for c in columns]

        self.create_default_heading_html(element)
        self.create_default_info_html(element)
        element.append(
            html.Div(
                [
                    dcc.Dropdown(
                        id="dropdown-echo-property",
                        multi=False,
                        options=options,
                        style=dict(width=40),
                    )
                ],
                style={"width": "350px", "margin-left": "15px"},
            )
        )
        self.create_default_figure_html(element)

    def register(self, app):
        def _function_return_simple_figure(selected_dropdown_values, echo_property_value):
            return base.return_data_or_empty_list(selected_dropdown_values, self, self.get_figure, echo_property_value)

        # Default callbacks
        self.register_default_name(app)
        self.register_default_info(app)

        # Custom callbacks start here
        app.callback(
            Output("{name}-figure".format(name=self.get_name()), "children"),
            [
                Input("dropdown-selection-evaluation", "value"),
                Input("dropdown-echo-property", "value"),
            ],
        )(_function_return_simple_figure)

        @app.callback(
            Output(component_id="dropdown-echo-property", component_property="style"),
            [
                Input(
                    component_id="dropdown-selection-evaluation",
                    component_property="value",
                )
            ],
        )
        def show_hide_element(selected_dropdown_values):
            if selected_dropdown_values and self.get_name() in selected_dropdown_values:
                return {"display": "block"}
            else:
                return {"display": "none"}
