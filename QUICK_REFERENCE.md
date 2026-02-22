# Quick Reference - Railway Deployment

## 🚀 Deploy in 3 Steps

### 1. Set Environment Variables
In Railway dashboard, add:
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=App
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
```

### 2. Connect Repository
- Go to railway.app → New Project
- Connect your GitHub repository
- Railway auto-detects configuration

### 3. Deploy
- Railway automatically deploys
- Access: `https://your-project.railway.app`
- Check health: `https://your-project.railway.app/api/health`

---

## 📋 Quick Checklist

Before deploying:
- [ ] MongoDB Atlas cluster created
- [ ] MongoDB network access allows 0.0.0.0/0
- [ ] Code pushed to GitHub
- [ ] .env file NOT in repository
- [ ] Environment variables ready

After deploying:
- [ ] Health endpoint responds with status: ok
- [ ] No errors in Railway logs
- [ ] API endpoints working
- [ ] Database connected

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway to use Gunicorn |
| `railway.json` | Railway configuration |
| `runtime.txt` | Python version (3.11.7) |
| `.railwayignore` | Files to exclude |
| `requirements.txt` | Python dependencies |

---

## 🔐 Environment Variables

### Required
- `MONGODB_URI` - Database connection string
- `SECRET_KEY` - Flask security key (generate random)

### Optional
- `FLASK_ENV=production` - Environment mode
- `FLASK_DEBUG=False` - Debug mode
- `ALLOWED_ORIGINS=https://yourdomain.com` - CORS

---

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-app.railway.app/api/health

# Expected response:
{"status":"ok","message":"CraftChain API is running","environment":"production"}
```

---

## 📊 Monitoring

View in Railway Dashboard:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Deployments**: History and rollback options

---

## ⚡ Performance

Current configuration:
- 4 workers
- 2 threads per worker
- Handles ~400-800 concurrent requests

To scale, edit `Procfile`:
```
web: gunicorn backend.app:app --workers 8 ...
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "MONGODB_URI not set" | Add in Railway environment variables |
| "SECRET_KEY not set" | Generate and add: `python -c "import secrets; print(secrets.token_hex(32))"` |
| 502 Bad Gateway | Check logs for startup errors |
| Database connection fails | Verify MongoDB network access allows Railway |

---

## 📚 Documentation

- **Full Guide**: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Changes**: [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)

---

## 💡 Tips

1. **Generate SECRET_KEY**: Never use a simple string
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **MongoDB Atlas**: Use M0 (free tier) for testing

3. **Custom Domain**: Configure in Railway → Settings → Domains

4. **Auto-Deploy**: Railway deploys on every git push

5. **Rollback**: Use previous deployment in Railway dashboard

---

## 🎯 What Was Optimized

✅ Production server (Gunicorn)  
✅ No hardcoded credentials  
✅ Environment-based configuration  
✅ Enhanced error handling  
✅ Comprehensive logging  
✅ Security improvements  
✅ Performance tuning  

---

## 💰 Cost

- **Railway Hobby**: $5/month
- **MongoDB M0**: Free
- **Total**: $5/month minimum

---

## 🆘 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- MongoDB Support: https://support.mongodb.com

---

**Your app is ready for Railway! 🎉**
