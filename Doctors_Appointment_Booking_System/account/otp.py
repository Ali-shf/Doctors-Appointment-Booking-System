import hashlib, hmac, time, secrets, string
from django.core.cache import cache
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

ALPHABET = "0123456789"
SECRET_SALT = "otp-v1-salt"

def send_email_otp(to_email: str, otp: str, subject: str = "Your verification code"):
    context = {"otp": otp}
    text_body = render_to_string("account/otp.txt", context)
    html_body = render_to_string("account/otp.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()

def gen_otp(n: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(n))

def _key(identifier: str, purpose: str) -> str:
    return f"otp:{purpose}:{identifier}"

def _attempts_key(Email: str, purpose: str) -> str:
    return f"otp:{purpose}:{Email}:attempts"

def hash_otp(otp: str) -> str:
    return hmac.new(SECRET_SALT.encode(), otp.encode(), hashlib.sha256).hexdigest()

def can_resend(Email: str, purpose: str, cooldown: int) -> bool:
    k = _key(Email, purpose)
    meta = cache.get(k + ":meta")
    if not meta:
        return True
    return (time.time() - meta.get("ts", 0)) >= cooldown

def save_otp(Email: str, purpose: str, otp: str) -> None:
    k = _key(Email, purpose)
    hashed = hash_otp(otp)
    cache.set(k, hashed, timeout=settings.OTP_TTL_SECONDS)
    cache.set(k + ":meta", {"ts": time.time()}, timeout=settings.OTP_TTL_SECONDS)
    cache.set(_attempts_key(Email, purpose), 0, timeout=settings.OTP_TTL_SECONDS)

def verify_otp(Email: str, purpose: str, otp: str) -> bool:
    k = _key(Email, purpose)
    attempts_k = _attempts_key(Email, purpose)

    hashed_saved = cache.get(k)
    if not hashed_saved:
        return False

    attempts = cache.get(attempts_k) or 0
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        return False

    cache.incr(attempts_k)

    if hmac.compare_digest(hashed_saved, hash_otp(otp)):
        cache.delete(k)
        cache.delete(k + ":meta")
        cache.delete(attempts_k)
        return True
    return False
