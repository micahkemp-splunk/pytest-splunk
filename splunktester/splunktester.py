import splunklib.client as client
import yaml
import pytest

from .testlogger import TestLogger
from .conftester import ConfTester
from .credstester import CredsTester


class SplunkTester(object):
    def __init__(self, indent=0, **connect_args):
        self._indent = indent
        self._connect_args = connect_args
        self._service = client.connect(**connect_args)

    def _context_service(self, app=None, user=None, **connect_args):
        if app or user:
            TestLogger.info(f"User: {user}")
            TestLogger.info(f"App: {app}")

            return client.connect(app=app, owner=user, **connect_args)

        return self._service

    @classmethod
    def test_yaml_file(cls, yaml_file):
        with open(yaml_file, 'r') as config_file:
            test_config = yaml.load(config_file, Loader=yaml.SafeLoader)

        splunk_hostname = test_config["splunk_hostname"]
        splunk_username = test_config["splunk_username"]
        splunk_password = test_config["splunk_password"]

        tester = cls(
            host=splunk_hostname,
            username=splunk_username,
            password=splunk_password,
        )

        for test in test_config.get("tests", []):
            user = test.get("user", None)
            app = test.get("app", None)

            assert tester.test_configs(test.get("configs", {}), user=user, app=app)

            assert tester.test_creds(test.get("creds", {}), user=user, app=app)

        for fail_test in test_config.get("fail_tests", []):
            user = test.get("user", None)
            app = test.get("app", None)

            if "configs" in fail_test:
                with pytest.raises(AssertionError):
                    assert tester.test_configs(fail_test["configs"], user=user, app=app)

            if "creds" in fail_test:
                with pytest.raises(AssertionError):
                    assert tester.test_creds(fail_test["creds"], user=user, app=app)

    def test_configs(self, files, app=None, user=None):
        test_service = self._context_service(app=app, user=user, **self._connect_args)

        return ConfTester(files=files, service=test_service, indent=self._indent+2).run()

    def test_creds(self, creds, app=None, user=None):
        test_service = self._context_service(app=app, user=user, **self._connect_args)

        return CredsTester(creds=creds, service=test_service, indent=self._indent+2).run()
