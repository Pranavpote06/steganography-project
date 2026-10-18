# 📱 SMS Configuration - Complete Guide

## Overview

StegoCyber supports **real SMS delivery** to phone numbers for OTP (One-Time Password) verification. This enables true multi-factor authentication where recipients must verify their identity via:
1. 📱 SMS code sent to their phone
2. 👤 Live face scan via webcam

---

## 🎯 Quick Links

- **Quick Start (5 min):** [QUICKSTART_SMS.md](QUICKSTART_SMS.md)
- **Detailed Setup:** [SMS_SETUP_GUIDE.md](SMS_SETUP_GUIDE.md)
- **Test SMS:** Run `python backend/test_sms.py`

---

## 🌟 Supported SMS Providers

### 1. **Twilio** ⭐ Recommended
- **Region:** Worldwide
- **Cost:** $0.0075 - $0.20 per SMS
- **Free Trial:** $15 credit (~2000 SMS)
- **Setup Time:** 2 minutes
- **Best For:** Production, Global reach

### 2. **Fast2SMS** 
- **Region:** India only (+91)
- **Cost:** ₹0.15 per SMS (~$0.002)
- **Free Trial:** No
- **Setup Time:** 3 minutes
- **Best For:** Budget India deployments

### 3. **2Factor.in**
- **Region:** India only (+91)
- **Cost:** ₹0.20 per SMS
- **Free Trial:** No
- **Setup Time:** 3 minutes
- **Best For:** India with OTP templates

### 4. **TextBee**
- **Region:** Global
- **Cost:** Free (uses your SIM)
- **Free Trial:** Yes
- **Setup Time:** 5 minutes
- **Best For:** Testing, personal use

### 5. **Custom Webhook**
- **Region:** Any
- **Cost:** Depends on your service
- **Setup Time:** Varies
- **Best For:** Custom integrations

---

## ⚡ Quick Setup (Recommended: Twilio)

### Step 1: Get Twilio Account (Free)
```
1. Visit: https://www.twilio.com/try-twilio
2. Sign up (2 minutes)
3. Get $15 free credit
4. No credit card required
```

### Step 2: Get Credentials
```
1. Go to: https://console.twilio.com
2. Copy:
   - Account SID (starts with "AC...")
   - Auth Token (click "Show")
   - Get a trial phone number (click big button)
```

### Step 3: Configure
**Option A: Web Interface** (Easiest)
```
1. Start backend: cd backend && python run_backend.py
2. Start frontend: cd frontend && npm run dev
3. Open: http://localhost:5173
4. Click: "SMS Configuration" in sidebar
5. Paste credentials and save
```

**Option B: Edit .env File**
```bash
# Edit backend/.env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+15551234567
```

### Step 4: Verify (Optional Phone Numbers)
For Twilio trial, verify recipient phone numbers:
```
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Add phone numbers you want to send to
3. Each number gets a verification code
```

### Step 5: Test!
```bash
cd backend
python test_sms.py
# Enter your phone number
# Check your phone for SMS!
```

---

## 🔧 Configuration Files

### backend/.env
```env
# Twilio (Global - works worldwide)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+15551234567

# Fast2SMS (India only)
FAST2SMS_API_KEY=your_fast2sms_api_key_here

# 2Factor.in (India only)
TWOFACTOR_API_KEY=your_2factor_api_key_here

# TextBee (Android Gateway)
TEXTBEE_API_KEY=your_textbee_api_key
TEXTBEE_DEVICE_ID=your_device_id

# Custom Webhook
SMS_WEBHOOK_URL=https://your-domain.com/api/send-sms
```

---

## 🧪 Testing SMS

### Method 1: Test Script (Recommended)
```bash
cd backend
python test_sms.py
```

This will:
- ✅ Check your SMS configuration
- ✅ Show which providers are configured
- ✅ Send a test OTP to your phone
- ✅ Optionally test OTP verification

### Method 2: Via Application
```
1. Open frontend (http://localhost:5173)
2. Go to "Extract" page
3. Upload a carrier file with recipient verification
4. Enter phone number
5. Click "Send OTP"
6. Check your phone!
```

### Method 3: Check Status Endpoint
```bash
curl http://localhost:8000/security/sms-status
```

Response:
```json
{
  "active_provider": "twilio",
  "twilio_configured": true,
  "fast2sms_configured": false,
  "twofactor_configured": false,
  "webhook_configured": false,
  "twilio_number": "+15551234567"
}
```

---

## 📊 Provider Priority

The system tries SMS gateways in this order:
1. **Twilio** (if configured)
2. **Fast2SMS** (if configured)  
3. **2Factor.in** (if configured)
4. **TextBee** (if configured)
5. **Custom Webhook** (if configured)

Only the **first configured provider** will be used.

---

## 🔍 Verification Flow

When a file has recipient verification enabled:

```
1. User uploads carrier file (audio/video)
2. System inspects file → detects recipient phone required
3. User enters their phone number
4. System validates phone matches embedded metadata
5. System generates 6-digit OTP
6. System sends SMS to phone via gateway ✉️📱
7. User receives SMS with OTP code
8. User enters OTP in app
9. System verifies OTP
10. User captures face scan 📸
11. System logs access attempt with face photo
12. System extracts hidden payload ✅
```

