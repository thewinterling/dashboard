from dash import dcc
from dash import html
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats

import evaluation_semantics.base as base


def spearmanr_correlation(x, y):
    return stats.spearmanr(x, y)[0]


def spearmanr_pvalues(x, y):
    return stats.spearmanr(x, y)[1]


class CorrelationMatrixEvaluation(base.EvaluationSemanticsBase):
    def __init__(self, reader, mode="notebook"):
        super().__init__(reader, mode)

    def get_info_text(self):
        return html.P("Show a simple plot of the correlation matrix of all available measurements.")

    def get_name(self):
        return "Correlation Matrix"

    def get_figure(self):
        echoes = self.adapter.echoes

        correlation = echoes.corr(method=spearmanr_correlation)
        pvalues = echoes.corr(method=spearmanr_pvalues)

        mask = np.zeros_like(correlation, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        mask[np.diag_indices(len(mask))] = False
        correlation_upper_triangle = correlation.mask(mask)

        length = len(correlation)
        column_names = correlation_upper_triangle.columns.values
        hovertext = [
            [
                f"correlation({column_names[i]}, {column_names[j]})= {correlation.iloc[i][j]:.2f}, p_value= {pvalues.iloc[i][j]:.3f}"
                if i >= j
                else ""
                for j in range(length)
            ]
            for i in range(length)
        ]

        heat = go.Heatmap(
            z=correlation_upper_triangle,
            x=column_names,
            y=column_names,
            xgap=1,
            ygap=1,
            colorscale=base.DIVERGING_COLOR_SCHEME,
            colorbar_thickness=20,
            colorbar_ticklen=3,
            zmid=0,
            hovertext=hovertext,
            hoverinfo="text",
        )
        layout = go.Layout(
            title_text="Spearman Correlation Matrix",
            title_x=0.5,
            width=800,
            height=800,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            yaxis_autorange="reversed",
        )
        figure = go.Figure(data=[heat], layout=layout)

        if self.mode == "dashboard":
            base.unify_layout(figure)
            figure.update_layout(autosize=False, width=base.DASHBOARD_WIDTH, height=base.PLOT_HEIGHT)
            return dcc.Graph(figure=figure)
        elif self.mode == "notebook":
            figure.update_layout(autosize=False, width=base.NOTEBOOK_WIDTH, height=base.PLOT_HEIGHT)
            return figure
