-- Fix documentcategory enum to include 'architecture'
-- Run this if you get error: invalid input value for enum documentcategory: "ARCHITECTURE"

-- Check current enum values
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (
  SELECT oid 
  FROM pg_type 
  WHERE typname = 'documentcategory'
)
ORDER BY enumsortorder;

-- Add 'architecture' if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'architecture' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'documentcategory')
    ) THEN
        ALTER TYPE documentcategory ADD VALUE 'architecture';
        RAISE NOTICE 'Added architecture to documentcategory enum';
    ELSE
        RAISE NOTICE 'architecture already exists in documentcategory enum';
    END IF;
END$$;

-- Verify it was added
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (
  SELECT oid 
  FROM pg_type 
  WHERE typname = 'documentcategory'
)
ORDER BY enumsortorder;
