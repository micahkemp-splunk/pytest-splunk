from .testlogger import TestLogger


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
