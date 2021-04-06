from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime


class NetflixShowUpdateModel(BaseModel):
    """
    Used for operations where the primary key is not expected or allowed
    """
    type: str = None
    title: str
    director: str = None
    cast: Optional[str]
    country: Optional[str]
    rating: Optional[str]
    duration: Optional[str]
    listed_in: Optional[str]
    description: Optional[str]
    release_year: int = Field(gt=0, lt=2147483647, default=None)
    date_added: str = None  # TODO: Possibly sanitize table data and use formal dates, not priority
    #                         TODO: Becuase the data in the DB is in different date formats, just using string.

    class Config:
        orm_mode = True


class NetflixShowModel(NetflixShowUpdateModel):
    """
    Main Netflix Show Pydantic Model
    """
    show_id: int = Field(gt=0, lt=2147483647, default=None)


class NetflixShowSearchModel(NetflixShowModel):
    """
    Model with all identical fields to the main Netflix Show model, except:
    1) Has no required fields, unless they must be used in every search, which is unlikely
    2) Only contains fields which should be used to search
    """
    title: str = None
