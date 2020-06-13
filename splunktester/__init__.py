import splunklib.client as client

class SplunkTester(object):
    def __init__(self, **connect_args):
        self._service = client.connect(**connect_args)
