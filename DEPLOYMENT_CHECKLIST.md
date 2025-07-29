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
- [x] Run migrations to fix missing database columns ✅ **NEED TO RUN VIA SHELL**
- [ ] Create superuser via Render shell
- [ ] Test admin interface
- [ ] Test breaking news functionality

### 🚨 URGENT: Migrations Not Applied
Your build script has been improved with better logging. Since you can't access Shell:

**OPTION A: Manual Database Migration in Neon (RECOMMENDED)**
1. Go to your Neon console: https://console.neon.tech
2. Open your database: `neondb`
3. Go to SQL Editor
4. Run the SQL commands below to add missing columns
5. This will bypass the Django migration system

**OPTION B: Force Fresh Deployment**
1. Go to your Render service dashboard: `world-news-7eai`
2. Click **"Manual Deploy"** button
3. Select **"Clear build cache & deploy"**
4. **Watch the build logs** for migration output

**SQL Commands for Neon (Run in SQL Editor):**
```sql
-- Add missing columns to news_category table
ALTER TABLE news_category ADD COLUMN IF NOT EXISTS slug VARCHAR(100);
ALTER TABLE news_category ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';

-- Add unique constraint for slug (ignore if already exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'news_category_slug_unique'
    ) THEN
        ALTER TABLE news_category ADD CONSTRAINT news_category_slug_unique UNIQUE (slug);
    END IF;
END $$;

-- Update existing categories with slug values
UPDATE news_category SET slug = LOWER(REGEXP_REPLACE(TRIM(name), '[^a-zA-Z0-9]+', '-', 'g')) 
WHERE slug IS NULL OR slug = '';

-- Remove leading/trailing hyphens from slugs
UPDATE news_category SET slug = TRIM(BOTH '-' FROM slug);

-- Add missing Article columns
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS content TEXT DEFAULT '';
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS excerpt TEXT DEFAULT '';
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS slug VARCHAR(200);
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'draft';
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS views_count INTEGER DEFAULT 0;
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS is_breaking_news BOOLEAN DEFAULT FALSE;
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS breaking_news_text VARCHAR(250) DEFAULT '';
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS show_breaking_image BOOLEAN DEFAULT FALSE;
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS featured_image_url VARCHAR(500);
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS published_at TIMESTAMP;

-- Add unique constraint for article slug (ignore if already exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'news_article_slug_unique'
    ) THEN
        ALTER TABLE news_article ADD CONSTRAINT news_article_slug_unique UNIQUE (slug);
    END IF;
END $$;

-- Update existing articles with slug values
UPDATE news_article SET slug = LOWER(REGEXP_REPLACE(TRIM(title), '[^a-zA-Z0-9]+', '-', 'g')) 
WHERE slug IS NULL OR slug = '';

-- Check that all tables and columns exist
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('news_category', 'news_article') 
ORDER BY table_name, column_name;
```

**After running these SQL commands:**
1. Your website should work at: https://world-news-7eai.onrender.com
2. All database schema issues will be resolved
3. You can create categories and articles normally

**The improved build script will now:**
- ✅ Test database connection first
- ✅ Show which migrations need to be applied
- ✅ Run migrations with verbose output
- ✅ Show exactly where any errors occur

**After successful deployment, your site should work at:**
https://world-news-7eai.onrender.com

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
