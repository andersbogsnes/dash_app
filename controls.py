import datetime
from typing import List, Dict, Union

from db import crimes
import sqlalchemy as sa
import pandas as pd


def available_months(conn: sa.Connection) -> list[str]:
    year_month = sa.func.date_trunc('month', crimes.c.occurred_on_date).label('year_month')
    months_sql = sa.select(year_month.distinct()).order_by(year_month)
    return [row.year_month for row in conn.execute(months_sql)]


def available_districts(conn: sa.Connection) -> list[str]:
    districts_sql = sa.select(sa.func.coalesce(crimes.c.district, 'Unknown')
                              .label('district')
                              .distinct())

    return [row.district for row in conn.execute(districts_sql)]


ReturnData = List[Dict[str, Union[int, str]]]


def get_num_offenses_by_year_and_district(
        conn: sa.Connection,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        districts: List[str]) -> ReturnData:
    """
    Calculates number of offenses per month filtered by district and interval

    :param conn:
    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    yearmonth = sa.func.date_trunc('month', crimes.c.occurred_on_date).label('year_month')

    query = (sa.select(yearmonth, sa.func.count().label('num_offenses'))
             .group_by(yearmonth)
             .where(crimes.c.occurred_on_date.between(start_date, end_date))
             .where(crimes.c.district.in_(districts))
             .order_by(yearmonth))

    return [dict(row) for row in conn.execute(query).mappings()]


def get_num_shootings_by_year_and_district(conn: sa.Connection,
                                           start_date: datetime.datetime,
                                           end_date: datetime.datetime,
                                           districts: List[str]) -> ReturnData:
    """
    Calculates number of shootings per month filtered by district and interval

    :param conn: A SQLAlchemy connection
    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    yearmonth = sa.func.date_trunc('month', crimes.c.occurred_on_date).label('year_month')

    query = (sa.select(yearmonth,
                        sa.func.sum(sa.cast(crimes.c.shooting, sa.Integer)).label('num_shootings'))
             .group_by(yearmonth)
             .where(crimes.c.occurred_on_date.between(start_date, end_date))
             .where(crimes.c.district.in_(districts))
             .order_by(yearmonth)
             )
    return [dict(row) for row in conn.execute(query).mappings()]


def get_top10_offense_groups(
        conn: sa.Connection,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        districts: List[str]) -> ReturnData:
    """
    Calculates top 10 number of offenses per offense group

    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    query = (sa.select(crimes.c.offense_code_group,
                        sa.func.count().label('num_offenses'))
             .group_by(crimes.c.offense_code_group)
             .where(crimes.c.occurred_on_date.between(start_date, end_date))
             .where(crimes.c.district.in_(districts))
             .order_by(sa.desc(sa.func.count()))
             .limit(10)
             )
    return [dict(r) for r in conn.execute(query).mappings()]


def get_heatmap_data(conn: sa.Connection,
                     start_date: datetime.datetime,
                     end_date: datetime.datetime,
                     districts: List[str]) -> pd.DataFrame:
    """
    Calculates a frequency table for HOUR and DAY_OF_WEEK
    :param start_date: Date to calculate from
    :param end_date: Date to calculate until
    :param districts: Districts to be included
    :return: Dataframe of values where DAY_OF_WEEK is index and HOUR is columns
    """
    query = (sa.select(crimes.c.hour,
                        crimes.c.day_of_week,
                        sa.func.count().label('counts'))
             .group_by(crimes.c.hour, crimes.c.day_of_week)
             .where(crimes.c.occurred_on_date.between(start_date, end_date))
             .where(crimes.c.district.in_(districts))
             )
    df = pd.read_sql(query, conn)
    df['day_of_week'] = pd.Categorical(df['day_of_week'],
                                       categories=["Monday",
                                                   "Tuesday",
                                                   "Wednesday",
                                                   "Thursday",
                                                   "Friday",
                                                   "Saturday",
                                                   "Sunday"],
                                       ordered=True)
    return df.set_index(['hour', 'day_of_week']).unstack()['counts']
