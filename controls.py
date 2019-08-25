import datetime
from typing import List, Dict, Union

from db import crimes
import sqlalchemy as sa
import pandas as pd


def available_months():
    year_month = sa.func.date_trunc('month', crimes.c.OCCURRED_ON_DATE).label('year_month')
    months = sa.select([year_month.distinct()]).order_by(year_month)
    return [row.year_month for row in months.execute()]


def available_districts():
    districts = sa.select([sa.func.coalesce(crimes.c.DISTRICT, 'Unknown')
                          .label('DISTRICT')
                          .distinct()])

    return [row.DISTRICT for row in districts.execute()]


yearmonth = sa.func.date_trunc('month', crimes.c.OCCURRED_ON_DATE).label('year_month')

ReturnData = List[Dict[str, Union[int, str]]]


def get_num_offenses_by_year_and_district(start_date: datetime.datetime,
                                          end_date: datetime.datetime,
                                          districts: List[str]) -> ReturnData:
    """
    Calculates number of offenses per month filtered by district and interval

    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    query = (sa.select([yearmonth, sa.func.count().label('num_offenses')])
             .group_by(yearmonth)
             .where(crimes.c.OCCURRED_ON_DATE.between(start_date, end_date))
             .where(crimes.c.DISTRICT.in_(districts))
             .order_by(yearmonth))

    return [dict(row) for row in query.execute()]


def get_num_shootings_by_year_and_district(start_date: datetime.datetime,
                                           end_date: datetime.datetime,
                                           districts: List[str]) -> ReturnData:
    """
    Calculates number of shootings per month filtered by district and interval

    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    query = (sa.select([yearmonth,
                        sa.func.sum(crimes.c.SHOOTING).label('num_shootings')])
             .group_by(yearmonth)
             .where(crimes.c.OCCURRED_ON_DATE.between(start_date, end_date))
             .where(crimes.c.DISTRICT.in_(districts))
             .order_by(yearmonth)
             )
    return [dict(row) for row in query.execute()]


def get_top10_offense_groups(start_date: datetime.datetime,
                             end_date: datetime.datetime,
                             districts: List[str]) -> ReturnData:
    """
    Calculates top 10 number of offenses per offense group

    :param start_date: Date to calculate from
    :param end_date: Date to calculate to
    :param districts: Districts to include
    :return: List of dicts for each result
    """
    query = (sa.select([crimes.c.OFFENSE_CODE_GROUP,
                        sa.func.count().label('num_offenses')])
             .group_by(crimes.c.OFFENSE_CODE_GROUP)
             .where(crimes.c.OCCURRED_ON_DATE.between(start_date, end_date))
             .where(crimes.c.DISTRICT.in_(districts))
             .order_by(sa.desc(sa.func.count()))
             .limit(10)
             )
    return [dict(r) for r in query.execute()]


def get_heatmap_data(start_date: datetime.datetime,
                     end_date: datetime.datetime,
                     districts: List[str]) -> pd.DataFrame:
    """
    Calculates a frequency table for HOUR and DAY_OF_WEEK
    :param start_date: Date to calculate from
    :param end_date: Date to calculate until
    :param districts: Districts to be included
    :return: Dataframe of values where DAY_OF_WEEK is index and HOUR is columns
    """
    query = (sa.select([crimes.c.HOUR,
                        crimes.c.DAY_OF_WEEK,
                        sa.func.count().label('counts')])
             .group_by(crimes.c.HOUR, crimes.c.DAY_OF_WEEK)
             .where(crimes.c.OCCURRED_ON_DATE.between(start_date, end_date))
             .where(crimes.c.DISTRICT.in_(districts))
             )
    df = pd.read_sql(query, query.bind)
    df['DAY_OF_WEEK'] = pd.Categorical(df['DAY_OF_WEEK'],
                                       categories=["Monday",
                                                   "Tuesday",
                                                   "Wednesday",
                                                   "Thursday",
                                                   "Friday",
                                                   "Saturday",
                                                   "Sunday"],
                                       ordered=True)
    return df.set_index(['HOUR', 'DAY_OF_WEEK']).unstack()['counts']
