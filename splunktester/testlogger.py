from colorama import Fore, Style


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
