import os
import sqlalchemy as sa


db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432')
engine = sa.create_engine(db_url)
meta = sa.MetaData(bind=engine)

crimes = sa.Table('crimes', meta, autoload=True)
