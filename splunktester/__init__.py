import splunklib.client as client


class SplunkTester(object):
    def __init__(self, **connect_args):
        self._connect_args = connect_args
        self._service = client.connect(**connect_args)

    def _context_service(self, app=None, user=None, **connect_args):
        if app or user:
            return client.connect(app=app, owner=user, **connect_args)

        return self._service

    def test_configs(self, files, app=None, user=None):
        test_service = self._context_service(app=app, user=user, **self._connect_args)

        print(f"User: {user}")
        print(f"App: {app}")

        success = True

        for test_file_name, test_file_config in files.items():
            print(f"  Config file: {test_file_name}")

            try:
                conf_file = test_service.confs[test_file_name]
            except KeyError:
                print(f"!!!!Expected: present, Got: absent")
                success = False
                continue

            test_file_stanzas = test_file_config.get("stanzas", {})
            for test_stanza_name, test_stanza_config in test_file_stanzas.items():
                print(f"    Stanza: {test_stanza_name}")

                try:
                    stanza = conf_file[test_stanza_name]
                except KeyError:
                    print(f"!!!!!!Expected: present, Got: absent")
                    success = False
                    continue

                for test_key_name, test_key_value in test_stanza_config.items():
                    print(f"      Key: {test_key_name}")

                    try:
                        key_value = stanza[test_key_name]
                    except KeyError:
                        print(f"!!!!!!!!Expected: present, Got: absent")
                        success = False
                        continue

                    try:
                        # all conf values are returned as strings, so compare appropriately
                        assert key_value == str(test_key_value)
                    except AssertionError:
                        print(f"!!!!!!!!Expected: {test_key_value}, Got: {key_value}")
                        success = False

        # did we pass all of our tests?
        assert success
