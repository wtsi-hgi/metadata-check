import json
import unittest

from mcheck.results.checks_results import CheckResultJSONEncoder, CheckResult, RESULT_JSON_PROPERTY, \
    EXECUTED_JSON_PROPERTY, ERROR_MESSAGE_JSON_PROPERTY, SEVERITY_JSON_PROPERTY, CHECK_NAME_JSON_PROPERTY, \
    CheckResultJSONDecoder
from mcheck.results.constants import RESULT, SEVERITY

_NAME = "my_name"
_SEVERITY = SEVERITY.IMPORTANT
_ERROR_MESSAGE = "test"
_EXEUCTED = False
_RESULT = RESULT.SUCCESS


class TestCheckResultJSONEncoder(unittest.TestCase):
    """
    Tests for `CheckResultJSONEncoder`.
    """
    def setUp(self):
        self.check_result = CheckResult(
            _NAME, executed=_EXEUCTED, result=_RESULT, severity=_SEVERITY, error_message=_ERROR_MESSAGE)

    def test_with_all_properties_set(self):
        check_result_as_json_str = json.dumps(self.check_result, cls=CheckResultJSONEncoder)
        check_result_as_json_dict = json.loads(check_result_as_json_str)
        self.assertEqual(check_result_as_json_dict[CHECK_NAME_JSON_PROPERTY], self.check_result.check_name)
        self.assertEqual(check_result_as_json_dict[SEVERITY_JSON_PROPERTY], self.check_result.severity)
        self.assertEqual(check_result_as_json_dict[ERROR_MESSAGE_JSON_PROPERTY], self.check_result.error_message)
        self.assertEqual(check_result_as_json_dict[EXECUTED_JSON_PROPERTY], self.check_result.executed)
        self.assertEqual(check_result_as_json_dict[RESULT_JSON_PROPERTY], self.check_result.result)

    def test_with_no_error_message(self):
        self.check_result.error_message = None
        check_result_as_json_dict = CheckResultJSONEncoder().default(self.check_result)
        self.assertNotIn(ERROR_MESSAGE_JSON_PROPERTY, check_result_as_json_dict)

    def test_with_list(self):
        check_results = [self.check_result for _ in range(10)]
        check_result_as_json_dict = CheckResultJSONEncoder().default(check_results)
        self.assertEqual(len(check_result_as_json_dict), len(check_results))


class TestCheckResultJSONDecoder(unittest.TestCase):
    """
    Tests for `CheckResultJSONDecoder`.
    """
    def setUp(self):
        self.check_result_as_json_dict = {
            CHECK_NAME_JSON_PROPERTY: _NAME,
            EXECUTED_JSON_PROPERTY: _EXEUCTED,
            RESULT_JSON_PROPERTY: _RESULT,
            SEVERITY_JSON_PROPERTY: _SEVERITY,
            ERROR_MESSAGE_JSON_PROPERTY: _ERROR_MESSAGE
        }

    def test_with_all_properties_set(self):
        check_result_as_json_str = json.dumps(self.check_result_as_json_dict)
        check_result = json.loads(check_result_as_json_str, cls=CheckResultJSONDecoder)
        self.assertEqual(check_result.check_name, _NAME)
        self.assertEqual(check_result.severity, _SEVERITY)
        self.assertEqual(check_result.error_message, _ERROR_MESSAGE)
        self.assertEqual(check_result.executed, _EXEUCTED)
        self.assertEqual(check_result.result, _RESULT)

    def test_with_no_error_message(self):
        del self.check_result_as_json_dict[ERROR_MESSAGE_JSON_PROPERTY]
        check_result_as_json_str = json.dumps(self.check_result_as_json_dict)
        check_result = json.loads(check_result_as_json_str, cls=CheckResultJSONDecoder)
        self.assertIsNone(check_result.error_message)

    def test_with_list(self):
        check_results_as_json_dict = [self.check_result_as_json_dict for _ in range(10)]
        check_results_as_json_str = json.dumps(check_results_as_json_dict)
        check_results = json.loads(check_results_as_json_str, cls=CheckResultJSONDecoder)
        self.assertEqual(len(check_results), len(check_results))
        for check_result in check_results:
            self.assertIsInstance(check_result, CheckResult)


if __name__ == "__main__":
    unittest.main()
