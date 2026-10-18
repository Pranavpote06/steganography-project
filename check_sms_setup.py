#!/usr/bin/env python3
"""
Quick SMS Configuration Checker
Verifies your SMS gateway setup without sending any actual messages.
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "=" * 70)
    print("  📱 SMS CONFIGURATION CHECKER")
    print("=" * 70 + "\n")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path("backend/.env")
    
    if not env_path.exists():
        print("❌ backend/.env file not found!")
        print("   Create it by copying: backend/.env.example")
        print("   Then add your SMS provider credentials.\n")
        return False
    
    print("✅ backend/.env file exists\n")
    return True

def check_providers():
    """Check which SMS providers are configured"""
    env_path = Path("backend/.env")
    
    if not env_path.exists():
        return {}
    
    providers = {}
    
    with open(env_path, 'r') as f:
        content = f.read()
        
        # Check Twilio
        if 'TWILIO_ACCOUNT_SID=' in content and 'TWILIO_AUTH_TOKEN=' in content and 'TWILIO_FROM_NUMBER=' in content:
            for line in content.split('\n'):
                if line.startswith('TWILIO_ACCOUNT_SID=') and '=' in line:
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#') and value:
                        providers['twilio'] = True
                        break
        
        # Check Fast2SMS
        if 'FAST2SMS_API_KEY=' in content:
            for line in content.split('\n'):
                if line.startswith('FAST2SMS_API_KEY=') and '=' in line:
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#'):
                        providers['fast2sms'] = True
                        break
        
        # Check 2Factor
        if 'TWOFACTOR_API_KEY=' in content:
            for line in content.split('\n'):
                if line.startswith('TWOFACTOR_API_KEY=') and '=' in line:
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#'):
                        providers['2factor'] = True
                        break
        
        # Check TextBee
        if 'TEXTBEE_API_KEY=' in content and 'TEXTBEE_DEVICE_ID=' in content:
            has_key = False
            has_device = False
            for line in content.split('\n'):
                if line.startswith('TEXTBEE_API_KEY='):
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#'):
                        has_key = True
                if line.startswith('TEXTBEE_DEVICE_ID='):
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#'):
                        has_device = True
            if has_key and has_device:
                providers['textbee'] = True
        
        # Check Webhook
        if 'SMS_WEBHOOK_URL=' in content:
            for line in content.split('\n'):
                if line.startswith('SMS_WEBHOOK_URL=') and '=' in line:
                    value = line.split('=', 1)[1].strip()
                    if value and not value.startswith('#') and value:
                        providers['webhook'] = True
                        break
    
    return providers

def display_status(providers):
    """Display configuration status"""
    print("📊 SMS PROVIDER STATUS:\n")
    print("-" * 70)
    
    all_providers = [
        ('twilio', '🌍 Twilio (Global)', 'Works worldwide, $15 free credit'),
        ('fast2sms', '🇮🇳 Fast2SMS (India)', 'Cheapest for India, ₹0.15/SMS'),
        ('2factor', '🇮🇳 2Factor.in (India)', 'India OTP service'),
        ('textbee', '📱 TextBee (Android)', 'Free, uses your phone SIM'),
        ('webhook', '🔗 Custom Webhook', 'Your own SMS service'),
    ]
    
    configured_count = 0
    
    for key, name, description in all_providers:
        if key in providers:
            print(f"✅ {name}")
            print(f"   {description}")
            print(f"   Status: CONFIGURED ✓")
            configured_count += 1
        else:
            print(f"❌ {name}")
            print(f"   {description}")
            print(f"   Status: Not configured")
        print()
    
    print("-" * 70)
    print(f"\n📈 Summary: {configured_count}/{len(all_providers)} providers configured\n")
    
    return configured_count > 0

def print_next_steps(has_providers):
    """Print next steps based on configuration status"""
    if has_providers:
        print("✅ SMS READY TO USE!")
        print("\n🎯 Next Steps:")
        print("   1. Test your setup:")
        print("      cd backend")
        print("      python test_sms.py")
        print()
        print("   2. Or start the application:")
        print("      Backend:  cd backend && python run_backend.py")
        print("      Frontend: cd frontend && npm run dev")
        print()
        print("   3. Try extracting a file with recipient verification")
        print()
    else:
        print("⚠️  NO SMS PROVIDERS CONFIGURED")
        print("\n🚀 Quick Setup (Choose ONE):")
        print()
        print("   Option 1: Twilio (Recommended - Free $15 credit)")
        print("   ─────────────────────────────────────────────────")
        print("   1. Sign up: https://www.twilio.com/try-twilio")
        print("   2. Get Account SID, Auth Token, and Phone Number")
        print("   3. Add to backend/.env:")
        print("      TWILIO_ACCOUNT_SID=ACxxxxxxxxx...")
        print("      TWILIO_AUTH_TOKEN=your_token")
        print("      TWILIO_FROM_NUMBER=+1234567890")
        print()
        print("   Option 2: Fast2SMS (India - Cheapest)")
        print("   ─────────────────────────────────────")
        print("   1. Sign up: https://www.fast2sms.com/")
        print("   2. Recharge wallet (₹10 minimum)")
        print("   3. Get API key from Dev API section")
        print("   4. Add to backend/.env:")
        print("      FAST2SMS_API_KEY=your_api_key")
        print()
        print("   📖 Full guide: See SMS_SETUP_GUIDE.md")
        print("   ⚡ Quick start: See QUICKSTART_SMS.md")
        print()

def main():
    print_header()
    
    # Check if running from correct directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (the directory containing 'backend' and 'frontend' folders)\n")
        sys.exit(1)
    
    # Check .env file
    has_env = check_env_file()
    
    if not has_env:
        print("⚠️  Create backend/.env first:")
        print("   1. Copy backend/.env.example to backend/.env")
        print("   2. Add your SMS provider credentials")
        print("   3. Run this script again\n")
        sys.exit(1)
    
    # Check providers
    providers = check_providers()
    
    # Display status
    has_providers = display_status(providers)
    
    # Print next steps
    print_next_steps(has_providers)
    
    print("─" * 70)
    print("✅ Configuration check complete!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
