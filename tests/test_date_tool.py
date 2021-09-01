from toolbox.date_tool import DateTool
import unittest


class DateToolTestCase(unittest.TestCase):

    def test_date_to_ex_year_and_season_success(self):
        ex_year, ex_season = DateTool.date_to_ex_year_and_season(2019, 10)
        assert (ex_year == 2019 and ex_season == 3) is True

        ex_year, ex_season = DateTool.date_to_ex_year_and_season(2020, 1)
        assert (ex_year == 2019 and ex_season == 4) is True

    def test_season_to_ex_year_and_season_int_success(self):
        ex_year_and_season_int = DateTool.season_to_ex_year_and_season_int(20201)
        assert ex_year_and_season_int == 20194

    def test_to_tw_year_success(self):
        tw_year = DateTool.to_tw_year(2020)
        assert tw_year == 109

    def test_tw_year_to_year_success(self):
        year = DateTool.tw_year_to_year(109)
        assert year == 2020


if __name__ == '__main__':
    unittest.main()
