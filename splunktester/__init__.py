import splunklib.client as client
from colorama import Fore, Style
import pytest


class SplunkTester(object):
    def __init__(self, indent=0, **connect_args):
        self._indent = indent
        self._connect_args = connect_args
        self._service = client.connect(**connect_args)

    def _context_service(self, app=None, user=None, **connect_args):
        if app or user:
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
        TestLogger.info(f"User: {user}", indent=self._indent)
        TestLogger.info(f"App: {app}", indent=self._indent)

        test_service = self._context_service(app=app, user=user, **self._connect_args)

        return ConfTester(files=files, service=test_service, indent=self._indent+2).run()

    def test_creds(self, creds, app=None, user=None):
        TestLogger.info(f"User: {user}", indent=self._indent)
        TestLogger.info(f"App: {app}", indent=self._indent)

        test_service = self._context_service(app=app, user=user, **self._connect_args)

        return CredsTester(creds=creds, service=test_service, indent=self._indent+2).run()


class ConfTester(object):
    def __init__(self, files, service, indent=0):
        self._files = files
        self._service = service
        self._indent = indent

    def run(self):
        success = True

        for test_file_name, test_file_config in self._files.items():
            TestLogger.info(f"Config file: {test_file_name}", indent=self._indent)

            try:
                test_file_config_state = test_file_config.get("state", "present")
                conf_file = self._service.confs[test_file_name]
                assert test_file_config_state == "present"
                TestLogger.info(f"Expected: present, Got: present", indent=self._indent)
            except KeyError:
                if not test_file_config_state == "absent":
                    TestLogger.error(f"Expected: present, Got: absent", indent=self._indent)
                    success = False
                continue
            except AssertionError:
                TestLogger.error(f"Expected: absent, Got: present", indent=self._indent)
                success = False
                continue

            test_file_stanzas = test_file_config.get("stanzas", {})
            if not StanzaTester(stanzas=test_file_stanzas, conf_file=conf_file, indent=self._indent+2).run():
                success = False

        return success


class StanzaTester(object):
    def __init__(self, stanzas, conf_file, indent=0):
        self._stanzas = stanzas
        self._conf_file = conf_file
        self._indent = indent

    def run(self):
        success = True

        for test_stanza_name, test_stanza_config in self._stanzas.items():
            TestLogger.info(f"Stanza: {test_stanza_name}", indent=self._indent)

            try:
                stanza = self._conf_file[test_stanza_name]
                TestLogger.info(f"Expected: present, Got: present", indent=self._indent+2)
            except KeyError as e:
                TestLogger.error(f"Expected: present, Got: absent", indent=self._indent+2)
                success = False
                continue

            test_file_keys = test_stanza_config.get("keys", {})
            if not KeyTester(keys=test_file_keys, stanza_keys=stanza, indent=self._indent+2).run():
                success = False

        return success


class KeyTester(object):
    def __init__(self, keys, stanza_keys, indent=0):
        self._keys = keys
        self._stanza_keys = stanza_keys
        self._indent = indent

    def run(self):
        success = True

        for test_key_name, test_key_value in self._keys.items():
            TestLogger.info(f"Key: {test_key_name}", indent=self._indent)

            try:
                key_value = self._stanza_keys[test_key_name]
                TestLogger.info(f"Expected: present, Got: present", indent=self._indent+2)
            except KeyError:
                TestLogger.error(f"Expected: present, Got: absent", indent=self._indent+2)
                success = False
                continue

            try:
                # all conf values are returned as strings, so compare appropriately
                assert key_value == str(test_key_value)
                TestLogger.info(f"Expected: {test_key_value}, Got: {key_value}", indent=self._indent+2)
            except AssertionError:
                TestLogger.error(f"Expected: {test_key_value}, Got: {key_value}", indent=self._indent+2)
                success = False

        return success


class CredsTester(object):
    def __init__(self, creds, service, indent=0):
        self._creds = creds
        self._service = service
        self._indent = indent

    def run(self):
        success = True

        # test_cred_title needs to be in the form :realm:username:
        for test_cred_title, test_cred_value in self._creds.items():
            TestLogger.info(f"Cred: {test_cred_title}", indent=self._indent)

            try:
                found_cred_value = self._service.storage_passwords[test_cred_title].content.clear_password
                TestLogger.info(f"Expected: present, Got: present", indent=self._indent+2)
            except KeyError:
                TestLogger.error(f"Expected: present, Got: absent", indent=self._indent+2)
                success = False
                continue

            try:
                assert found_cred_value == str(test_cred_value)
                TestLogger.info(f"Expected: {test_cred_value}, Got: {found_cred_value}", indent=self._indent+2)
            except AssertionError:
                TestLogger.error(f"Expected: {test_cred_value}, Got: {found_cred_value}", indent=self._indent+2)
                success = False

        return success


class TestLogger(object):
    @classmethod
    def log(cls, msg, indent=0, indentchar=' '):
        print(f"{indentchar * indent}{msg}")

    @classmethod
    def info(cls, msg, indent=0):
        cls.log(msg, indent=indent, indentchar=' ')

    @classmethod
    def error(cls, msg, indent=0):
        print(Fore.RED, end='')
        cls.log(msg, indent=indent, indentchar='!')
        print(Style.RESET_ALL, end='')
