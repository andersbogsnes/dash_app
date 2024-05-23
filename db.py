import sqlalchemy as sa
from settings import Settings

settings = Settings()

engine = sa.create_engine(settings.db_url.get_secret_value())
meta = sa.MetaData()

crimes = sa.Table('crimes', meta,
                  sa.Column('incident_number', sa.String),
                  sa.Column('offense_code', sa.String),
                  sa.Column('offense_code_group', sa.String),
                  sa.Column('offense_description', sa.String),
                  sa.Column('district', sa.String),
                  sa.Column('reporting_area', sa.String),
                  sa.Column('shooting', sa.Boolean),
                  sa.Column('occurred_on_date', sa.Date),
                  sa.Column('year', sa.Integer),
                  sa.Column('month', sa.Integer),
                  sa.Column('day_of_week', sa.String),
                  sa.Column('hour', sa.Integer),
                  sa.Column('ucr_part', sa.String),
                  sa.Column('street', sa.String),
                  sa.Column('lat', sa.Float),
                  sa.Column('long', sa.Float),
                  )
