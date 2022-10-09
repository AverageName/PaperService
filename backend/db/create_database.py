from sqlalchemy_utils import database_exists, create_database
from database import DATABASE_URL


if __name__ == "__main__":
    if not database_exists(DATABASE_URL):
        create_database(DATABASE_URL)
