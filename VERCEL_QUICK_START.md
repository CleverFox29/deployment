# Vercel Quick Start

## 🚀 Deploy to Vercel in 5 Minutes

### Prerequisites
- [ ] MongoDB Atlas account with connection string
- [ ] Vercel account (free)
- [ ] Git repository

### Step 1: Validate Configuration
```bash
python validate_vercel.py
```

### Step 2: Deploy via Dashboard
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Add environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
4. Click **Deploy**

### Step 3: Deploy via CLI (Alternative)
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Step 4: Test Deployment
```bash
# Health check
curl https://your-app.vercel.app/api/health
```

## 📝 Required Environment Variables

| Variable | Example | How to Generate |
|----------|---------|-----------------|
| `MONGODB_URI` | `mongodb+srv://...` | From MongoDB Atlas |
| `SECRET_KEY` | `a1b2c3d4...` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALLOWED_ORIGINS` | `https://yourapp.vercel.app` | Your Vercel domain (optional) |

## ✅ Deployment Checklist

- [ ] `vercel.json` exists
- [ ] `api/index.py` exists
- [ ] Environment variables set in Vercel
- [ ] MongoDB Atlas allows connections from all IPs (0.0.0.0/0)
- [ ] Tested health endpoint: `/api/health`

## 🐛 Common Issues

### Module Import Error
```bash
# Error: ModuleNotFoundError: No module named 'backend'
# Solution: Check api/index.py has correct path setup
```

### Database Connection Error
```bash
# Error: ServerSelectionTimeoutError
# Solution: 
# 1. Verify MONGODB_URI is correct
# 2. Check MongoDB Atlas Network Access → Allow 0.0.0.0/0
```

### CORS Error
```bash
# Error: CORS policy blocked
# Solution: Set ALLOWED_ORIGINS environment variable
ALLOWED_ORIGINS=https://your-app.vercel.app
```

## 📚 Full Documentation

- **Detailed Guide**: [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)
- **What Changed**: [VERCEL_OPTIMIZATION_SUMMARY.md](VERCEL_OPTIMIZATION_SUMMARY.md)
- **Validation Script**: Run `python validate_vercel.py`

## 💡 Pro Tips

1. **Custom Domain**: Add in Project Settings → Domains
2. **View Logs**: Project → Deployments → Select deployment → Runtime Logs
3. **Preview Deployments**: Every branch gets a preview URL
4. **Automatic Deploys**: Push to `main` branch auto-deploys to production

## 🆘 Need Help?

- [Vercel Documentation](https://vercel.com/docs)
- [MongoDB Atlas Support](https://support.mongodb.com)
- Run `python validate_vercel.py` to check configuration

---

**Ready to deploy?** Start with Step 1 above! 🚀
