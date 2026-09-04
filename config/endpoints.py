HEALTH = "/api/v1/health"
USERS = "/users"

AUTH_SEND_OTP = "/api/v1/auth/send-otp"
AUTH_VERIFY_OTP = "/api/v1/auth/verify-otp"
AUTH_REFRESH = "/api/v1/auth/refresh"
AUTH_GUEST_SESSION = "/api/v1/auth/guest-session"


def auth_guest_session(device_id):
    return f"{AUTH_GUEST_SESSION}/{device_id}"


MEMBERSHIP_PLANS = "/api/v1/membership/plans"

USER_ME_PREFERENCES = "/api/v1/user/me/preferences"
USER_ME_DEVICES = "/api/v1/user/me/devices"
USER_ME_ACCOUNT = "/api/v1/user/me/account"
USER_ME = "/api/v1/user/me"

ZODIAC_SIGNS = "/api/v1/zodiac-signs"


def zodiac_sign(slug):
    return f"{ZODIAC_SIGNS}/{slug}"


ASTRO_PROGRAMS = "/api/v1/astro-programs"
ASTRO_PROGRAM_THEMES = f"{ASTRO_PROGRAMS}/themes"
ASTRO_PROGRAMS_FEATURED = f"{ASTRO_PROGRAMS}/featured"


def astro_program(program_id):
    return f"{ASTRO_PROGRAMS}/{program_id}"


WISDOM = "/api/v1/wisdom"
WISDOM_GLOSSARY = f"{WISDOM}/glossary"
WISDOM_WORD_OF_THE_DAY = f"{WISDOM}/word-of-the-day"
WISDOM_XP = f"{WISDOM}/xp"


def wisdom_glossary_term(slug):
    return f"{WISDOM_GLOSSARY}/{slug}"


LOCATION = "/api/v1/location"
LOCATION_SEARCH = f"{LOCATION}/search"


def location_details(place_id):
    return f"{LOCATION}/{place_id}"


KARMA_COINS = "/api/v1/karma-coins"
KARMA_COINS_PRICING = f"{KARMA_COINS}/pricing"
KARMA_COINS_WALLET = f"{KARMA_COINS}/wallet"
KARMA_COINS_TRANSACTIONS = f"{KARMA_COINS}/transactions"
PAYMENTS = "/api/v1/payments"
