# Deployment Checklist

## Pre-deployment Verification

### ✅ Files Ready
- [x] `requirements.txt` - Updated with production dependencies
- [x] `build.sh` - Deployment script created
- [x] `.env` - Environment variables configured
- [x] `settings.py` - Production settings configured
- [x] `README.md` - Deployment instructions added

### ✅ Database
- [x] Neon PostgreSQL database created
- [x] Database connection tested locally
- [x] All migrations applied
- [x] Database URL configured in `.env`

### ✅ Static Files
- [x] WhiteNoise middleware added
- [x] STATIC_ROOT configured
- [x] Static files storage configured

### ✅ Security
- [x] New SECRET_KEY generated
- [x] DEBUG=False in production
- [x] ALLOWED_HOSTS configured

## Render Deployment Steps

### 1. GitHub Repository
- [ ] Push all changes to GitHub
- [ ] Ensure main branch is up to date

### 2. Render Service Setup
- [x] Create new Web Service on Render
- [x] Connect GitHub repository
- [x] Configure build command: `./build.sh`
- [x] Configure start command: `gunicorn news_portal.wsgi:application`

### 3. Environment Variables on Render
Add these environment variables in Render dashboard:

- [x] `DATABASE_URL` = `postgresql://neondb_owner:npg_MHPujd9ksIT5@ep-old-moon-afol7yjb-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&options=endpoint%3Dep-old-moon-afol7yjb`
- [x] `SECRET_KEY` = `x-i2elq8*)p!-15e@0+s72)f#uj4v6g1w%wh&6_wc7yb)*(&6=`
- [x] `DEBUG` = `False`
- [x] `ALLOWED_HOSTS` = `world-news-7eai.onrender.com`

### 4. Post-deployment
- [x] Verify deployment succeeded ✅ App is deployed at world-news-7eai.onrender.com
- [x] Add `ALLOWED_HOSTS` environment variable ✅ Fixed
- [x] Fix Neon database connection error ✅ Fixed
- [ ] **🚨 CRITICAL**: Run migrations to fix missing database columns
- [ ] Create superuser via Render shell
- [ ] Test admin interface
- [ ] Test breaking news functionality

## Important Notes

1. **Replace placeholders**: Update `your-app-name.onrender.com` with your actual Render URL
2. **Keep secrets secure**: Never commit real SECRET_KEY or DATABASE_URL to version control
3. **Test thoroughly**: Always test the deployed application before announcing it's live

## Quick Commands for Render Shell

After deployment, you can run these commands in Render's shell:

```bash
# Create superuser
python manage.py createsuperuser

# Check database connection
python manage.py dbshell

# Collect static files (if needed)
python manage.py collectstatic --noinput

# Run migrations (if needed)
python manage.py migrate
```
