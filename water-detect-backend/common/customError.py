from common import constants
from common.customResponse import NewErrorResponse


class CustomError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def toResp(self):
        return NewErrorResponse(code=self.code, msg=self.msg)

    def __str__(self):
        return f"code: {self.code}, msg: {self.msg}"

class ParamError(CustomError):
    def __init__(self, code=-1, msg=""):
        if msg == "":
            msg = "params error"
        if code == -1:
            code = 401
        super().__init__(code, msg)

InternalServerError = CustomError(500, constants.INTERNAL_ERROR)
