from slowapi import Limiter
from slowapi.util import get_remote_address

# Ініціалізація лімітера за IP-адресою
limiter = Limiter(key_func=get_remote_address)
