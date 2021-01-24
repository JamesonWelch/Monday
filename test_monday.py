import unittest
from monday import *
import speech_config
import contextlib


class TestMonday(unittest.TestCase):

    def test_random_response(self):
        self.assertEqual(random_response(['1','1']),'1')

    def test_response_polarity(self):
        self.assertEqual(response_polarity(speech_config.deny),'-')


if __name__ == '__main__':
    # find all tests in this module
    import __main__
    suite = unittest.TestLoader().loadTestsFromModule(__main__)
    with io.StringIO() as buf:
        # run the tests
        with contextlib.redirect_stdout(buf):
            unittest.TextTestRunner(stream=buf).run(suite)
        # process (in this case: print) the results
        print(buf.getvalue())