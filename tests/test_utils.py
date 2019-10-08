import unittest
import pandas
import numpy
import copy
import datetime

from prescience_client.utils import get_dataframe_real_predict_theoric, filter_dataframe_on_index

class TestUtils(unittest.TestCase):

    def test_filter_dataframe_on_index_int(self):
        initial_dataframe = pandas.DataFrame(
            data={
                'steps': [x for x in range(100)],
                'passengers': [x for x in range(100)]
            }
        )
        filtered = filter_dataframe_on_index(
            df=initial_dataframe,
            index='steps',
            min_bound=10,
            max_bound=20
        )
        expected = pandas.DataFrame(
            index=[x for x in range(10, 21)],
            data={
                'steps': [x for x in range(10, 21)],
                'passengers': [x for x in range(10, 21)]
            }
        )
        self.assertTrue(pandas.DataFrame.equals(expected, filtered))


    def test_filter_dataframe_on_index_str(self):
        initial_dataframe = pandas.DataFrame(
            data={
                'steps': [str(x) for x in range(10, 100)],
                'passengers': [x for x in range(10, 100)]
            }
        )
        filtered = filter_dataframe_on_index(
            df=initial_dataframe,
            index='steps',
            min_bound='50',
            max_bound='60'
        )
        expected = pandas.DataFrame(
            index=[str(x) for x in range(50, 61)],
            data={
                'steps': [str(x) for x in range(50, 61)],
                'passengers': [x for x in range(50, 61)]
            }
        )
        self.assertTrue(pandas.DataFrame.equals(expected, filtered))


    def test_filter_dataframe_on_index_datetime(self):
        initial_dataframe = pandas.DataFrame(
            data={
                'steps': [datetime.datetime(2018, 1, 1, x, 0, 0) for x in range(1, 12)],
                'passengers': [x for x in range(1, 12)]
            }
        )
        filtered = filter_dataframe_on_index(
            df=initial_dataframe,
            index='steps',
            min_bound=datetime.datetime(2018, 1, 1, 5, 0, 0),
            max_bound=datetime.datetime(2018, 1, 1, 8, 0, 0)
        )
        expected = pandas.DataFrame(
            index=[datetime.datetime(2018, 1, 1, x, 0, 0) for x in range(5, 9)],
            data={
                'steps': [datetime.datetime(2018, 1, 1, x, 0, 0) for x in range(5, 9)],
                'passengers': [x for x in range(5, 9)]
            }
        )
        self.assertTrue(pandas.DataFrame.equals(expected, filtered))


    def test_get_dataframe_real_predict_theoric_with_numbers(self):
        t_index = 50
        back_steps = 5
        forward_steps = 4

        steps = [x for x in range(100)]
        passengers = [900 for _ in steps]
        predicted_passengers = [1000 for _ in range(forward_steps)]

        initial_dataframe = pandas.DataFrame(data={
            'steps': copy.deepcopy(steps),
            'passengers': copy.deepcopy(passengers)
        })
        series_dict_input = {
            'steps': copy.deepcopy(steps)[t_index - back_steps : t_index + 1],
            'passengers': copy.deepcopy(passengers)[t_index - back_steps : t_index + 1]
        }
        series_dict_predict = {
            'steps': copy.deepcopy(steps)[t_index + 1 : t_index + 1 + forward_steps],
            'passengers': copy.deepcopy(predicted_passengers)
        }

        expected = pandas.DataFrame(index=steps[t_index - back_steps : t_index + 1 + forward_steps], data={
            'passengers_input': passengers[t_index - back_steps : t_index + 1] + [numpy.nan for _ in range(forward_steps)],
            'passengers_predicted': [numpy.nan for _ in range(back_steps)] + [passengers[t_index]] + predicted_passengers,
            'passengers_theoric': [numpy.nan for _ in range(back_steps)] + passengers[t_index: t_index + 1 + forward_steps]
        })

        final = get_dataframe_real_predict_theoric(
            series_dict_input=series_dict_input,
            series_dict_predict=series_dict_predict,
            time_feature_name='steps',
            initial_dataframe=initial_dataframe,
            label_id='passengers'
        )

        self.assertTrue(pandas.DataFrame.equals(expected, final))


    def test_get_dataframe_real_predict_theoric_with_dates(self):
        t_index = 6
        back_steps = 4
        forward_steps = 3

        months = [f'1990-0{x}' for x in range(0, 10)]
        passengers = [900 for _ in months]
        predicted_passengers = [1000 for _ in range(forward_steps)]

        initial_dataframe = pandas.DataFrame(data={
            'months': copy.deepcopy(months),
            'passengers': copy.deepcopy(passengers)
        })
        series_dict_input = {
            'months': copy.deepcopy(months)[t_index - back_steps : t_index + 1],
            'passengers': copy.deepcopy(passengers)[t_index - back_steps : t_index + 1]
        }
        series_dict_predict = {
            'months': copy.deepcopy(months)[t_index + 1 : t_index + 1 + forward_steps],
            'passengers': copy.deepcopy(predicted_passengers)
        }

        expected = pandas.DataFrame(index=months[t_index - back_steps : t_index + 1 + forward_steps], data={
            'passengers_input': passengers[t_index - back_steps : t_index + 1] + [numpy.nan for _ in range(forward_steps)],
            'passengers_predicted': [numpy.nan for _ in range(back_steps)] + [passengers[t_index]] + predicted_passengers,
            'passengers_theoric': [numpy.nan for _ in range(back_steps)] + passengers[t_index: t_index + 1 + forward_steps]
        })

        print(expected)

        final = get_dataframe_real_predict_theoric(
            series_dict_input=series_dict_input,
            series_dict_predict=series_dict_predict,
            time_feature_name='months',
            initial_dataframe=initial_dataframe,
            label_id='passengers'
        )

        print(final)

        self.assertTrue(pandas.DataFrame.equals(expected, final))