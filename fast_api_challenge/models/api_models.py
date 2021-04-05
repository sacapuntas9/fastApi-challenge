"""
Pydantic models that the Api-layer uses
"""

from pydantic import BaseModel


class ApiUser(BaseModel):
    name: str


class Token(BaseModel):
    token: str
    type: str


class TokenRequestModel(BaseModel):
    name: str


class SummaryResponseModel(BaseModel):
    number_of_shows: int
    number_of_unique_shows: int
    number_of_unique_titles: int
    number_of_unique_directors: int
    number_of_unique_countries: int
    api_version: str
    time_current_api_node_started: str
