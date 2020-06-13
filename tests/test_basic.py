import splunktester
import yaml

# TODO - is this path ok being relative from the project top level?
with open('tests//test-config.yml', 'r') as config_file:
    test_config = yaml.load(config_file, Loader=yaml.SafeLoader)

splunk_hostname = test_config["splunk_hostname"]
splunk_username = test_config["splunk_username"]
splunk_password = test_config["splunk_password"]

def test_something():
    splunktester.SplunkTester(
        host=splunk_hostname,
        username=splunk_username,
        password=splunk_password,
    )