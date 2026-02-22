# 🔑 How to Get Your OpenAI API Key

## Quick Setup (5 minutes)

### Step 1: Create OpenAI Account
1. Go to **https://platform.openai.com/**
2. Click **"Sign up"** or **"Log in"** if you have an account
3. Complete the registration process

### Step 2: Get API Key
1. Once logged in, click on your **profile picture** (top right)
2. Select **"View API keys"** or go to https://platform.openai.com/api-keys
3. Click **"Create new secret key"**
4. Give it a name like "E-commerce Chat Bot"
5. **Copy the API key** (starts with `sk-proj-...`)
   ⚠️ **Important**: You can only see this key once!

### Step 3: Add to Your Project
1. Open your `.env` file in the project
2. Replace `your-openai-api-key-here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
3. Save the file

### Step 4: Test It Works
```bash
python test_ai_chat.py
```

## 💰 Pricing Info
- **Free Tier**: $5 in free credits for new accounts
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens (very cheap!)
- **Average chat**: Costs about $0.001-0.003 per conversation

## 🎉 That's It!
Your AI Chat Assistant will now work perfectly for helping customers and sellers!

## 🆘 Need Help?
- **OpenAI Support**: https://help.openai.com/
- **API Documentation**: https://platform.openai.com/docs