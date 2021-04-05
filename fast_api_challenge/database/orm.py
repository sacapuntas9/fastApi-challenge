from sqlalchemy import Column, Date, Integer, String
from fast_api_challenge.database.base import Base


class NetflixShow(Base):
    __tablename__ = "netflix"

    show_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String)
    title = Column(String, index=True)
    director = Column(String)
    cast = Column(String)
    country = Column(String)
    date_added = Column(String)  # TODO: Possibly sanitize table data and use formal dates, not priority
    release_year = Column(Integer)  # This should be only positive, enforced in API.
    rating = Column(String)
    duration = Column(String)
    listed_in = Column(String)
    description = Column(String)

    def dict(self):
        """
        Converts the contents of this ORM object into a dict
        """
        return_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):  # Doesn't return protected values which are not actually class variables but are python builtins
                return_dict[key] = value
        return return_dict