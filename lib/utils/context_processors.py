# -*- coding: utf-8 -*-
import datetime


def date_context_processor(request):
    return {
        "TODAY": datetime.date.today(),
        "NOW": datetime.datetime.now()
    }