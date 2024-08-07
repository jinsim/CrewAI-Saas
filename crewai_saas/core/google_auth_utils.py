import os
import requests
import jwt
from fastapi import HTTPException, Header
from typing import Optional
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드합니다
load_dotenv()


class GoogleAuthUtils:
    GOOGLE_PUBLIC_KEYS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

    @staticmethod
    def get_google_public_keys():
        response = requests.get(GoogleAuthUtils.GOOGLE_PUBLIC_KEYS_URL)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def load_jwk(jwk):
        # JWK를 PEM 형식의 공개 키로 변환
        rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        return rsa_key

#일단 안쓰는 함수
    @staticmethod
    def decode_google_id_token(id_token: str):
        try:
            # 구글의 공개 키를 가져옵니다
            public_keys = GoogleAuthUtils.get_google_public_keys()
            print(f"Public Keys: {public_keys}")

            # 토큰의 헤더에서 키 ID를 가져옵니다
            headers = jwt.get_unverified_header(id_token)
            print(f"Token Headers: {headers}")
            kid = headers.get('kid')
            if not kid:
                raise HTTPException(status_code=403, detail="Invalid token: Key ID not found in token header")
            print(f"Key ID: {kid}")

            # 키 ID에 해당하는 공개 키를 찾습니다
            public_key_data = next((key for key in public_keys['keys'] if key['kid'] == kid), None)
            if public_key_data is None:
                raise HTTPException(status_code=403, detail="Invalid token: Public key not found for Key ID")
            print(f"Public Key Data: {public_key_data}")

            # 공개 키를 변환합니다
            public_key = GoogleAuthUtils.load_jwk(public_key_data)
            print(f"Public Key: {public_key}")

            # 공개 키를 사용하여 토큰을 디코딩합니다
            payload = jwt.decode(id_token, public_key, algorithms=['RS256'], audience=GoogleAuthUtils.GOOGLE_CLIENT_ID)
            print(f"Payload: {payload}")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            print(f"JWT Decode Error: {e}")
            raise HTTPException(status_code=403, detail=f"Invalid token: Token decoding failed with error {e}")
        except Exception as e:
            print(f"General Error: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @staticmethod
    async def get_current_user_email(authorization: Optional[str] = Header(None)) -> str:
        if not authorization:
            raise HTTPException(status_code=403, detail="Authorization header missing")

        try:
            token_type, token = authorization.split()
            if token_type.lower() != "bearer":
                raise HTTPException(status_code=403, detail="Invalid token type")
            return extract_email_from_jwt(token)
            #payload = GoogleAuthUtils.decode_google_id_token(token)

            #email = payload.get('email')

            #if not email:
               # raise HTTPException(status_code=403, detail="Email not found in token")

            #return email
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid token format")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def extract_email_from_jwt(token: str) -> str:
    try:
        # JWT 디코딩 (서명 검증 없이)
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"Payload: {payload}")

        # 이메일 값 추출
        email = payload.get("email")
        print(f"Email: {email}")
        if not email:
            raise ValueError("Email not found in token")

        return email
    except jwt.DecodeError as e:
        raise ValueError(f"Invalid token: {e}")