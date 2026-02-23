# Vercel Deployment Guide for CraftChain

This guide covers deploying your CraftChain application to Vercel with optimized serverless configuration.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **MongoDB Atlas**: Your MongoDB instance must be accessible from the internet
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)

## 🚀 Quick Deployment Steps

### 1. Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### 2. Configure Environment Variables

You need to set these environment variables in Vercel:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/craftchain` |
| `SECRET_KEY` | Flask secret key for sessions | `your-secret-key-here-generate-random` |
| `ALLOWED_ORIGINS` | CORS allowed origins (optional) | `https://yourapp.vercel.app` |

**To set environment variables in Vercel:**
- Dashboard: Project Settings → Environment Variables
- CLI: `vercel env add MONGODB_URI`

### 3. Deploy via Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Vercel will automatically detect the `vercel.json` configuration
4. Add your environment variables
5. Click "Deploy"

### 4. Deploy via Vercel CLI

```bash
# Login to Vercel
vercel login

# Navigate to your project directory
cd path/to/deployment

# Deploy (production)
vercel --prod

# Deploy (preview)
vercel
```

## 🔧 Configuration Explained

### vercel.json

The project includes an optimized `vercel.json` configuration:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*\\.(css|js|html|png|jpg|jpeg|gif|svg|ico|json))",
      "dest": "/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

**Key features:**
- Python serverless function handler in `api/index.py`
- API routes go to serverless function
- Static files served directly
- SPA fallback to `index.html`

### Serverless Optimizations

The application has been optimized for Vercel serverless:

1. **Connection Pooling**: MongoDB client configured with optimal pool settings
2. **Timeout Management**: 10-second function timeout (Vercel default)
3. **Index Caching**: Database indexes only created once per instance
4. **Cold Start Optimization**: Minimal initialization on function startup

## 📊 Vercel Limits (Hobby Plan)

- **Function Duration**: 10 seconds max
- **Function Memory**: 1024 MB
- **Deployments**: Unlimited
- **Bandwidth**: 100 GB/month
- **Invocations**: Unlimited

**Pro Plan** increases limits significantly if needed.

## 🔍 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Should return: {"status": "ok", "message": "CraftChain API is running"}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Ensure `api/index.py` has correct path setup:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

#### 2. MongoDB Connection Timeout
**Error**: `ServerSelectionTimeoutError`

**Solution**: 
- Verify `MONGODB_URI` is set correctly
- Ensure MongoDB Atlas allows connections from all IPs (0.0.0.0/0)
- Check MongoDB Atlas network access settings

#### 3. CORS Issues
**Error**: Browser shows CORS policy errors

**Solution**: Set `ALLOWED_ORIGINS` environment variable:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-app.vercel.app
```

#### 4. Function Timeout
**Error**: `FUNCTION_INVOCATION_TIMEOUT`

**Solution**:
- Optimize database queries
- Add indexes to frequently queried collections
- Consider upgrading to Vercel Pro for 60s timeout

### View Logs

**Vercel Dashboard:**
- Go to your project
- Click on "Deployments"
- Select a deployment
- View "Functions" and "Runtime Logs"

**CLI:**
```bash
vercel logs [deployment-url]
```

## 🔄 CI/CD with Vercel

Vercel automatically deploys:
- **Production**: Commits to `main` or `master` branch
- **Preview**: Pull requests and other branches

Configure in `vercel.json` or project settings.

## 🌐 Custom Domain

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Vercel automatically provisions SSL certificate

## 📈 Monitoring & Performance

### Built-in Analytics
- Vercel provides analytics in the dashboard
- View function invocations, errors, and performance

### Custom Monitoring
Consider adding:
- **Sentry**: Error tracking
- **LogRocket**: Session replay
- **MongoDB Atlas Monitoring**: Database performance

## 🔐 Security Best Practices

1. **Secret Keys**: Never commit secrets to Git
2. **MongoDB**: Use IP allowlist + strong auth
3. **CORS**: Specify exact origins in production
4. **Rate Limiting**: Consider adding rate limiting middleware
5. **Environment Variables**: Use Vercel's encrypted storage

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [MongoDB Atlas Setup](https://docs.atlas.mongodb.com/)
- [Flask Deployment Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)

## 🎯 Next Steps

After successful deployment:
1. ✅ Test all API endpoints
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring and alerts
4. ✅ Set up automatic backups for MongoDB
5. ✅ Review and optimize performance

---

## 💡 Tips for Optimal Performance

### 1. Reduce Cold Starts
- Keep dependencies minimal
- Use lazy imports where possible
- Consider Vercel's Edge Functions for faster response

### 2. Database Optimization
- Use MongoDB indexes effectively
- Implement query result caching
- Consider connection pooling optimization

### 3. Static Asset Optimization
- Use Vercel's CDN for static files
- Compress images before deployment
- Minify CSS/JS files

### 4. Monitoring
- Set up alerts for errors
- Monitor function execution time
- Track database query performance

---

## 🆘 Getting Help

- **Vercel Support**: [vercel.com/support](https://vercel.com/support)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **MongoDB Support**: [support.mongodb.com](https://support.mongodb.com)

---

**Last Updated**: February 2026
**CraftChain Version**: Optimized for Vercel Serverless
