import pandas as pd


def results_to_dataframe(segment_results):
    return pd.DataFrame(segment_results)


def weighted_avg(df, value_col, weight_col="weight"):
    if df.empty or df[weight_col].sum() == 0:
        return 0.0
    return (df[value_col] * df[weight_col]).sum() / df[weight_col].sum()


def aggregate_results(segment_results):
    df = results_to_dataframe(segment_results)

    overall_support = weighted_avg(df, "support_pct")
    overall_sentiment = weighted_avg(df, "sentiment_score")
    total_population = int(df["count"].sum())

    def breakdown_by(col):
        grouped = (
            df.groupby(col)
            .apply(lambda g: pd.Series({
                "support_pct": weighted_avg(g, "support_pct"),
                "sentiment_score": weighted_avg(g, "sentiment_score"),
                "count": g["count"].sum(),
            }))
            .reset_index()
            .sort_values("count", ascending=False)
        )
        return grouped

    return {
        "overall_support": overall_support,
        "overall_sentiment": overall_sentiment,
        "total_population": total_population,
        "by_income_tier": breakdown_by("income_tier"),
        "by_employment_status": breakdown_by("employment_status"),
        "by_ethnicity": breakdown_by("ethnicity"),
        "segment_df": df.sort_values("count", ascending=False),
    }
