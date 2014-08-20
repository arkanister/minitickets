# coding: utf-8


class ApplicationMiddleware(object):
    def process_request(self, request):
        # http headers
        request._HEADERS = dict([(
                key.replace('HTTP_', ''), value
            ) for key, value in request.META.items() \
                if key.startswith('HTTP_')
        ])