# %%
import duckdb

con = duckdb.connect()

# %%
# %%
df = con.sql("""
    SELECT
        dokumentstatus.dokument.dok_id AS parent_dok_id,
        dokumentstatus.dokument.titel AS parent_titel,
        ref.*
    FROM read_json('datasets/json/betänkande/*.json', auto_detect=true, ignore_errors=true),
    UNNEST(dokumentstatus.dokreferens.referens) AS t(ref)
    WHERE ref.ref_dok_typ IN ('mot', 'prop')
    ORDER BY parent_dok_id
""").pl()

df


# %%
