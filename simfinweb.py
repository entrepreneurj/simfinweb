#!/usr/bin/env python3
"""
    simfinweb : A module that interfaces with the SimFin low-level web API
"""
from typing import Dict, Any, List, Optional
import numbers
import re
import requests
from rich import print




class APIResponseObject(object):
    """ Returns an object with attributes corresponding to the keys of the
        dict/json passed to it at initialisaton.
        Note: Keys that are number types are prepended with an underline
    """

    def __init__(self, api_response: Dict[str, str]):
        self.keys = []
        for k, v in api_response.items():
            key_name = get_key_name(k)
            self.keys.append(key_name)
            if isinstance(v, dict):
                setattr(self, key_name, APIResponseObject(v))
            elif isinstance(v, list):
                _arr = []
                for member in v:
                    _arr.append(APIResponseObject(member))

                setattr(self, key_name, _arr)

            else:
                setattr(self, key_name, v)

    def __repr__(self) -> str:
        return {k: getattr(self, k) for k in self.keys}.__repr__()

def get_key_name(key: Any) -> Any:
    """ If the key provided is
        - a number: a valid attribute name is returned as a replacement

        - a string: a valid attribute name without hyphens is returned as
        a replacement

        otherwise the original key is returned as the valid attribute name
    """
    if isinstance(key, numbers.Number):
        return "_{}".format(key)
    elif isinstance(key, str):
        return re.sub("-", "_", key)
    else:
        return key

class API:
    """ Wrapper class for the SimFin API
    """

    API_URL = "https://simfin.com/api/v1/{}"


    def __init__(self, key: str) -> None:
        """ Sets API key for API requests
        """
        self.api_key = key

    def get_id_for_ticker(self, ticker: str) -> List[APIResponseObject]:
        """ Returns an array of APIResponseObject, each with attributes
            providing the `name`, `simId` and `ticker` of a potential match
            to the request
            :param ticker: A ticker relating to a public company
        """

        endpoint = "info/find-id/ticker/{}"
        params = {"api-key": self.api_key}
        endpoint_url = endpoint.format(ticker)

        _response = requests.get(self.API_URL.format(endpoint_url), params=params)
        return [APIResponseObject(i) for i in _response.json()]

    def get_id_for_name(self, name: str) -> List[APIResponseObject]:
        """ Returns an array of APIResponseObject, each with attributes
            providing the `name`, `simId` and `ticker` of a potential match
            to the request
            :param name: The name of a public company
        """

        endpoint = "info/find-id/name-search/{}"
        params = {"api-key": self.api_key}
        endpoint_url = endpoint.format(name)

        _response = requests.get(self.API_URL.format(endpoint_url), params=params)
        return [APIResponseObject(i) for i in _response.json()]

    def get_available_statements(self, simfin_id: int) -> APIResponseObject:
        """ Returns an APIResponse instance containing information about the
            available financial statements for the company provided

            :param simfin_id: The SimFin id for the company

            The returned object contains an attribute for each financial statement
            e.g. `[pl, bs, cf]` and an attribute `year_range` that provides the
            earliest and latest years for which financial statements are available

            Each financial statement object contains an attribute for each
            financial year for which the statement is available. A list of
            financial years/attribute names is available in the object's
            `keys` property.

            Each financial year object in a financial statement object contains
            an attribute for each available reporting period during the year.
            These are again available in the financial year object's `keys`
            attribute.

            E.g. `statements.pl._2019.FY` returns an object with the attributes
            `[period, year, calculated]`

            `statements.pl.keys` shows the list of financial years available for the
            Statement of Profit and Loss.

            `statement.pl._2019.keys` shows the list of reporting periods available
            in 2019.
        """

        endpoint = "companies/id/{}/statements/list"
        params = {"api-key": self.api_key}
        endpoint_url = endpoint.format(simfin_id)


        _response = requests.get(self.API_URL.format(endpoint_url), params=params)

        available_statements = APIResponseObject(_response.json())
        years = set()
        for fs in available_statements.keys:
            new_structure = APIResponseObject({})
            instances = getattr(available_statements, fs)
            for i in instances:
                key_name = get_key_name(i.fyear)
                if key_name not in new_structure.keys:
                    setattr(new_structure, key_name, APIResponseObject({}))
                    new_structure.keys.append(key_name)
                    years.add(i.fyear)
                setattr(getattr(new_structure, key_name), i.period, i)
                getattr(new_structure, key_name).keys.append(i.period)
            new_structure.keys.sort()
            setattr(available_statements, fs, new_structure)


        years_sorted: List[int] = sorted(list(years))
        year_range: List[int] = [years_sorted[0], years_sorted[-1]]
        available_statements.year_range = year_range

        return available_statements


    def get_financial_ratios (self, simfin_id: int,
        indicators: Optional[str] = None) -> List[APIResponseObject]:

        """ Returns a list of financial indicators for a specific company

        :param simfin_id: The simId of the specified company
        :param indicators: A comma-separated string of
        [indicators](https://simfin.com/data/help/main?topic=api-indicators)
        """

        endpoint = "companies/id/{}/ratios"
        endpoint_url = endpoint.format(simfin_id)
        params = {
            "api-key": self.api_key,
            "indicators": indicators
        }

        _response = requests.get(self.API_URL.format(endpoint_url),
                                 params=params)

        return [APIResponseObject(i) for i in _response.json()]


    def get_standardised_financial_statement(self,
        simfin_id: int, years: int = 5) -> APIResponseObject:
        """ Returns a set of financial statements for a specified company
        """

        endpoint = "companies/id/{}/statements/original"
        endpoint_url = endpoint.format(simfin_id)

        available_statements = self.get_available_statements(simfin_id)

        # TODO Find a way to get the financial statements for the most sensible
        # period during the most recent financial year if it is incomplete.

        # Find year with most recent full year results
        end_index = -1
        found = False
        fs_years = available_statements.bs.keys
        while not found:
            if "Q4" in getattr(available_statements.bs, fs_years[end_index]).keys:
                found = True
            else:
                end_index -= 1

        # Now we have the most recent full year we need to construct a slice to get
        # the years we need from a list
        slice_end_index = len(fs_years) + end_index + 1
        slice_start_index = 0
        if slice_end_index > years:
            slice_start_index = slice_end_index - years

        valid_year_keys = fs_years[slice_start_index:slice_end_index]

        # We need to turn the year attribute names back into numbers
        valid_years = [int(yr.split("_")[-1]) for yr in valid_year_keys]


        # Here is where we should check to make sure that we haven't already
        # downloaded the financial statements to our database
        # TODO

        # Now we download the financial statements
        # Note we need a request for each statement for each year
        # Total requests here = 3 * years
        for fs in available_statements.keys:
            # iterates over the financial statements

            for yr in valid_years:

                params = {
                    "api-key": self.api_key,
                    "stype": fs,
                    "ptype": "Q4" if fs == "bs" else "FY",
                    "fyear": yr
                    }
                _response = requests.get(self.API_URL.format(endpoint_url),
                                         params=params)

                # Need to be careful with the metatprogramming magic here
                # After all we don't want each individual financial statement
                # result wrapped in an APIResponseObject instance.
                # TODO

                # TODO finish this function
                raise Exception("Not Implemented")
                return


def cli():
    """ Command line interface
    """
    return "WIP"