---

## 💰 Cost Estimates

### For 1000 OTP Messages

| Provider | Cost | Notes |
|----------|------|-------|
| Twilio (US) | $7.50 | $0.0075/SMS |
| Twilio (International) | $50-200 | Varies by country |
| Fast2SMS (India) | ₹150 ($1.80) | Cheapest option |
| 2Factor.in (India) | ₹200 ($2.40) | - |
| TextBee | Free | Uses your SIM |

### Free Tier Options

- **Twilio:** $15 credit = ~2000 SMS
- **TextBee:** Unlimited (but uses your phone)

---

## 🆘 Troubleshooting

### "No SMS gateway configured"
**Problem:** No SMS provider credentials in `.env`  
**Solution:** Configure at least one provider (see setup guide)

### "The number is unverified" (Twilio Trial)
**Problem:** Trial accounts can only send to verified numbers  
**Solution:** Verify numbers in Twilio Console OR upgrade to paid ($0)

### "Invalid credentials"
**Problem:** Wrong API keys in `.env`  
**Solution:** Double-check credentials, ensure no extra spaces

### "Insufficient balance" (Fast2SMS)
**Problem:** No credits in Fast2SMS wallet  
**Solution:** Recharge wallet (minimum ₹10)

### SMS not received
**Possible causes:**
- ❌ Wrong phone number format (needs country code: `+1234567890`)
- ❌ Phone is off or no signal
- ❌ SMS blocked/spam folder
- ❌ Invalid phone number
- ❌ Provider issue

**Solutions:**
1. Check backend logs for dispatch confirmation
2. Verify phone number format
3. Check SMS provider dashboard for delivery status
4. Try a different phone number

### Backend logs show "No SMS gateway configured"
**Problem:** `.env` file not loaded or invalid  
**Solution:**
```bash
# Check .env file exists
ls backend/.env

# Verify values (without quotes)
cat backend/.env | grep TWILIO

# Restart backend
cd backend
python run_backend.py
```

---

## 🔒 Security Best Practices

### 1. Protect API Keys
```bash
# NEVER commit .env to git
echo "backend/.env" >> .gitignore

# Restrict file permissions
chmod 600 backend/.env  # Unix/Mac
```

### 2. Rotate Keys Regularly
- Rotate Twilio tokens every 90 days
- Immediately rotate if exposed

### 3. Monitor Usage
- Check SMS provider dashboards weekly
- Set spending alerts
- Watch for unusual spikes

### 4. Use Environment Variables in Production
```bash
# Production server
export TWILIO_ACCOUNT_SID="ACxxx..."
export TWILIO_AUTH_TOKEN="xxx..."
export TWILIO_FROM_NUMBER="+1234567890"
```

### 5. Implement Rate Limiting
The system already implements:
- ✅ 5-minute OTP expiry
- ✅ Maximum 5 verification attempts per session
- ✅ Session tokens for security

---

## 🌐 Phone Number Format

### Always use E.164 format:
```
✅ CORRECT:
+1234567890      (US)
+911234567890    (India)
+442071234567    (UK)

❌ WRONG:
1234567890       (missing +)
(123) 456-7890   (has formatting)
123-456-7890     (has dashes)
```

### The system auto-formats when possible:
```python
# Input:  "9876543210" (India)
# System: "+919876543210"

# Input:  "+91 98765 43210"
# System: "+919876543210"
```

---

## 📱 SMS Message Format

Recipients receive:
```
StegoCyber Security: Your verification code is 123456. 
Valid for 5 minutes. Do not share this code.
```

**Message Length:** 94 characters  
**Segments:** 1 SMS (under 160 characters)  
**Cost:** 1 SMS credit per message

---

## 🎉 Production Checklist

Before going live:

- [ ] SMS provider account created
- [ ] API credentials configured in `.env`
- [ ] Test SMS sent successfully (`python test_sms.py`)
- [ ] Phone number format validated
- [ ] OTP verification tested end-to-end
- [ ] Face detection tested
- [ ] Audit logs working
- [ ] Error handling tested (wrong OTP, expired OTP)
- [ ] Rate limiting verified
- [ ] Spending alerts configured in provider dashboard
- [ ] Backup provider configured (optional)
- [ ] `.env` file secured (not in git)

---

## 📞 Support Resources

### Twilio
- Docs: https://www.twilio.com/docs/sms
- Console: https://console.twilio.com
- Support: https://support.twilio.com

### Fast2SMS
- Docs: https://www.fast2sms.com/docs
- Dashboard: https://www.fast2sms.com/dashboard
- Support: support@fast2sms.com

### 2Factor.in
- Website: https://2factor.in
- Support: support@2factor.in

### TextBee
- Website: https://textbee.dev
- App: Google Play Store

---

## ✅ Summary

1. **Sign up** for Twilio (free $15 credit)
2. **Copy** credentials from dashboard
3. **Paste** into backend/.env or use web UI
4. **Test** with `python backend/test_sms.py`
5. **Done!** Real SMS to any phone number 📱

For detailed instructions, see [QUICKSTART_SMS.md](QUICKSTART_SMS.md)

---

**Questions?** Check the troubleshooting section or review the full setup guide.

**Ready to send?** Run `python backend/test_sms.py` and enter your phone number!
