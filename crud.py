from sqlalchemy import insert, select
from create_tables import *


ins = lang.insert().values(
    id = 'sfsdkdf',
    name = 'fr'
)

engine = create_engine(f"postgresql+psycopg2://postgres:{os.environ['POSTGRES_PASSWORD']}@postgres/papers")
conn = engine.connect()
r = conn.execute(ins)

s = select([lang])
r = conn.execute(s)
print(r.fetchall(), file=sys.stderr)
