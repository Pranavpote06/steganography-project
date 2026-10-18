# 📱 Real SMS Setup Guide - StegoCyber

This guide will help you configure real SMS delivery to phone numbers for OTP verification.

## 🌍 Option 1: Twilio (Recommended - Works Worldwide)

### Step 1: Create Twilio Account
1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account (you get $15 credit)
3. Verify your email and phone number

### Step 2: Get Your Credentials
1. Go to https://console.twilio.com/
2. Copy your **Account SID** and **Auth Token** from the dashboard
3. Get a phone number:
   - Click "Get a Trial Number" (free)
   - Or buy a number from Phone Numbers → Buy a Number (~$1/month)

### Step 3: Configure in StegoCyber
Add these to your `backend/.env` file:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890
```

**Important Notes:**
- Trial accounts can only send to verified phone numbers
- To send to any number, upgrade to a paid account (Pay As You Go)
- Cost: ~$0.0075 per SMS in the US, varies by country

---

## 🇮🇳 Option 2: Fast2SMS (India Only - Cheapest)

### Step 1: Create Fast2SMS Account
1. Go to https://www.fast2sms.com/
2. Sign up and verify your account
3. Recharge your wallet (minimum ₹10)

### Step 2: Get API Key
1. Go to https://www.fast2sms.com/dashboard/dev-api
2. Copy your **API Key**

### Step 3: Configure in StegoCyber
Add this to your `backend/.env` file:
```env
FAST2SMS_API_KEY=your_fast2sms_api_key_here
```

**Important Notes:**
- Only works for Indian phone numbers (+91)
- Very cheap: ~₹0.15-0.25 per SMS
- Supports OTP and promotional routes

---

## 🇮🇳 Option 3: 2Factor.in (India Only)

### Step 1: Create 2Factor Account
1. Go to https://2factor.in/
2. Sign up and verify your account

### Step 2: Get API Key
1. Login to your dashboard
2. Navigate to API Settings
3. Copy your **API Key**

### Step 3: Configure in StegoCyber
Add this to your `backend/.env` file:
```env
TWOFACTOR_API_KEY=your_2factor_api_key_here
```

---

## 📱 Option 4: TextBee (Free - Use Your Android Phone)

### Step 1: Install TextBee App
1. Download TextBee from Google Play Store on your Android phone
2. Sign up for a free account

### Step 2: Get Credentials
1. Open the app
2. Go to Settings → API Settings
3. Copy your **API Key** and **Device ID**

### Step 3: Configure in StegoCyber
Add these to your `backend/.env` file:
```env
TEXTBEE_API_KEY=your_textbee_api_key
TEXTBEE_DEVICE_ID=your_device_id
```

**Important Notes:**
- Completely free - uses your phone's SIM card
- Your phone must be connected to internet
- SMS charges apply from your mobile carrier

---

## 🔗 Option 5: Custom Webhook (Advanced)

If you have your own SMS service, configure a webhook:

```env
SMS_WEBHOOK_URL=https://your-domain.com/api/send-sms
```

Your webhook will receive POST requests with:
```json
{
  "phone": "+1234567890",
  "otp": "123456",
  "message": "Full SMS text here"
}
```

---

## 🚀 Quick Start (Recommended Path)

### For Testing (Free):
1. **Twilio Trial** - Get $15 free credit, add verified numbers only
2. **TextBee** - Use your Android phone for free

### For Production (Paid):
1. **Worldwide**: Twilio ($0.0075/SMS)
2. **India Only**: Fast2SMS (₹0.15/SMS) - Cheapest option

---

## ✅ Verification

After configuring, restart your backend:
```bash
cd backend
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
python run_backend.py
```

Then test:
1. Open the frontend (http://localhost:5173)
2. Navigate to Extract → Security tab
3. Click "Check SMS Status" to verify configuration
4. Try sending a test OTP to your phone

---

## 📊 Priority Order

The system tries SMS gateways in this order:
1. **Twilio** (if configured)
2. **Fast2SMS** (if configured)
3. **2Factor.in** (if configured)
4. **TextBee** (if configured)
5. **Custom Webhook** (if configured)

Only the first configured gateway will be used.

---

## 🆘 Troubleshooting

### "No SMS gateway configured"
- Check that your `.env` file has at least one SMS provider configured
- Restart the backend after changing `.env`

### Twilio: "The number is unverified"
- Add the phone number to verified numbers in Twilio Console
- Or upgrade to a paid account

### Fast2SMS: "Invalid API key"
- Ensure you've copied the correct API key
- Check that your account has sufficient balance

### SMS not received
- Check phone number format (must include country code: +1234567890)
- Verify your SMS provider dashboard for delivery status
- Check spam/blocked messages on the phone

---

## 💡 Cost Comparison

| Provider | Region | Cost per SMS | Free Tier |
|----------|--------|--------------|-----------|
| Twilio | Global | $0.0075 | $15 credit |
| Fast2SMS | India | ₹0.15 | No |
| 2Factor.in | India | ₹0.20 | No |
| TextBee | Global | Free | Yes (uses your SIM) |

---

## 🔒 Security Best Practices

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Rotate API keys** if exposed
3. **Monitor usage** to detect unusual activity
4. **Set spending limits** in your SMS provider dashboard
5. **Use environment variables** in production deployments

---

## 🎉 Ready to Go!

Once configured, your OTP codes will be delivered via real SMS to any phone number in the world (or in India, depending on your provider).

**Questions?** Check the FAQ section or contact support.
