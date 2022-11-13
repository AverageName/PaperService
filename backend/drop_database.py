from sqlalchemy_utils import database_exists, drop_database

from db.database import DATABASE_URL

if __name__ == "__main__":
    assert database_exists(DATABASE_URL)
    drop_database(DATABASE_URL)
