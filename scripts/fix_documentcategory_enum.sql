-- Adicionar valores faltantes ao enum documentcategory
ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'ARCHITECTURE';
ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'GENERATED';
ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'RAG_SOURCE';
