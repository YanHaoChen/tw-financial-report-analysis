from datetime import datetime


class DateTool:

    @staticmethod
    def date_to_ex_season_and_year(year, month):
        ex_season_mapping = {
            1: 4,
            2: 4,
            3: 4,
            4: 1,
            5: 1,
            6: 1,
            7: 2,
            8: 2,
            9: 2,
            10: 3,
            11: 3,
            12: 3
        }
        season = ex_season_mapping[month]
        season_year = year if year != 4 else year - 1

        return season, season_year

    @staticmethod
    def to_tw_year(year: int) -> int:
        return year - 1911

    @staticmethod
    def tw_year_to_year(year: int) -> int:
        return year + 1911
