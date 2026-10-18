import time
import secrets
import uuid
import httpx
from typing import Dict, Any, Optional
from ..core import config

OTP_EXPIRY_SECONDS = 300 # 5 minutes

class OTPService:
    def __init__(self):
        # session_token -> { phone, otp, created_at, expires_at, verified, attempts }
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def _dispatch_real_sms(self, phone: str, otp_code: str) -> Dict[str, Any]:
        """
        Transmits real cellular SMS to the recipient's mobile phone using configured gateways:
        1. Twilio (Worldwide)
        2. Fast2SMS (India +91) - with automatic OTP / Quick route fallbacks
        3. 2Factor.in (India)
        4. TextBee (Android SIM Gateway)
        5. Custom Webhook
        """
        sms_text = f"StegoCyber Security: Your verification code is {otp_code}. Valid for 5 minutes. Do not share this code."
        clean_num = phone.replace("+91", "").replace("+", "").replace(" ", "").replace("-", "").strip()

        # 1. Twilio Gateway (Worldwide)
        if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_FROM_NUMBER:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Messages.json"
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        url,
                        auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
                        data={
                            "From": config.TWILIO_FROM_NUMBER,
                            "To": phone if phone.startswith("+") else f"+91{clean_num}",
                            "Body": sms_text
                        }
                    )
                if resp.status_code in (200, 201):
                    print(f"[SMS GATEWAY - TWILIO] Real SMS dispatched to {phone}")
                    return {"success": True, "gateway": "twilio", "message": f"Real SMS delivered to {phone} via Twilio."}
                else:
                    print(f"[SMS GATEWAY - TWILIO ERROR] Status {resp.status_code}: {resp.text}")
                    return {"success": False, "gateway": "twilio", "message": f"Twilio gateway error: {resp.status_code}"}
            except Exception as e:
                print(f"[SMS GATEWAY - TWILIO EXCEPTION] {e}")

        # 2. Fast2SMS Gateway (India)
        if config.FAST2SMS_API_KEY:
            try:
                with httpx.Client(timeout=12.0) as client:
                    # Attempt A: Route 'otp'
                    resp = client.post(
                        "https://www.fast2sms.com/dev/bulkV2",
                        headers={"authorization": config.FAST2SMS_API_KEY},
                        json={
                            "variables_values": otp_code,
                            "route": "otp",
                            "numbers": clean_num
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("return") is True:
                            print(f"[SMS GATEWAY - FAST2SMS OTP] Real SMS dispatched to {phone}")
                            return {"success": True, "gateway": "fast2sms", "message": f"Real cellular SMS delivered to {phone}."}

                    # Attempt B: Route 'q' (Quick transactional route fallback)
                    resp_q = client.post(
                        "https://www.fast2sms.com/dev/bulkV2",
                        headers={"authorization": config.FAST2SMS_API_KEY},
                        json={
                            "route": "q",
                            "message": f"StegoCyber Verification OTP: {otp_code}. Valid for 5 minutes.",
                            "language": "english",
                            "numbers": clean_num
                        }
                    )
                    if resp_q.status_code == 200:
                        data_q = resp_q.json()
                        if data_q.get("return") is True:
                            print(f"[SMS GATEWAY - FAST2SMS QUICK] Real SMS dispatched to {phone}")
                            return {"success": True, "gateway": "fast2sms", "message": f"Real cellular SMS delivered to {phone}."}
                        else:
                            err_msg = ", ".join(data_q.get("message", ["Delivery failed"]))
                            return {"success": False, "gateway": "fast2sms", "message": f"Fast2SMS: {err_msg}"}
                    else:
                        return {"success": False, "gateway": "fast2sms", "message": f"Fast2SMS HTTP {resp_q.status_code}"}
            except Exception as e:
                print(f"[SMS GATEWAY - FAST2SMS EXCEPTION] {e}")
                return {"success": False, "gateway": "fast2sms", "message": f"Fast2SMS error: {str(e)}"}

        # 3. 2Factor.in Gateway (India)
        if config.TWOFACTOR_API_KEY:
            try:
                url = f"https://2factor.in/API/V1/{config.TWOFACTOR_API_KEY}/SMS/{clean_num}/{otp_code}/AUTOGEN"
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(url)
                if resp.status_code == 200 and "Success" in resp.text:
                    print(f"[SMS GATEWAY - 2FACTOR] Real SMS dispatched to {phone}")
                    return {"success": True, "gateway": "2factor", "message": f"Real cellular SMS delivered to {phone} via 2Factor."}
                else:
                    return {"success": False, "gateway": "2factor", "message": f"2Factor: {resp.text}"}
            except Exception as e:
                print(f"[SMS GATEWAY - 2FACTOR EXCEPTION] {e}")

        # 4. TextBee Gateway (Android SIM Relay)
        if config.TEXTBEE_API_KEY and config.TEXTBEE_DEVICE_ID:
            try:
                full_num = f"+91{clean_num}" if not phone.startswith("+") else phone
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.textbee.dev/api/v1/gateway/send-sms",
                        headers={
                            "x-api-key": config.TEXTBEE_API_KEY,
                            "Content-Type": "application/json"
                        },
                        json={
                            "recipients": [full_num],
                            "message": sms_text,
                            "deviceId": config.TEXTBEE_DEVICE_ID
                        }
                    )
                if resp.status_code in (200, 201):
                    return {"success": True, "gateway": "textbee", "message": f"Real cellular SMS sent to {phone} via Android SIM gateway."}
            except Exception as e:
                print(f"[SMS GATEWAY - TEXTBEE EXCEPTION] {e}")

        # 5. Custom SMS Webhook
        if config.SMS_WEBHOOK_URL:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        config.SMS_WEBHOOK_URL,
                        json={"phone": phone, "otp": otp_code, "message": sms_text}
                    )
                if resp.status_code in (200, 201, 204):
                    print(f"[SMS GATEWAY - WEBHOOK] Real SMS dispatched to {phone}")
                    return {"success": True, "gateway": "webhook", "message": f"Real SMS delivered to {phone} via Webhook."}
            except Exception as e:
                print(f"[SMS GATEWAY - WEBHOOK EXCEPTION] {e}")

        # 6. No SMS Gateway Configured
        print("=" * 60)
        print(f"[SMS GATEWAY NOTICE] Real cellular SMS delivery requested for: {phone}")
        print("No SMS API key is configured yet in backend/.env")
        print(f"OTP generated for session: {otp_code}")
        print("=" * 60)

        return {
            "success": False,
            "gateway": "none",
            "message": f"No SMS gateway configured. Connect Fast2SMS or Twilio to deliver real SMS to {phone}."
        }

    def generate_otp(self, phone: str, carrier_name: str = "") -> Dict[str, Any]:
        """Generates a secure 6-digit OTP for the given recipient phone and sends it via SMS."""
        session_token = f"sess_{uuid.uuid4().hex}"
        # 6-digit numeric OTP
        otp_code = str(secrets.randbelow(900000) + 100000)
        now = time.time()
        expires_at = now + OTP_EXPIRY_SECONDS

        self._sessions[session_token] = {
            "phone": phone,
            "otp": otp_code,
            "carrier_name": carrier_name,
            "created_at": now,
            "expires_at": expires_at,
            "verified": False,
            "attempts": 0
        }

        # Dispatch real cellular SMS
        sms_result = self._dispatch_real_sms(phone, otp_code)

        # Notice: Real security - NEVER expose plain OTP in API response
        return {
            "session_token": session_token,
            "phone": phone,
            "expires_in": OTP_EXPIRY_SECONDS,
            "sms_sent": sms_result["success"],
            "sms_gateway": sms_result["gateway"],
            "sms_status_message": sms_result["message"]
        }

    def verify_otp(self, session_token: str, entered_otp: str) -> bool:
        """Verifies the entered OTP code against the active session."""
        session = self._sessions.get(session_token)
        if not session:
            return False

        if time.time() > session["expires_at"]:
            del self._sessions[session_token]
            return False

        session["attempts"] += 1
        if session["attempts"] > 5:
            del self._sessions[session_token]
            return False

        if session["otp"] == entered_otp.strip():
            session["verified"] = True
            return True

        return False

    def is_session_verified(self, session_token: str) -> bool:
        session = self._sessions.get(session_token)
        if not session:
            return False
        return session.get("verified", False) and time.time() <= session["expires_at"]

    def cleanup_expired(self):
        now = time.time()
        expired = [token for token, data in self._sessions.items() if data["expires_at"] < now]
        for token in expired:
            del self._sessions[token]

otp_service = OTPService()
