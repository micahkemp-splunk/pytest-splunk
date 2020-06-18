from .testlogger import TestLogger


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