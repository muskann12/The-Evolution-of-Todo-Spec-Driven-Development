-- Migration: Add priority and tags columns to tasks table
-- Date: 2026-01-01

-- Add priority column (default 'Medium')
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'Medium';

-- Add tags column (default empty string)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS tags VARCHAR(500) DEFAULT '';

-- Update existing NULL values to defaults
UPDATE tasks SET priority = 'Medium' WHERE priority IS NULL;
UPDATE tasks SET tags = '' WHERE tags IS NULL;
