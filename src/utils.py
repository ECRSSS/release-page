import datetime
import config


def is_versions_cache_time_expired(fix_versions):
    version_obj = fix_versions[0]
    now = datetime.datetime.now()
    created_at = version_obj.created_at
    time_diff_in_seconds = (now - created_at).total_seconds()
    print(f'saved time: {created_at}')
    print(f'now: {now}')
    print(f'timediff {time_diff_in_seconds} sec')
    if config.FIX_VERSIONS_CACHE_EXPIRE_AFTER <= time_diff_in_seconds:
        return True
    else:
        return False


def str_is_not_empty_or_none(param):
    if param is not None and param != '':
        return True
    else:
        return False
