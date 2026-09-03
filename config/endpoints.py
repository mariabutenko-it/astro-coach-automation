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
