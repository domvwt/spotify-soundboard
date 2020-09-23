import datetime as dt


def last_friday(x):
    weekday = x.weekday()
    if weekday >= 4:
        return x - dt.timedelta(weekday - 4)
    else:
        return x - dt.timedelta(weekday + 3)
