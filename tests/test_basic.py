import splunktester
import yaml
import pytest

# TODO - is this path ok being relative from the project top level?
with open('tests//test-config.yml', 'r') as config_file:
    test_config = yaml.load(config_file, Loader=yaml.SafeLoader)

splunk_hostname = test_config["splunk_hostname"]
splunk_username = test_config["splunk_username"]
splunk_password = test_config["splunk_password"]


def test_something():
    tester = splunktester.SplunkTester(
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

        with pytest.raises(AssertionError):
            assert tester.test_configs(fail_test.get("configs", {}), user=user, app=app)

        with pytest.raises(AssertionError):
            assert tester.test_creds(fail_test.get("creds", {}), user=user, app=app)
