from django.http import JsonResponse


class HelperJsonResponse(JsonResponse):
    def __init__(self,
                 success=False,
                 data=None,
                 message=None,
                 redirect_to=None,
                 status=None):
        if not success and not message: message = "Error en la solicitud!"
        aData = {
            'data': data,
            'message': message,
            'success': success,
            'redirect_to': redirect_to

        }
        super(HelperJsonResponse, self).__init__(data=aData, status=status)
