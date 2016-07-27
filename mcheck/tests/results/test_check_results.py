import json
import unittest

from mcheck.results.checks_results import CheckResult
from mcheck.results.constants import RESULT, SEVERITY
from hgijson import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder

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
        self.CheckResultJSONEncoder = MappingJSONEncoderClassBuilder(CheckResult, CheckResult.to_json_mapping()).build()


    def test_with_all_properties_set(self):
        check_result_as_json_str = json.dumps(self.check_result, cls=self.CheckResultJSONEncoder)
        check_result_as_json_dict = json.loads(check_result_as_json_str)
        self.assertEqual(check_result_as_json_dict["check_name"], self.check_result.check_name)
        self.assertEqual(check_result_as_json_dict["severity"], self.check_result.severity)
        self.assertEqual(check_result_as_json_dict["error_message"], self.check_result.error_message)
        self.assertEqual(check_result_as_json_dict["executed"], self.check_result.executed)
        self.assertEqual(check_result_as_json_dict["result"], self.check_result.result)

    def test_with_no_error_message(self):
        self.check_result.error_message = None
        check_result_as_json_dict = self.CheckResultJSONEncoder().default(self.check_result)
        self.assertNotIn("error_message", check_result_as_json_dict)

    def test_with_list(self):
        check_results = [self.check_result for _ in range(10)]
        check_result_as_json_dict = self.CheckResultJSONEncoder().default(check_results)
        self.assertEqual(len(check_result_as_json_dict), len(check_results))


class TestCheckResultJSONDecoder(unittest.TestCase):
    """
    Tests for `CheckResultJSONDecoder`.
    """
    def setUp(self):
        self.check_result_as_json_dict = {
            "check_name": _NAME,
            "executed": _EXEUCTED,
            "result": _RESULT,
            "severity": _SEVERITY,
            "error_message": _ERROR_MESSAGE
        }
        self.CheckResultJSONDecoder = MappingJSONDecoderClassBuilder(CheckResult, CheckResult.to_json_mapping()).build()


    def test_with_all_properties_set(self):
        check_result_as_json_str = json.dumps(self.check_result_as_json_dict)
        check_result = json.loads(check_result_as_json_str, cls=self.CheckResultJSONDecoder)
        self.assertEqual(check_result.check_name, _NAME)
        self.assertEqual(check_result.severity, _SEVERITY)
        self.assertEqual(check_result.error_message, _ERROR_MESSAGE)
        self.assertEqual(check_result.executed, _EXEUCTED)
        self.assertEqual(check_result.result, _RESULT)

    def test_with_no_error_message(self):
        del self.check_result_as_json_dict["error_message"]
        check_result_as_json_str = json.dumps(self.check_result_as_json_dict)
        check_result = json.loads(check_result_as_json_str, cls=self.CheckResultJSONDecoder)
        self.assertIsNone(check_result.error_message)

    def test_with_list(self):
        check_results_as_json_dict = [self.check_result_as_json_dict for _ in range(10)]
        check_results_as_json_str = json.dumps(check_results_as_json_dict)
        check_results = json.loads(check_results_as_json_str, cls=self.CheckResultJSONDecoder)
        self.assertEqual(len(check_results), len(check_results))
        for check_result in check_results:
            self.assertIsInstance(check_result, CheckResult)


if __name__ == "__main__":
    unittest.main()
