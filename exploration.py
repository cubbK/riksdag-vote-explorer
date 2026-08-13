# %%
from duckdb import pl
import duckdb

con = duckdb.connect()

# %%
# %%
df_betankade = con.sql("""
    SELECT
        dokumentstatus.dokument.dok_id AS parent_dok_id,
        dokumentstatus.dokument.titel AS parent_titel,
        ref.*
    FROM read_json('datasets/json/betänkande/*.json', auto_detect=true, ignore_errors=true),
    UNNEST(dokumentstatus.dokreferens.referens) AS t(ref)
    WHERE ref.ref_dok_typ IN ('mot', 'prop')
    ORDER BY parent_dok_id
""").pl()

df_betankade


# %%

df_motioner = con.sql("""
    WITH src AS (
        SELECT
            CASE json_type(to_json(dokumentstatus.dokreferens.referens))
                WHEN 'ARRAY' THEN CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON[])
                ELSE [CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON)]
            END AS refs,
            dokumentstatus.dokument.titel AS titel,
            CASE json_type(to_json(dokumentstatus.dokintressent.intressent))
                WHEN 'ARRAY' THEN CAST(to_json(dokumentstatus.dokintressent.intressent) AS JSON[])
                ELSE [CAST(to_json(dokumentstatus.dokintressent.intressent) AS JSON)]
            END AS intressenter,
            dokumentstatus.dokument.dok_id AS dok_id
        FROM read_json('datasets/json/motioner/*.json', auto_detect=true, ignore_errors=true, maximum_object_size=104857600)
    )
    SELECT
        ref->>'ref_dok_id'           AS ref_dok_id,
        dok_id,
        titel,
        ref2->>'intressent_id'       AS intressent_id
    FROM src,
    UNNEST(refs) AS t(ref),
    UNNEST(intressenter) AS t2(ref2)
    
""").pl()

df_motioner


# %%


df_propositioner = con.sql("""
    WITH src AS (
        SELECT
            CASE json_type(to_json(dokumentstatus.dokreferens.referens))
                WHEN 'ARRAY' THEN CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON[])
                ELSE [CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON)]
            END AS refs,
            dokumentstatus.dokument.titel AS titel,
            CASE json_type(to_json(dokumentstatus.dokintressent.intressent))
                WHEN 'ARRAY' THEN CAST(to_json(dokumentstatus.dokintressent.intressent) AS JSON[])
                ELSE [CAST(to_json(dokumentstatus.dokintressent.intressent) AS JSON)]
            END AS intressenter,
            dokumentstatus.dokument.dok_id AS dok_id
        FROM read_json('datasets/json/propositioner/*.json', auto_detect=true, ignore_errors=true, maximum_object_size=104857600)
    )
    SELECT
        ref->>'ref_dok_id'           AS ref_dok_id,
        dok_id,
        titel,
        ref2->>'intressent_id'       AS intressent_id
    FROM src,
    UNNEST(refs) AS t(ref),
    UNNEST(intressenter) AS t2(ref2)
    
""").pl()

df_propositioner


# %%

df_dokumenter = pl.concat([df_motioner, df_propositioner])  # ty: ignore[unresolved-attribute]
df_dokumenter

# %%


df_personlista = con.sql("""
    SELECT p.intressent_id, p.tilltalsnamn, p.efternamn, p.parti, p.status, 
    p.bild_url_192
FROM read_json('datasets/json/personlista.json', auto_detect=true, ignore_errors=true),
UNNEST(personlista.person) AS t(p)
WHERE p.status LIKE 'Tjänstgörande%'
ORDER BY p.parti, p.efternamn
""").pl()

df_personlista

# %%
