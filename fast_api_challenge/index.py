import uvicorn
from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from fast_api_challenge.models import database_models as models
from fast_api_challenge.models import api_enums, api_models
from fast_api_challenge import database_interface
from fast_api_challenge.auth import create_access_token, authenticate_api_user, ACCESS_TOKEN_EXPIRE_MINUTES

from fast_api_challenge.database import base

base.Base.metadata.create_all(bind=base.engine)  # Create table schema in db if not exists


version = open("VERSION", "r")
VERSION = version.readline()  # Used for metadata info
version.close()


app = FastAPI(
    title="FastApi Data Interface Demonstration",
    description="Showcases many FastApi features and good coding practices.",
    version=VERSION,)
APPLICATION_START_TIME = datetime.utcnow()  # Used for metadata info

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = base.DbSession()
    try:
        yield db
    finally:
        db.close()


@app.post("/show/", response_model=models.NetflixShowModel, status_code=201)
def create_show(show: models.NetflixShowModel, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Create a new show in the database. Throws an error if a show with the given show_id already exists, and generates
    a new show_id if one is not specified.
    """
    if show.show_id and database_interface.get_netflix_show(db, show_id=show.show_id):
        raise HTTPException(status_code=400, detail="Show already exists with given show_id.")
    return database_interface.create_netflix_show(db, show=show)


@app.get("/show/{show_id}", response_model=models.NetflixShowModel)
def get_show(show_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieve a show from the database with the given show_id, if one exists.
    """
    show = database_interface.get_netflix_show(db, show_id=show_id)
    if show is None:
        raise HTTPException(status_code=404, detail="Show not found.")
    return show


@app.get("/shows", response_model=List[models.NetflixShowModel])
def get_shows(
              filter_args: models.NetflixShowSearchModel=Depends(),
              skip: Optional[int] = Query(None, ge=0),
              limit: Optional[int] = Query(None, gt=0, lt=1000),
              orderBy: api_enums.SearchOrderByEnum = None,
              sort: api_enums.SearchSortEnum = None,
              db: Session = Depends(get_db),
              token: str = Depends(oauth2_scheme)):
    """
    Search for shows, based on query parameters. Includes the ability to paginate using skip and limit, the ability to
    sort using sort and orderBy, and the ability to filter based on any database field with a parameter identical to
    each field name.
    """
    if sort and not orderBy:
        raise HTTPException(status_code=400, detail="Cannot use the sort parameter without the orderBy parameter.")
    return database_interface.search_netflix_show(db, filter_args=filter_args, skip=skip, limit=limit, orderBy=orderBy,
                                                  sort=sort)


@app.put("/show/{show_id}", response_model=models.NetflixShowModel)
def update_show(show: models.NetflixShowUpdateModel, show_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Update the show with the given show_id using the fields in the request. Throws an error if the show_id does not
    exist.
    """
    if not database_interface.get_netflix_show(db, show_id=show_id):
        raise HTTPException(status_code=404, detail="Show not found.")
    return database_interface.update_netflix_show(db, show=show, show_id=show_id)


@app.delete("/show/{show_id}")
def delete_show(show_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Remove the show with the given show_id from the databse, if one exists.
    """
    if not database_interface.get_netflix_show(db, show_id=show_id):
        raise HTTPException(status_code=404, detail="Show not found.")
    return database_interface.delete_netflix_show(db, show_id=show_id)


@app.post("/token", response_model=api_models.Token)
async def retrieve_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Retrieve an Auth token
    """
    token_request = api_models.TokenRequestModel(name=form_data.username)
    authenticated = authenticate_api_user(token_request)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication Details",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_request.dict()}, expires_delta=access_token_expires
    )
    return access_token


@app.get("/summary", response_model=api_models.SummaryResponseModel)
def get_summary(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieve aggregated summary metadata about the stored data, including number of shows, number of unique shows,
    number of directors, etc., along with Api information such as the current Version.
    """
    response = api_models.SummaryResponseModel(number_of_shows=database_interface.get_number_netflix_shows(db_session=db),
                                               number_of_unique_shows=database_interface.get_number_of_unique_for_given_netflix_show_table_column(db_session=db, column_name=None),
                                               number_of_unique_titles=database_interface.get_number_of_unique_for_given_netflix_show_table_column(db_session=db, column_name="title"),
                                               number_of_unique_directors=database_interface.get_number_of_unique_for_given_netflix_show_table_column(db_session=db, column_name="director"),
                                               number_of_unique_countries=database_interface.get_number_of_unique_for_given_netflix_show_table_column(db_session=db, column_name="country"),
                                               time_current_api_node_started=APPLICATION_START_TIME.ctime() + " (UTC)",
                                               api_version=VERSION)
    return response


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="debug")
