import pycurl
import json

class PrescienceException(Exception):

    def message(self):
        return None

    def resolution_hint(self):
        return None

class PrescienceClientException(PrescienceException):
    def __init__(self, initial_error: pycurl.error):
        self.initial_error = initial_error

    def message(self):
        return f'An error happened on prescience client-side : {str(self.initial_error)}'

class TimeoutException(PrescienceClientException):
    def __init__(self, initial_error: pycurl.error):
        super().__init__(initial_error)

    def message(self):
        return self.initial_error.args[1]

class PyCurlExceptionFactory:
    @staticmethod
    def construct(initial_error: pycurl.error):
        switch = {
            pycurl.E_OPERATION_TIMEDOUT: TimeoutException
        }
        pycurl_code_error = initial_error.args[0]
        constructor = switch.get(pycurl_code_error, PrescienceClientException)
        return constructor(initial_error)

# HTTP ERROR CODE
E_UNAUTORIZED = 401
E_BAD_REQUEST = 400
E_NOT_FOUND = 404
E_METHOD_NOT_ALLOWED = 405
E_INTERNAL_SERVER_ERROR = 500

class PrescienceServerException(PrescienceException):
    def __init__(self, code_error: int, body: str = None):
        self.code_error = code_error
        self.body = body

    def message(self):
        return f'An error happened on prescience server-side : code_error = {str(self.code_error)} body_error = {str(self.body)}'

class UnauthorizedException(PrescienceServerException):
    def __init__(self, code_error: int, body: str = None):
        super().__init__(code_error, body)

    def message(self):
        return f'The prescience server answered us with an \'Unauthorized\' response.'

    def resolution_hint(self):
        return \
            'You should check the token that your configured on prescience :\n' + \
            '- You can get the currently used token by typing prescience.config().get_current_token()\n' \
            '- You can change the currently used token by typing prescience.config().set_project(<current-project-name>, <your-token>)\n'\
            'If you want a prescience token, you can request one here : https://survey.ovh.com/index.php/379341?lang=en'

class MethodNotAllowedException(PrescienceServerException):
    def __init__(self, code_error: int, body: str = None):
        super().__init__(code_error, body)

    def message(self):
        return f'The prescience server answered us with an \'MethodNotAllowed\' response. You are probably requesting a method that need specific rights to be executed.'

class NotFoundException(PrescienceServerException):
    def __init__(self, code_error: int, body: str = None):
        super().__init__(code_error, body)

    def message(self):
        result = f'The prescience server answered us with a \'NotFound\' response.'
        try:
            if self.body is not None:
                dict_error = json.loads(self.body)
                given_error = dict_error['message']
                result += ' ' + given_error
        except ValueError:
            pass

        return result

    def resolution_hint(self):
        return \
            'You should check that all the ID\'s that you refer to already exists on prescience.'


class HttpErrorExceptionFactory:
    @staticmethod
    def construct(code_error: int, body: str = None) -> PrescienceServerException:
        switch = {
            E_UNAUTORIZED: UnauthorizedException,
            E_NOT_FOUND: NotFoundException,
            E_METHOD_NOT_ALLOWED: MethodNotAllowedException
        }
        constructor = switch.get(code_error, PrescienceServerException)
        return constructor(code_error, body)