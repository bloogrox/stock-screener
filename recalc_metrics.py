import progressbar
from pymongo import MongoClient
from metrics import calc_metrics
from exchange_rate import cached_rates
import settings


if __name__ == '__main__':
    client = MongoClient(settings.MONGO_URL)
    db = client.get_default_database()
    collection_tickers_yearly = db['tickers']
    collection_tickers_quarterly = db['tickersq']
    metrics_coll = db['metrics']
    prices = db['prices']

    # metrics_coll.delete_many({})

    cursor = (
        collection_tickers_yearly
        .find(
            {
                "profile": {"$ne": "{}"},
                "income_statement": {"$ne": "{}"},
            }
        )
    )
    rates = cached_rates(settings.FREECURRENCY_API_TOKEN)
    rates["USD"] = 1

    for doc in progressbar.progressbar(cursor):
        ticker = doc["_id"]
        qdoc = collection_tickers_quarterly.find_one({"_id": ticker})
        if not qdoc:
            continue
        price_doc = prices.find_one({"_id": ticker})
        if not price_doc:
            continue

        try:
            d = calc_metrics(doc, qdoc, price_doc["marketCap"], rates)
            d["price"] = price_doc["price"]
            d["marketCap"] = price_doc["marketCap"]
        except Exception as e:
            print(f"skip {ticker}: {e}")
            continue
        res = metrics_coll.replace_one({"_id": doc["_id"]}, d, upsert=True)
