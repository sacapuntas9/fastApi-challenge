import sys, os
sys.path
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), '../..'))  # Reference the root of the project like api does

import math
from typing import List
import unittest
from hypothesis import given, strategies as st

from sqlalchemy.exc import IntegrityError

from fast_api_challenge.tests.test_utils import inject_in_memory_db_with_netflix_show_table
from fast_api_challenge import database_interface
from fast_api_challenge.models import database_models
from fast_api_challenge.database import orm


class TestDatabaseInterface(unittest.TestCase):
    """
    Tests the database interface module methods using an in-memory database
    Uses Hypothesis to generate test data, running it through the database and failing in the case of any errors.
    """

    @given(model_instance=st.builds(database_models.NetflixShowModel))
    @inject_in_memory_db_with_netflix_show_table
    def test_create_retrieve_netflix_show(self, model_instance: database_models.NetflixShowModel, db):
        """
        Tests create and read database interface methods by creating records and subsequently reading them.
        """
        result = database_interface.create_netflix_show(db_session=db, show=model_instance)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, orm.NetflixShow))

        show_query_result = database_interface.get_netflix_show(db_session=db, show_id=result.show_id)
        self.assertIsNotNone(show_query_result)
        self.assertTrue(isinstance(result, orm.NetflixShow))

    @given(model_instance=st.builds(database_models.NetflixShowModel))
    @inject_in_memory_db_with_netflix_show_table
    def test_create_duplicate_primary_key_raises_exception(self, model_instance: database_models.NetflixShowModel, db):
        """
        Tests that an exception is raised when a show is added to the database with the same show_id as an existing show
        """
        result = database_interface.create_netflix_show(db_session=db, show=model_instance)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, orm.NetflixShow))

        model_instance.show_id = result.show_id

        self.assertRaises(IntegrityError, lambda: database_interface.create_netflix_show(db_session=db, show=model_instance))

        db.rollback()  # Required to prevent errors in subsequent iterations due to the exception occurring earlier

    @given(model_instance=st.builds(database_models.NetflixShowModel))
    @inject_in_memory_db_with_netflix_show_table
    def test_create_delete_netflix_show(self, model_instance: database_models.NetflixShowModel, db):
        """
        Tests create and delete database interface methods by creating records and subsequently deleting them.
        Verifies that the shows are deleted by calling the Get method and checking if they exist.
        """
        result = database_interface.create_netflix_show(db_session=db, show=model_instance)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, orm.NetflixShow))

        database_interface.delete_netflix_show(db_session=db, show_id=result.show_id)

        show_query_result = database_interface.get_netflix_show(db_session=db, show_id=result.show_id)
        self.assertIsNone(show_query_result)

    @given(update_model_instances=st.lists(st.builds(database_models.NetflixShowUpdateModel)), model_instance=st.builds(database_models.NetflixShowModel))
    @inject_in_memory_db_with_netflix_show_table
    def test_update_netflix_show(self, update_model_instances: List[database_models.NetflixShowUpdateModel],
                                 model_instance: database_models.NetflixShowModel, db):
        """
        Tests database update by generating a random list of Update models and updating a randomly generated Show Row
        using these models
        """
        result = database_interface.create_netflix_show(db_session=db, show=model_instance)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, orm.NetflixShow))

        show_id = result.show_id  # Get the show_id which was written into the DB

        for db_update_model in update_model_instances:
            update_result = database_interface.update_netflix_show(db_session=db, show=db_update_model, show_id=show_id)
            self.assertIsNotNone(update_result)
            self.assertTrue(isinstance(update_result, database_models.NetflixShowUpdateModel))

    @given(model_instances=st.lists(st.builds(database_models.NetflixShowModel), min_size=11))
    @inject_in_memory_db_with_netflix_show_table
    def test_search_netflix_shows(self, model_instances: List[database_models.NetflixShowModel], db):
        """
        Tests database method which searches for a show based on filter parameters, with ordering and pagination.
        This could be alternatively split into multiple tests based on each configurable aspect of Search.
        """
        for db_model in model_instances:  # Add all instances to db
            database_interface.create_netflix_show(db_session=db, show=db_model)

        # Test Pagination
        for i in range(0, math.floor(len(model_instances)/10)):  # Uses page size of 10 - this could be randomized
            current_page = database_interface.search_netflix_show(db_session=db,
                                                                  filter_args=database_models.NetflixShowSearchModel(),
                                                                  skip=i*10,
                                                                  limit=10,
                                                                  )
            self.assertEqual(10, len(current_page))

        final_page = database_interface.search_netflix_show(db_session=db,
                                                            filter_args=database_models.NetflixShowSearchModel(),
                                                            skip=math.floor(len(model_instances)/10) * 10,
                                                            limit=10
                                                            )
        self.assertEqual(len(model_instances) % 10, len(final_page))

    @given(model_instances=st.lists(st.builds(database_models.NetflixShowModel)))
    @inject_in_memory_db_with_netflix_show_table
    def test_get_number_of_shows(self, model_instances: List[database_models.NetflixShowModel], db):
        """
        Tests database method which retrieves the number of shows in the DB by adding a list of shows and checking
        that the result is equal to the number of shows added
        """
        show_ids_used = set()  # Keeps track of unique show_ids so that the random generation doesn't create a clash

        for db_model in model_instances:
            if db_model.show_id is None or db_model.show_id not in show_ids_used:

                result = database_interface.create_netflix_show(db_session=db, show=db_model)
                self.assertIsNotNone(result)
                self.assertTrue(isinstance(result, orm.NetflixShow))
                show_ids_used.add(result.show_id)

        number_shows_from_db_query = database_interface.get_number_netflix_shows(db)

        self.assertEqual(number_shows_from_db_query, len(show_ids_used))

    @given(model_instances=st.lists(st.builds(database_models.NetflixShowModel)))
    @inject_in_memory_db_with_netflix_show_table
    def test_get_number_of_unique_for_given_netflix_show_table_column(self, model_instances: List[database_models.NetflixShowModel], db):
        """
        Tests database method which retrieves the number unique values for a given column in the Netflix DB by adding
        a list of shows and keeping track of unique values for each column in those shows, asserting each of these
        columns matches the expected count
        """
        db_column_values = {"show_id": set()}  # Keeps track of unique db columns, with show_id to prevent clash

        for db_model in model_instances:
            if db_model.show_id is None or db_model.show_id not in db_column_values.get("show_id"):
                result = database_interface.create_netflix_show(db_session=db, show=db_model)
                self.assertIsNotNone(result)
                self.assertTrue(isinstance(result, orm.NetflixShow))
                for key, value in result.dict().items():
                    db_column_values.setdefault(key, set()).add(value)

        for key, value in db_column_values.items():
            number_for_colum_from_db = database_interface.get_number_of_unique_for_given_netflix_show_table_column(db_session=db, column_name=key)
            self.assertEqual(number_for_colum_from_db, len(value))
