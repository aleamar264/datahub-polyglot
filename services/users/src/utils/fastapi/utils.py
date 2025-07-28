from fastapi import Request
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import EmailStr


def get_base_url(request: Request) -> str:
	return f"{request.url.scheme}://{request.url.netloc}"



token = URLSafeTimedSerializer(secret_key="", salt='Email_Verification_&_Forgot_password')

def url_with_token(email: EmailStr)->str:
    return token.dumps(email)

def verify_token(token_to_verify:str):
    try:
        email = token.loads(token_to_verify, max_age=1800)
    except SignatureExpired:
        return
    except BadTimeSignature:
        return
    return