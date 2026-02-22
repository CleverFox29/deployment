# Railway Deployment Guide for CraftChain

This guide will help you deploy your CraftChain application to Railway.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- MongoDB Atlas account with a database cluster
- Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Prepare Your MongoDB Database

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster or use an existing one
3. Click "Connect" and select "Connect your application"
4. Copy the connection string (format: `mongodb+srv://username:password@cluster.mongodb.net/`)
5. In Network Access, add `0.0.0.0/0` to allow Railway to connect

### 2. Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)

1. Push your code to a GitHub repository
2. Go to [railway.app](https://railway.app) and sign in
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will automatically detect the configuration

#### Option B: Deploy using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Environment Variables

In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add the following environment variables:

**Required:**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
SECRET_KEY=<generate-secure-random-string>
```

**Optional:**
```
FLASK_ENV=production
FLASK_DEBUG=False
CLEAR_DB_TOKEN=<your-admin-token>
ALLOWED_ORIGINS=https://yourdomain.com
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Deploy and Monitor

1. Railway will automatically deploy when you push to your connected repository
2. Monitor deployment logs in the Railway dashboard
3. Check the health endpoint: `https://your-app.railway.app/api/health`

## Project Structure

The following files are optimized for Railway deployment:

- **Procfile**: Tells Railway how to start your application using Gunicorn
- **runtime.txt**: Specifies the Python version
- **railway.json**: Railway-specific configuration
- **.railwayignore**: Excludes unnecessary files from deployment
- **requirements.txt**: Python dependencies including Gunicorn

## Post-Deployment

### Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Under "Domains", click "Generate Domain" or add a custom domain
3. Follow Railway's instructions to configure DNS

### Monitoring

- View logs in Railway dashboard
- Use the `/api/health` endpoint for health checks
- Railway provides automatic metrics and monitoring

### Environment-Specific Configuration

The app automatically detects Railway environment using `RAILWAY_ENVIRONMENT` variable and adjusts:
- Debug mode (disabled in production)
- CORS settings
- Logging level
- Error handling

## Troubleshooting

### Common Issues

**Database Connection Fails:**
- Verify MONGODB_URI is correctly set
- Check MongoDB Atlas Network Access allows Railway IPs
- Ensure connection string includes password and database name

**App Crashes on Startup:**
- Check Railway logs for errors
- Verify all required environment variables are set
- Ensure SECRET_KEY is configured

**502 Bad Gateway:**
- Check if the app is binding to `0.0.0.0:$PORT`
- Verify Gunicorn is installed in requirements.txt
- Review application logs

### View Logs

```bash
# Using Railway CLI
railway logs
```

Or view them in the Railway dashboard under "Deployments" → "View Logs"

## Scaling

Railway automatically scales based on your plan:
- **Hobby Plan**: Suitable for development/testing
- **Pro Plan**: Production-ready with better resources
- Adjust workers and threads in Procfile for your needs

Current configuration: 4 workers, 2 threads per worker

## Security Best Practices

1. ✅ Use strong SECRET_KEY (32+ characters, random)
2. ✅ Set FLASK_DEBUG=False in production
3. ✅ Configure ALLOWED_ORIGINS for CORS (don't use * in production)
4. ✅ Use MongoDB Atlas IP whitelist
5. ✅ Keep environment variables in Railway, never commit .env
6. ✅ Regularly update dependencies

## Continuous Deployment

Railway automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will detect changes and redeploy automatically.

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- MongoDB Atlas Support: [support.mongodb.com](https://support.mongodb.com)

## Cost Optimization

- Use Railway's free tier for development
- MongoDB Atlas M0 (free tier) for testing
- Optimize database queries and indexes
- Monitor usage in Railway dashboard

---

**Your deployment is ready!** 🚀

Access your app at: `https://your-project-name.railway.app`
