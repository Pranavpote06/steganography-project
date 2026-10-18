#!/usr/bin/env python3
"""
SMS Gateway Test Script
Tests your SMS configuration by sending a test OTP to your phone number.
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.otp_service import otp_service
from app.core import config

def print_banner():
    print("=" * 60)
    print("  📱 SMS GATEWAY TEST SCRIPT")
    print("=" * 60)
    print()

def check_configuration():
    """Check which SMS providers are configured"""
    print("🔍 Checking SMS Configuration...\n")
    
    providers = []
    
    if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_FROM_NUMBER:
        providers.append("✅ Twilio (Global)")
        print(f"   Account SID: {config.TWILIO_ACCOUNT_SID[:10]}...")
        print(f"   From Number: {config.TWILIO_FROM_NUMBER}")
    else:
        print("   ❌ Twilio: Not configured")
    
    if config.FAST2SMS_API_KEY:
        providers.append("✅ Fast2SMS (India)")
        print(f"   API Key: {config.FAST2SMS_API_KEY[:10]}...")
    else:
        print("   ❌ Fast2SMS: Not configured")
    
    if config.TWOFACTOR_API_KEY:
        providers.append("✅ 2Factor.in (India)")
        print(f"   API Key: {config.TWOFACTOR_API_KEY[:10]}...")
    else:
        print("   ❌ 2Factor.in: Not configured")
    
    if config.TEXTBEE_API_KEY and config.TEXTBEE_DEVICE_ID:
        providers.append("✅ TextBee (Android Gateway)")
    else:
        print("   ❌ TextBee: Not configured")
    
    if config.SMS_WEBHOOK_URL:
        providers.append("✅ Custom Webhook")
        print(f"   URL: {config.SMS_WEBHOOK_URL}")
    else:
        print("   ❌ Custom Webhook: Not configured")
    
    print()
    
    if not providers:
        print("⚠️  No SMS providers configured!")
        print()
        print("📖 Quick Setup:")
        print("   1. Edit backend/.env")
        print("   2. Add Twilio or Fast2SMS credentials")
        print("   3. See SMS_SETUP_GUIDE.md for details")
        print()
        return False
    
    print(f"✅ Active Providers: {', '.join(providers)}")
    print()
    return True

def send_test_sms():
    """Send a test SMS to verify configuration"""
    print("📱 Enter your phone number to receive a test OTP")
    print("   Format: +1234567890 (include country code)")
    print()
    
    phone = input("   Phone Number: ").strip()
    
    if not phone:
        print("❌ Phone number is required")
        return
    
    # Ensure phone has country code
    if not phone.startswith('+'):
        print("\n⚠️  Warning: Phone number should start with + and country code")
        print("   Example: +1234567890 for US, +91234567890 for India")
        confirm = input("   Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    print(f"\n🚀 Sending test OTP to {phone}...")
    print("   This may take 5-10 seconds...")
    print()
    
    try:
        result = otp_service.generate_otp(phone, carrier_name="test_carrier.wav")
        
        print("=" * 60)
        print("📊 RESULT:")
        print("=" * 60)
        print(f"Status:      {'✅ SUCCESS' if result['sms_sent'] else '❌ FAILED'}")
        print(f"Gateway:     {result['sms_gateway'].upper()}")
        print(f"Message:     {result['sms_status_message']}")
        print(f"Session:     {result['session_token']}")
        print(f"Expires In:  {result['expires_in']} seconds")
        print("=" * 60)
        print()
        
        if result['sms_sent']:
            print("✅ SUCCESS! Check your phone for the SMS.")
            print()
            print(f"📱 You should receive an SMS with a 6-digit OTP code.")
            print()
            
            # Ask if they want to test verification
            test_verify = input("Do you want to test OTP verification? (y/n): ").strip().lower()
            if test_verify == 'y':
                otp_code = input("Enter the OTP code you received: ").strip()
                
                is_valid = otp_service.verify_otp(result['session_token'], otp_code)
                
                if is_valid:
                    print("✅ OTP VERIFIED SUCCESSFULLY!")
                else:
                    print("❌ Invalid OTP code")
        else:
            print("❌ FAILED to send SMS")
            print()
            print("🔧 Troubleshooting:")
            print("   1. Check your credentials in backend/.env")
            print("   2. Verify account balance (if using Fast2SMS)")
            print("   3. For Twilio trial: verify the phone number in Twilio Console")
            print("   4. Check backend logs for detailed error messages")
        
        print()
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("🔧 Check backend/.env configuration and try again")
        print()

def main():
    print_banner()
    
    if not check_configuration():
        sys.exit(1)
    
    print("─" * 60)
    print()
    
    send_test_sms()
    
    print("─" * 60)
    print("✅ Test complete!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
