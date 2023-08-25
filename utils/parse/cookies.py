import re


def decode(cookie_string: str) -> dict:
    """
    解析cookies参数
    :param cookie_string: 解析的cookie
    :return: 解析后的键值对
    """
    cookies = re.split(r';\s*', cookie_string)
    cookie_dict = {}

    # 将cookie键值对存储到字典中
    for cookie in cookies:
        cookie_parts = cookie.split('=')
        if len(cookie_parts) == 2:
            key, value = cookie_parts
            cookie_dict[key] = value
    return cookie_dict
