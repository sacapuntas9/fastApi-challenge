from sqlalchemy.orm import Session

from fast_api_challenge.models import database_models as models
from fast_api_challenge.database import orm

"""
Interface methods which reconcile usage of Pydantic Models with SQLAlchemy ORM Models and interact with the Database.
"""


def create_netflix_show(db_session: Session, show: orm.NetflixShow):
    """
    Create a new show in the database Netflix table
    :param db_session: SQLAlchemy DB session object
    :param show: ORM NetflixShow object to add (Can be sent as Pydantic NetflixShow model)
    :return: The newly created database record, queried directly from the DB. (Pydantic NetflixShow model)
    """
    netflix_db_show = orm.NetflixShow(**show.dict())
    db_session.add(netflix_db_show)
    db_session.commit()
    db_session.refresh(netflix_db_show)
    return get_netflix_show(db_session=db_session, show_id=netflix_db_show.show_id)


def get_netflix_show(db_session: Session, show_id: int):
    """
        Retrieves an existing show from the database using its show_id
        :param db_session: SQLAlchemy Session
        :param show_id: Possibly existing NetflixShow ID to return
        :return: Existing NetflixShow Model Object, or None
        """
    return db_session.query(orm.NetflixShow).filter(orm.NetflixShow.show_id == show_id).one_or_none()


def update_netflix_show(db_session: Session, show: orm.NetflixShow, show_id: int):
    """
    Update show in the database Netflix table
    :param db_session: SQLAlchemy DB session object
    :param show: ORM NetflixShow object to add (Can be sent as Pydantic NetflixShow model)
    :param show_id: show_id of the show to update (int)
    :return: Newly upated show (Pydantic NetflixShow Model Object)
    """
    db_session.query(orm.NetflixShow).filter(orm.NetflixShow.show_id == show_id).update(show.dict())
    db_session.commit()
    return show


def delete_netflix_show(db_session: Session, show_id: int):
    """
    Delete the show with the given show_id in the table
    :param db_session: SQLAlchemy DB session object
    :param show_id: show_id of the show to delete (int)
    :return: None (throw exception if failure)
    """
    db_session.query(orm.NetflixShow).filter(orm.NetflixShow.show_id == show_id).delete()
    db_session.commit()


def search_netflix_show(db_session: Session,
                        filter_args: models.NetflixShowSearchModel,
                        skip: int = None,
                        limit: int = None,
                        orderBy: str = None,
                        sort: str = None):
    """
    Dynamically construct query based on the passed parameters and execute it
    :param db_session: SQLAlchemy database session object
    :param filter_args: Filter argument values for each column in the form of a Pydantic Model
    :param skip: Number of records to skip for the starting record returned
    :param limit: Max number of records to return
    :param orderBy: Name of column in Netflix table to order by
    :param sort: Descending / Ascending (desc/asc)
    :return: (list) A list of NetflixShow Pydantic Model objects, representing the results retrieved from the DB.

    """
    db_query = db_session.query(orm.NetflixShow)  # Create initial query

    # loop over all filters and add them in as SQL "LIKE" searches
    for key, value in filter_args.dict().items():
        if value:
            db_query = db_query.filter(getattr(orm.NetflixShow, key).like(f"%{value}%"))  # searches for value as substring on both sides

    # Handle order by and sort (descending/ascending)
    if orderBy:
        order_by_attribute = getattr(orm.NetflixShow, orderBy.value)
        if sort:
            order_by_attribute = getattr(order_by_attribute, sort.value)()

        db_query = db_query.order_by(order_by_attribute)

    if limit:
        db_query = db_query.limit(limit)

    if skip:
        db_query = db_query.offset(skip)

    return db_query.all()  # Execute the dynamically generated, chained, filter expression


def get_number_netflix_shows(db_session: Session):
    """
    Return the number of records (shows) in the Netflix show database for the given db_session
    :param db_session: SQLAlchemy DB session object
    :return: number of shows (records) in the database (int)
    """
    return db_session.query(orm.NetflixShow).count()


def get_number_of_unique_for_given_netflix_show_table_column(db_session: Session, column_name: str = None):
    """
    For a given column name in the NetflixShow table, query the table to get the number of unique entries.
    :param db_session: DB session which contains the NetflixShow table
    :param column_name: Valid column name in the table
    :return: (int) number of unique records for the column
    """
    if column_name:
        orm_database_object = getattr(orm.NetflixShow, column_name)
    else:
        orm_database_object = orm.NetflixShow

    return db_session.query(orm_database_object).distinct().count()
