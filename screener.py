import json
import pymongo
import pandas as pd
from millify import millify
from tabulate import tabulate
from pymongo import MongoClient
import settings


def df_from_json(data: str) -> pd.DataFrame:
    return pd.DataFrame.from_dict(json.loads(data))


def take_series(metric: str, data: str) -> pd.Series:
    return df_from_json(data).loc[metric]


def std(ticker: str, metric: str) -> float:
    doc = tickers_coll.find_one({"_id": ticker})
    series = take_series(metric, doc["income_statement"])
    vol = series.iloc[::-1].pct_change().rolling(5).std().to_list()[-1]
    return float(vol)


if __name__ == '__main__':

    client = MongoClient(settings.MONGO_URL)
    db = client.get_default_database()
    collection = db['metrics']
    prices = db['prices']
    tickers_coll = db['tickers']

    for sector in collection.distinct('sector', {}):

        filters = {
            # "EV_EBITDA_revenueG": {"$gt": 0},
            "ebitda_ttm": {"$gt": 0},
            "revenueTTM5YGrowth": {"$gt": 0},
            "ebitdaTTM5YGrowth": {"$gt": 0},
            "years": {"$gt": 5},
            # "EV_EBITDA_ebidtaG": {"$gt": 0},
            # "ebitda": {"$gt": 0},
            "marketCap": {"$gt": 5 * 1e9},
            "sector": sector,
        }

        curs = (
            collection
            .find(
                filter=filters,
                projection={
                    "_id": 1,
                    "EV_EBITDA_revenueG": 1,
                    "marketCap": 1,
                    "enterpriseValue": 1,
                    "ebitda_ttm": 1,
                    "grossProfit_ttm": 1,
                    "revenueTTM5YGrowth": 1,
                    "ebitdaTTM5YGrowth": 1,
                    "sector": 1,
                    "industry": 1,
                    "country": 1,
                })
            .sort("EV_EBITDA_revenueG", pymongo.ASCENDING).limit(10)
        )

        table = []
        for doc in curs:
            ticker = doc["_id"]
            price_doc = prices.find_one({"_id": ticker})
            row = [
                ticker,
                f"{price_doc['price']:.2f}",
                doc["EV_EBITDA_revenueG"],
                millify(doc["marketCap"], 1),
                millify(doc["enterpriseValue"], 1),
                millify(doc["ebitda_ttm"], 1),
                millify(doc["grossProfit_ttm"], 1),
                round(doc["enterpriseValue"] / doc["ebitda_ttm"], 1),
                # round(doc["enterpriseValue"] / doc["grossProfit_ttm"], 1),
                f'{100 * doc["revenueTTM5YGrowth"]:.1f} %',
                f'{100 * doc["ebitdaTTM5YGrowth"]:.1f} %',
                std(ticker, "revenue"),
                std(ticker, "ebitda"),
                doc["sector"][:13],
                doc["industry"][:13],
                doc["country"],
                "https://finviz.com/quote.ashx?t=" + doc["_id"],
            ]
            table.append(row)

        print()
        print(f"Sector: {sector}")
        columns = [
            "Ticker",
            "Price",
            "Rating",
            "mktCap",
            "EV",
            "Ebitda",
            "GP",
            "EV/Ebda",
            # "EV/GP",
            "Rev. Gr",
            "Ebitda Gr",
            "Rev. Std",
            "Ebitda Std",
            "Sector",
            "Industry",
            "",
            "",
        ]
        print(tabulate(table, headers=columns))
