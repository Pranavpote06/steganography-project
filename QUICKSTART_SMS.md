# 🚀 Quick Start: Enable Real SMS in 5 Minutes

This guide will get you sending **real SMS messages to phone numbers** in under 5 minutes!

---

## ✅ Easiest Option: Twilio (Free Trial - $15 Credit)

### Step 1: Sign Up (2 minutes)
1. Visit: https://www.twilio.com/try-twilio
2. Fill out the form:
   - Email
   - Password
   - First & Last Name
3. Verify your email
4. Verify your phone number (Twilio will call you)

### Step 2: Get Your Credentials (1 minute)
1. After signing in, you'll land on the **Console Dashboard**
2. You'll see:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click "Show" to reveal
3. **Copy both values** - you'll need them in a moment

### Step 3: Get a Phone Number (30 seconds)
1. Click the big **"Get a Trial Number"** button
2. Twilio will assign you a free phone number (e.g., `+15551234567`)
3. Click **"Choose this Number"**
4. **Copy this number** - you'll need it next

### Step 4: Configure StegoCyber (1 minute)

**Option A: Via Web Interface (Easiest)**
1. Start your backend: `cd backend && python run_backend.py`
2. Start your frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173 in your browser
4. Click **"SMS Configuration"** in the sidebar
5. Expand **"Twilio (Global - Recommended)"**
6. Paste your credentials:
   - Account SID
   - Auth Token
   - From Phone Number
7. Click **"Save Configuration"**
8. ✅ Done!

**Option B: Via .env File**
1. Open `backend/.env` in a text editor
2. Add these lines:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+15551234567
```
3. Save the file
4. Restart the backend
5. ✅ Done!

### Step 5: Test It! (30 seconds)
1. Go to **Extract** page
2. Upload a carrier file (audio/video with embedded data)
3. Click "Inspect File"
4. If it requires verification, enter your phone number
5. Click "Send OTP"
6. **Check your phone** - you should receive an SMS! 📱

---

## 🇮🇳 Alternative: Fast2SMS (India Only - Cheapest)

### Step 1: Sign Up
1. Visit: https://www.fast2sms.com/
2. Sign up with your email
3. Verify your account

### Step 2: Recharge
1. Go to: https://www.fast2sms.com/dashboard/wallet-recharge
2. Minimum: ₹10 (sends ~60 SMS)
3. Use any payment method (UPI, Card, Net Banking)

### Step 3: Get API Key
1. Go to: https://www.fast2sms.com/dashboard/dev-api
2. Copy your **API Key**

### Step 4: Configure
Add to `backend/.env`:
```env
FAST2SMS_API_KEY=your_fast2sms_api_key_here
```

Or use the web interface (SMS Configuration page).

---

## 🎯 Important Notes for Twilio Trial

### ✅ What Works
- Send SMS to **verified phone numbers**
- $15 free credit (~2000 SMS)
- Works worldwide
- No credit card required

### ❌ Trial Limitations
- Can only send to numbers you've verified in Twilio Console
- SMS shows "Sent from a Twilio trial account"

### How to Verify a Phone Number
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Click **"Add a phone number"**
3. Enter the recipient's phone number
4. They'll receive a verification code
5. Enter the code
6. ✅ Now you can send SMS to that number!

### When to Upgrade
Upgrade to **paid account** when you want to:
- Send to ANY phone number (not just verified ones)
- Remove "trial account" message
- Get better delivery rates

**Cost after upgrade:**
- No monthly fee (pay-as-you-go)
- ~$0.0075 per SMS in US
- ~$0.05-0.20 per SMS internationally
- Your $15 credit still applies

---

## 🔍 Verify SMS is Working

### Method 1: Check Status in App
1. Open the frontend
2. Go to "Extract" page
3. Click "Check SMS Status" button (bottom right)
4. Should show:
   ```
   ✓ SMS Gateway Active
   Provider: TWILIO
   ```

### Method 2: Check Backend Logs
When you send OTP, you should see:
```
[SMS GATEWAY - TWILIO] Real SMS dispatched to +1234567890
```

Instead of:
```
[SMS GATEWAY NOTICE] No SMS API key is configured
```

### Method 3: Test Send
1. Use the "Extract" feature
2. Upload a file that requires recipient verification
3. Enter your phone number
4. Click "Send OTP"
5. Check your phone!

---

## 🆘 Troubleshooting

### "No SMS gateway configured"
**Solution:** Check that your `.env` file has the correct values and restart the backend.

### "The number is unverified" (Twilio trial)
**Solution:** Go to Twilio Console → Verified Caller IDs → Add the phone number

### "Invalid credentials" (Twilio)
**Solution:** Double-check Account SID and Auth Token. Make sure there are no extra spaces.

### "Insufficient balance" (Fast2SMS)
**Solution:** Recharge your Fast2SMS wallet.

### SMS not received
**Solutions:**
- Check phone number format (must include country code: `+1234567890`)
- Check spam/blocked messages folder
- Verify phone number is correct
- Check SMS provider dashboard for delivery status
- Make sure backend is running and shows successful dispatch in logs

---

## 💰 Cost Comparison

| Provider | Best For | Cost per SMS | Free Trial |
|----------|----------|--------------|------------|
| **Twilio** | Global, Production | $0.0075 - $0.20 | $15 credit |
| **Fast2SMS** | India Budget | ₹0.15 (~$0.002) | No |
| **TextBee** | Testing Only | Free* | Yes |

*TextBee uses your phone's SIM card, so carrier SMS charges may apply

---

## 🎉 Success!

You're now sending **real SMS messages** to phone numbers! 

Your OTP codes will be delivered via actual cellular SMS, making your steganography system production-ready with multi-factor authentication.

### Next Steps
- Test with multiple phone numbers
- Check the "Audit Logs" to see recipient access attempts
- Consider upgrading Twilio for production use
- Monitor your SMS usage in the provider dashboard

---

## 📚 Need More Help?

- **Full Setup Guide:** See `SMS_SETUP_GUIDE.md`
- **SMS Configuration UI:** Click "SMS Configuration" in the app sidebar
- **Twilio Docs:** https://www.twilio.com/docs/sms
- **Fast2SMS Docs:** https://www.fast2sms.com/docs

---

**Questions?** The system is fully configured and ready to send real SMS!
