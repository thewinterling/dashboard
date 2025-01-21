#!/usr/bin/env python3

import abc
from dash.dependencies import Input, Output
from dash import html
import plotly.express as px
from data_adapter.data_adapter import DataAdapter


class EvaluationSemanticsBase(abc.ABC):
    def __init__(self, adapter: DataAdapter, mode: str):
        """Base class constructor to set reader and the mode.

        Args:
            reader: The data reader holding the actual data for evaluation.
            mode: Mode of evaluation, either 'dashboard' or 'notebook'.
        """
        self._SUPPORTED_MODES = set(["dashboard", "notebook"])

        self.adapter = adapter
        self.mode = mode
        assert (
            mode in self._SUPPORTED_MODES
        ), f"Specified mode '{mode}' is not supported. Must be one of {str(self._SUPPORTED_MODES)}."

    @abc.abstractmethod
    def get_name(self):
        """Abstract method to be overridden to return the name of the evaluation section."""
        pass

    @abc.abstractmethod
    def get_info_text(self):
        """Abstract method to be overridden to return all info text that should be displayed alongside the plots."""
        pass

    @abc.abstractmethod
    def get_figure(self):
        """Abstract method to be overridden to return the (plotly) figure to be displayed."""
        pass

    def create_html(self, element):
        """Creates the default html elements. If anything else is needed this method should be overridden by its subclass.
        Partial use of default creation (in the subclass) is possible as well via direct call to the respective method.

        Args:
            element: The list to be added as 'children' in the overall html structure lateron.
        """
        self.create_default_heading_html(element)
        self.create_default_info_html(element)
        self.create_default_figure_html(element)

    def create_default_heading_html(self, element):
        """Creates the default html element for the 'heading' section only.

        Args:
            element: The list to be added as 'children' in the overall html struture lateron.
        """
        element.append(html.H3(id="{name}-heading".format(name=self.get_name())))

    def create_default_info_html(self, element):
        """Creates the default html element for the 'info' section only.

        Args:
            element: The list to be added as 'children' in the overall html struture lateron.
        """
        element.append(html.H3(id="{name}-info".format(name=self.get_name())))

    def create_default_figure_html(self, element):
        """Creates the default html element for the 'figure' section only.

        Args:
            element: The list to be added as 'children' in the overall html struture lateron.
        """
        element.append(html.H3(id="{name}-figure".format(name=self.get_name())))

    def register(self, app):
        """Creates the default callbacks matching the default html elements as created via `create_html`.
        If anything else is needed this method should be overridden by its subclass.
        Partial use of default creation (in the subclass) is possible as well via direct call to the respective method.

        Args:
            app: The dash app where the callbacks need to be registered.
        """
        self.register_default_name(app)
        self.register_default_info(app)
        self.register_default_figure(app)

    def register_default_name(self, app):
        """Creates the default callback matching the default html element as created via `create_html` or
        `create_default_name_html`.

        Args:
            app: The dash app where the default `name` callback needs to be registered.
        """

        def _function_return_name(selected_dropdown_values):
            return return_data_or_empty_list(selected_dropdown_values, self, self.get_name)

        app.callback(
            Output("{name}-heading".format(name=self.get_name()), "children"),
            [Input("dropdown-selection-evaluation", "value")],
        )(_function_return_name)

    def register_default_info(self, app):
        """Creates the default callback matching the default html element as created via `create_html` or
        `create_default_info_html`.

        Args:
            app: The dash app where the default `info` callback needs to be registered.
        """

        def _function_return_info(selected_dropdown_values):
            return return_data_or_empty_list(selected_dropdown_values, self, self.get_info_text)

        app.callback(
            Output("{name}-info".format(name=self.get_name()), "children"),
            [Input("dropdown-selection-evaluation", "value")],
        )(_function_return_info)

    def register_default_figure(self, app):
        """Creates the default callback matching the default html element as created via `create_html` or
        `create_default_figure_html`.

        Args:
            app: The dash app where the default `figure` callback needs to be registered.
        """

        def _function_return_simple_figure(selected_dropdown_values):
            return return_data_or_empty_list(selected_dropdown_values, self, self.get_figure)

        app.callback(
            Output("{name}-figure".format(name=self.get_name()), "children"),
            [Input("dropdown-selection-evaluation", "value")],
        )(_function_return_simple_figure)


UNIFIED_COLOR_SCHEME = px.colors.sequential.Bluyl_r
DIVERGING_COLOR_SCHEME = px.colors.diverging.RdBu
DASHBOARD_WIDTH = 1400
NOTEBOOK_WIDTH = 850
PLOT_HEIGHT = 1000


def unify_layout(figure):
    """Unifies the look of the plots for the dashboard.

    Args:
        figure: plotly figure to be styled.
    """
    template = "plotly_dark"
    layout = {
        "plot_bgcolor": "rgba(255, 255, 255, 0.5)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    }
    figure.update_layout(layout, template=template)


def return_data_or_empty_list(ui_value, instance, method, *args):
    """Returns the data as provided by the return value of `method` if the `instance`-name is in `ui_value`
    (which corresponds to the dropdown menu).
    This function should be used for the callbacks.

    Args:
        ui_value: The list of values as given from the main dropdown menu.
        instance: The actual class to be used for name retrieval.
        method: The method that should be called.
        *args: Further arguments that need to be passed to `method` (without any checks).
    Returns:
        An empty list if the specified evaluation has not been selected in the dashboard else
        the data as returned via the callable `method`.
    """
    if ui_value is None:
        return list()
    if instance.get_name() in ui_value:
        if len(args) > 0:
            return method(args)
        else:
            return method()
    return list()
