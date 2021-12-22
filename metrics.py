import json
import numpy as np
import pandas as pd
from millify import millify


def df_from_json(data: str) -> pd.DataFrame:
    return pd.DataFrame.from_dict(json.loads(data))


def take_metric_raw(metric: str, s: str):
    return df_from_json(s).loc[metric][0]


def take_metric(metric: str, s: str):
    return float(df_from_json(s).loc[metric][0])


def take_series(metric: str, s: str) -> pd.Series:
    return df_from_json(s).loc[metric]


def get_loc(loc: str, df_json: str) -> pd.Series:
    return df_from_json(df_json).loc[loc]


def safe_divide(x, y, if_zero):
    """
    >>> assert safe_divide(1, 0, 100) == 100
    """
    try:
        return x / y
    except ZeroDivisionError:
        return if_zero


def growth(series: pd.Series, n_periods: int = 1) -> float:
    """
    series - [2021, 2020, 2019,...]
    n_periods - 1: yearly growth
                2: 2Y growth
    """
    if len(series) < 2:
        """
        if we have only 1 point, we cannot calc growth,
        so we assume that we have no growth yet, which is 0.0
        """
        print(f"Warning: Series is too short. length - {len(series)}")
        return 0.0
    cut_series = series[:(n_periods + 1)]
    cnt = len(cut_series)
    reversed_ = cut_series.iloc[::-1]
    compound = (
        ((
            reversed_.pct_change() * np.sign(reversed_.shift().astype(float))
        ).dropna() + 1)
        .prod()
    )
    if compound >= 0:
        avg_gr = (compound ** (1 / (cnt - 1))) - 1
    else:
        avg_gr = compound / (cnt - 1)
    return float(avg_gr)


def calc_metrics(
        doc: dict, qdoc: dict, marketCap: float,
        rates: dict, debug=False) -> dict:

    ebidta_quarterly_series = take_series("ebitda", qdoc['income_statement'])
    xxx = (len(ebidta_quarterly_series.values) // 4) * 4
    ebidta_yearly_series = pd.Series(
        ebidta_quarterly_series.values[:xxx].reshape(-1, 4).sum(1)
    )
    ebitdaTTM5YGrowth = growth(ebidta_yearly_series, n_periods=5)

    revenue_quarterly_series = take_series("revenue",
                                           qdoc['income_statement'])
    revenue_yearly_series = pd.Series(
        revenue_quarterly_series.values[:xxx].reshape(-1, 4).sum(1)
    )
    revenueTTM5YGrowth = growth(revenue_yearly_series, n_periods=5)

    reported_currency = take_metric_raw(
        "reportedCurrency", doc["income_statement"]
    )

    ex_rate = rates[reported_currency]

    # rev_ttm_raw = sum(take_series("revenue", qdoc['income_statement'])[:4])
    # revenue_ttm = rev_ttm_raw / ex_rate

    gp_ttm_raw = sum(take_series("grossProfit", qdoc['income_statement'])[:4])
    grossProfit_ttm = gp_ttm_raw / ex_rate

    ebitda_ttm_raw = sum(take_series("ebitda", qdoc['income_statement'])[:4])
    ebitda_ttm = ebitda_ttm_raw / ex_rate

    netDebt_raw = take_metric("netDebt", qdoc['balance_sheet_statement'])
    netDebt = netDebt_raw / ex_rate

    enterpriseValue = marketCap + netDebt

    if debug:
        print("Ticker:", doc["_id"])
        print("mktCap:", millify(marketCap))
        print("EV:", millify(enterpriseValue))

    EV_EBITDA = enterpriseValue / ebitda_ttm

    EV_EBITDA_ebidtaG = EV_EBITDA / (100 * ebitdaTTM5YGrowth)
    EV_EBITDA_revenueG = EV_EBITDA / (100 * revenueTTM5YGrowth)

    years = len(take_series('revenue', doc['income_statement']).values)

    return {
        "enterpriseValue": enterpriseValue,

        "grossProfit_ttm": grossProfit_ttm,
        "ebitda_ttm": ebitda_ttm,
        "EV_EBITDA_ebidtaG": EV_EBITDA_ebidtaG,
        "ebitdaTTM5YGrowth": ebitdaTTM5YGrowth,
        "revenueTTM5YGrowth": revenueTTM5YGrowth,
        "EV_EBITDA_revenueG": EV_EBITDA_revenueG,

        "marketCap": marketCap,
        "years": years,
        "country": take_metric_raw("country", doc['profile']),
        "sector": take_metric_raw("sector", doc['profile']),
        "industry": take_metric_raw("industry", doc['profile']),
        "exchangeShortName": take_metric_raw("exchangeShortName",
                                             doc['profile']),
    }
