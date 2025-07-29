-- Complete Database Schema Fix for Neon PostgreSQL
-- Run this entire script in Neon SQL Editor to fix all missing columns

-- Add missing columns to news_category table
ALTER TABLE news_category ADD COLUMN IF NOT EXISTS slug VARCHAR(100);
ALTER TABLE news_category ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';

-- Add unique constraint for category slug (ignore if already exists)
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

-- Add missing Article columns (THIS IS THE CRITICAL PART)
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
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

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

-- Remove leading/trailing hyphens from article slugs  
UPDATE news_article SET slug = TRIM(BOTH '-' FROM slug);

-- Verify all tables and columns exist
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('news_category', 'news_article') 
ORDER BY table_name, column_name;
