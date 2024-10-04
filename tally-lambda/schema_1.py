import polars as pl

coord_columns = ["contig", "position", "ref", "alt"]

# the initial schema for variant tally
# plain counts

schema_1 = pl.Schema(
    {
        "contig": pl.String,
        "position": pl.UInt64,
        "ref": pl.String,
        "alt": pl.String,
        "hom_count": pl.UInt32,
        "het_count": pl.UInt32,
    }
)
