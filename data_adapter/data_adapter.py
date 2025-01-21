#!/usr/bin/env python3

import abc


class DataAdapter(abc.ABC):
    @property
    @abc.abstractmethod
    def data(self):
        """Simple property for getting all internal data.

        Returns:
            The data as read from file.
        """
        pass
