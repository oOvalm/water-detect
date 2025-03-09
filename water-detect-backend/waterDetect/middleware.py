import logging

from django.http import JsonResponse

from common import constants
from common.customError import CustomError
from common.customResponse import NewErrorResponse
from django.db import models

logger = logging.getLogger(__name__)

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except models.Model.DoesNotExist as e:
            logger.error(f"An custom error occurred: {str(e)}", exc_info=True)
            return NewErrorResponse(400, "not found")
        except CustomError as e:
            logger.error(f"An custom error occurred: {str(e)}", exc_info=True)
            return e.toResp()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return NewErrorResponse(500, constants.INTERNAL_ERROR)
        return response