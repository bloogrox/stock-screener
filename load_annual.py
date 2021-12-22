"""
Загружаем отчеты для всех тикеров
"""
import json
import progressbar
from pymongo import MongoClient
import FundamentalAnalysis as fa
import settings


if __name__ == "__main__":

    client = MongoClient(settings.MONGO_URL)
    db = client.get_default_database()
    collection = db['tickers']

    print("Collect tickers")
    with open("tinkoff_tickers.json") as f:
        tickers = json.load(f)
    print(f"Found {len(tickers)} tickers")

    api_key = settings.FUNDAMENTAL_ANALYSIS_API_KEY

    for ticker in progressbar.progressbar(tickers):
        res = collection.find_one({"_id": ticker})
        if res:
            print(f"skip {ticker}: exists")
            continue

        profile = fa.profile(ticker, api_key)
        if profile.empty:
            print("skip: empty profile")
            continue

        income_statement = fa.income_statement(ticker, api_key,
                                               period="annual")

        drop_columns = ['description', 'address', 'website', 'image']
        doc = {
            'profile': profile.drop(drop_columns).to_json(),
            'income_statement': income_statement.to_json(),
        }

        _ = collection.replace_one({"_id": ticker}, doc, upsert=True)
        # print(f"inserted {ticker}: {res}")
