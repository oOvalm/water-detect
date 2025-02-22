from common import constants
from common.utils import NewErrorResponse


class CustomError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def toResp(self):
        return NewErrorResponse(code=self.code, msg=self.msg)

    def __str__(self):
        return f"code: {self.code}, msg: {self.msg}"


InternalServerError = CustomError(500, constants.INTERNAL_ERROR)
ParamError = CustomError(401, "params error")
