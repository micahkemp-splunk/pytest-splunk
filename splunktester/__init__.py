import splunklib.client as client


class SplunkTester(object):
    def __init__(self, **connect_args):
        self._connect_args = connect_args
        self._service = client.connect(**connect_args)

    def _context_service(self, app=None, user=None, **connect_args):
        if app or user:
            return client.connect(app=app, user=user, **connect_args)

        return self._service

    def test_configs(self, files, app=None, user=None):
        test_service = self._context_service(app=app, user=user, **self._connect_args)

        for test_file_name, test_file_config in files.items():
            conf_file = test_service.confs[test_file_name]

            success = True

            for test_stanza_name, test_stanza_config in test_file_config.items():
                stanza = conf_file[test_stanza_name]

                for test_key_name, test_key_value in test_stanza_config.items():
                    key_value = stanza[test_key_name]

                    try:
                        # all conf values are returned as strings, so compare appropriately
                        assert key_value == str(test_key_value)
                    except:
                        print(f"Config file: {test_file_name}")
                        print(f"  Stanza: {test_stanza_name}")
                        print(f"    Key: {test_key_name}")
                        print(f"      Expected: {test_key_value}, Got: {key_value}")
                        success = False

            assert success
