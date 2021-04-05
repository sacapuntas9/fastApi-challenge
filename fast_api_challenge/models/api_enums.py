from enum import Enum

from fast_api_challenge.models.database_models import NetflixShowModel


class SearchSortEnum(str, Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


search_order_enum_member_names = {}
for key in NetflixShowModel.schema().get("properties"):  # iterate over all of the field names in the model
    search_order_enum_member_names[key.upper()] = key  # Save to dict for dynamic enum creation


"""
SearchOrderByEnum

Valid values to Order By, (values in the Netflix Shows database).
"""
SearchOrderByEnum = Enum('SearchOrderByEnum', search_order_enum_member_names)  # Dynamically create enum with fieldnames
