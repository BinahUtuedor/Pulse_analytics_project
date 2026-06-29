-- ==========================================================
-- Metadata table
-- ==========================================================

CREATE TABLE IF NOT EXISTS pipeline_metadata (

    pipeline_name VARCHAR(100) PRIMARY KEY,

    last_loaded TIMESTAMP
);

INSERT INTO pipeline_metadata (

    pipeline_name,

    last_loaded

)

VALUES (

    'olist_pipeline',

    '1900-01-01 00:00:00'

)

ON CONFLICT (pipeline_name)

DO NOTHING;