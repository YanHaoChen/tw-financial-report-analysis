from datetime import datetime


class DateTool:

    @staticmethod
    def date_to_ex_year_and_season(year, month):
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
        season_year = year if season != 4 else year - 1

        return season_year, season

    @staticmethod
    def season_to_ex_year_and_season_int(now_year_and_season: int):
        now_season = now_year_and_season % 10
        now_year = now_year_and_season // 10
        ex_season = now_season - 1
        ex_year = now_year
        if ex_season == 0:
            ex_season = 4
            ex_year -= 1
        return ex_year * 10 + ex_season

    @staticmethod
    def to_tw_year(year: int) -> int:
        return year - 1911

    @staticmethod
    def tw_year_to_year(year: int) -> int:
        return year + 1911

    @staticmethod
    def to_next_year_month(year: int, month: int) -> (int, int):
        month += 1
        if month == 13:
            year += 1
            month = 1
        return year, month

