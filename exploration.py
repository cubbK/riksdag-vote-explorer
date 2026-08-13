# %%
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
            END AS refs
        FROM read_json('datasets/json/motioner/*.json', auto_detect=true, ignore_errors=true)
    )
    SELECT
        ref->>'referenstyp'          AS referenstyp,
        ref->>'uppgift'              AS uppgift,
        ref->>'ref_dok_id'           AS ref_dok_id,
        ref->>'ref_dok_typ'          AS ref_dok_typ,
        ref->>'ref_dok_rm'           AS ref_dok_rm,
        ref->>'ref_dok_bet'          AS ref_dok_bet,
        ref->>'ref_dok_titel'        AS ref_dok_titel,
        ref->>'ref_dok_subtitel'     AS ref_dok_subtitel,
        ref->>'ref_dok_subtyp'       AS ref_dok_subtyp,
        ref->>'ref_dok_dokumentnamn' AS ref_dok_dokumentnamn
    FROM src,
    UNNEST(refs) AS t(ref)
    
""").pl()

df_motioner


# %%


df_propositioner = con.sql("""
    WITH src AS (
        SELECT
            CASE json_type(to_json(dokumentstatus.dokreferens.referens))
                WHEN 'ARRAY' THEN CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON[])
                ELSE [CAST(to_json(dokumentstatus.dokreferens.referens) AS JSON)]
            END AS refs
        FROM read_json('datasets/json/propositioner/*.json', auto_detect=true, ignore_errors=true, maximum_object_size=104857600)
    )
    SELECT
        ref->>'referenstyp'          AS referenstyp,
        ref->>'uppgift'              AS uppgift,
        ref->>'ref_dok_id'           AS ref_dok_id,
        ref->>'ref_dok_typ'          AS ref_dok_typ,
        ref->>'ref_dok_rm'           AS ref_dok_rm,
        ref->>'ref_dok_bet'          AS ref_dok_bet,
        ref->>'ref_dok_titel'        AS ref_dok_titel,
        ref->>'ref_dok_subtitel'     AS ref_dok_subtitel,
        ref->>'ref_dok_subtyp'       AS ref_dok_subtyp,
        ref->>'ref_dok_dokumentnamn' AS ref_dok_dokumentnamn
    FROM src,
    UNNEST(refs) AS t(ref)
    
""").pl()

df_propositioner

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
