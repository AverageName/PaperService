from sqlalchemy_utils import create_database, database_exists

from database import DATABASE_URL

if __name__ == "__main__":
    if not database_exists(DATABASE_URL):
        create_database(DATABASE_URL)
