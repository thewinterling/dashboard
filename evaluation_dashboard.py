#!/usr/bin/env python3

import argparse
import dash
from dash import dcc
from dash import html
import glob
import importlib
import inspect
import os
from pathlib import Path

from evaluation_semantics.base import EvaluationSemanticsBase


def available_data_adapters():
    folder = Path(__file__).parent / "data_adapter"
    adapters = {}
    files = folder.glob("*.py")
    for file in files:
        if file.name.startswith("_") or file.name == "data_adapter.py":
            continue
        class_name = file.stem.title().replace("_", "")
        adapters[class_name] = file.stem
    return adapters


def _parse_args():
    """
    Define and parse the command line arguments.
    @return: argparse.Namespace Command line arguments specified by the user.
    """
    parser = argparse.ArgumentParser(description="Evaluation dashboard")
    parser.add_argument(
        "-i",
        "--input_file",
        type=Path,
        required=True,
        default=None,
        help="Input file to evaluate.",
    )
    parser.add_argument(
        "-da",
        "--data_adapter",
        choices=available_data_adapters().keys(),
        default=None,
        required=True,
        help="Data Adapter to use.",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8050,
        help="The port to be used by the dashboard.",
    )
    return parser.parse_args()


def get_all_available_evaluations():
    # Dynamically loading all available evaluations
    EVALUATIONS_DIRECTORY_NAME = "evaluation_semantics"
    evaluations_directory = Path(__file__).parent / EVALUATIONS_DIRECTORY_NAME
    files = glob.glob(str(evaluations_directory / "*.py"))
    module_names = [os.path.splitext(os.path.basename(module))[0] for module in files]
    evaluations = list()
    for module_name in module_names:
        # Ignoring 'private' modules and the `base` module.
        if module_name.startswith("_") or "base" in module_name:
            continue

        # Importing like 'import evaluation_semantics.measurement_count'
        module = importlib.import_module(f"{EVALUATIONS_DIRECTORY_NAME}.{module_name}")

        # Filter out all members which are not sub classes of EvaluationSemanticsBase.
        for _, member_type in inspect.getmembers(module):
            if not inspect.isclass(member_type):
                continue
            if not issubclass(member_type, EvaluationSemanticsBase):
                continue
            evaluations.append(member_type(adapter, mode="dashboard"))
    return evaluations


if __name__ == "__main__":
    args = _parse_args()

    # Dynamically import import the adapters (i.e. this code does not need to be changed, when
    # adding a new DataAdapter implementation for another data source.
    adapters = available_data_adapters()
    module_name = adapters[args.data_adapter]
    imported_module = importlib.import_module(f"data_adapter.{module_name}")
    imported_class = getattr(imported_module, args.data_adapter)
    adapter = imported_class(args.input_file)  # Instantiate the adapter here.

    all_available_evaluations = get_all_available_evaluations()
    evaluation_dropdown = [{"value": a.get_name(), "label": a.get_name()} for a in all_available_evaluations]
    html_container = list()

    app = dash.Dash(__name__)
    app.layout = html.Div(
        children=[
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="three columns div-user-controls",
                        children=[
                            html.H1("Evaluation Dashboard"),
                            html.P(
                                """This dashboard visualizes various fields of the data. It can be used to get
                                    an overall understanding of the measurements. """
                            ),
                            html.P("Pick one or more evaluation options from the dropdown below."),
                            dcc.Dropdown(
                                id="dropdown-selection-evaluation",
                                multi=True,
                                options=evaluation_dropdown,
                            ),
                        ],
                    ),
                    html.Div(
                        className="nine columns bg-grey",
                        id="evaluation-container",
                        children=html_container,
                        # This is where the html containers for each individual evaluation
                        # will be added to.
                    ),
                ],
            )
        ]
    )

    for e in all_available_evaluations:
        # Please be aware the order of the following two method calls must not be changed.
        e.create_html(html_container)
        e.register(app)

    app.run_server(debug=True, port=args.port)
