# Railway Deployment Checklist

Use this checklist to ensure your CraftChain application is properly configured for Railway deployment.

## Pre-Deployment Checklist

### Code Preparation
- [x] Procfile created with Gunicorn configuration
- [x] railway.json configuration file added
- [x] runtime.txt specifies Python version
- [x] .railwayignore excludes unnecessary files
- [x] requirements.txt includes all dependencies (especially gunicorn)
- [x] Hardcoded credentials removed from code
- [x] app.py configured for production
- [x] Error handlers implemented
- [x] Logging configured

### Environment Variables
- [ ] MONGODB_URI configured in Railway
- [ ] SECRET_KEY generated and set (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] CLEAR_DB_TOKEN set (if using admin functions)
- [ ] FLASK_ENV set to "production" (optional)
- [ ] FLASK_DEBUG set to "False" (optional)
- [ ] ALLOWED_ORIGINS configured for CORS (optional)

### Database Setup
- [ ] MongoDB Atlas cluster created
- [ ] Database user created with proper permissions
- [ ] Network access configured (add 0.0.0.0/0 for Railway)
- [ ] Connection string tested and working
- [ ] Database name specified in connection string

### Repository
- [ ] Code pushed to Git repository (GitHub/GitLab/Bitbucket)
- [ ] .env file NOT committed (should be in .gitignore)
- [ ] README.md updated with deployment instructions
- [ ] All changes committed and pushed

## Deployment Checklist

### Railway Setup
- [ ] Railway account created
- [ ] New project created in Railway
- [ ] Repository connected to Railway
- [ ] Environment variables added in Railway dashboard
- [ ] Deployment triggered

### Post-Deployment Verification
- [ ] Deployment completed successfully (check Railway logs)
- [ ] App is running (green status in Railway dashboard)
- [ ] Health endpoint responding: `https://your-app.railway.app/api/health`
- [ ] API endpoints working correctly
- [ ] Database connectivity verified
- [ ] Frontend loading correctly
- [ ] Authentication flow working

### Optional Configuration
- [ ] Custom domain configured (if needed)
- [ ] CORS origins updated if using custom domain
- [ ] SSL/HTTPS verified
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented for database

## Testing Checklist

Test these endpoints after deployment:

- [ ] `GET /` - Homepage loads
- [ ] `GET /api/health` - Returns status: ok
- [ ] `POST /api/auth/register` - User registration works
- [ ] `POST /api/auth/login` - User login works
- [ ] `GET /api/projects` - Projects API responds (with auth)
- [ ] `GET /api/items` - Items API responds
- [ ] Static files load (CSS, JS, images)

## Troubleshooting

If deployment fails, check:

1. **Railway Logs**: View deployment logs for errors
2. **Environment Variables**: Ensure all required variables are set
3. **MongoDB Connection**: Verify connection string and network access
4. **Python Version**: Check runtime.txt matches your local version
5. **Dependencies**: Ensure all packages in requirements.txt are installable

## Rollback Plan

If something goes wrong:

1. Railway keeps previous deployments
2. Go to "Deployments" tab in Railway
3. Select a previous working deployment
4. Click "Redeploy"

## Performance Optimization

After deployment, consider:

- [ ] Monitor response times in Railway dashboard
- [ ] Check database query performance
- [ ] Review logs for errors or warnings
- [ ] Optimize slow endpoints
- [ ] Consider scaling workers if needed (edit Procfile)
- [ ] Add database indexes for frequently queried fields

## Security Review

- [ ] No sensitive data in logs
- [ ] CORS properly configured (not using * in production)
- [ ] SECRET_KEY is strong and unique
- [ ] Database credentials are secure
- [ ] HTTPS is enforced
- [ ] Rate limiting considered (if needed)

## Documentation

- [ ] Update README.md with deployment URL
- [ ] Document environment variables
- [ ] Update API documentation with production endpoint
- [ ] Share deployment guide with team

---

**Deployment Status**: ⏳ Ready to Deploy

Once all checkboxes are complete, your application is ready for Railway deployment!

**Quick Deploy Command** (using Railway CLI):
```bash
railway login
railway init
railway up
```

**Or deploy via GitHub:**
1. Push to GitHub
2. Connect repository in Railway dashboard
3. Railway auto-deploys on push
