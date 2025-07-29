-- Complete Database Constraint Fix for news_article table
-- Run this in Neon SQL Editor to remove NOT NULL constraints from optional fields

-- Fix all columns that should allow NULL or have defaults
ALTER TABLE news_article ALTER COLUMN description DROP NOT NULL;
ALTER TABLE news_article ALTER COLUMN description SET DEFAULT '';

ALTER TABLE news_article ALTER COLUMN summary DROP NOT NULL;
ALTER TABLE news_article ALTER COLUMN summary SET DEFAULT '';

ALTER TABLE news_article ALTER COLUMN excerpt DROP NOT NULL;
ALTER TABLE news_article ALTER COLUMN excerpt SET DEFAULT '';

ALTER TABLE news_article ALTER COLUMN breaking_news_text DROP NOT NULL;
ALTER TABLE news_article ALTER COLUMN breaking_news_text SET DEFAULT '';

ALTER TABLE news_article ALTER COLUMN featured_image_url DROP NOT NULL;

ALTER TABLE news_article ALTER COLUMN slug DROP NOT NULL;

-- Fix publication_date constraint
ALTER TABLE news_article ALTER COLUMN publication_date DROP NOT NULL;
ALTER TABLE news_article ALTER COLUMN publication_date SET DEFAULT NULL;

-- Ensure updated_at column exists
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Ensure published_at column exists
ALTER TABLE news_article ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;

-- Verify the constraints are fixed
SELECT column_name, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'news_article' 
AND column_name IN ('description', 'summary', 'excerpt', 'breaking_news_text', 'featured_image_url', 'slug', 'updated_at', 'publication_date', 'published_at')
ORDER BY column_name;
