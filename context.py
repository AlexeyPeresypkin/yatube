import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    y = dt.datetime.now().year

    return {
        'year': y,
    }
