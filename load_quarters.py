"""
https://financialmodelingprep.com/developer/docs
https://github.com/JerBouma/FundamentalAnalysis
"""
import json
from pymongo import MongoClient
import FundamentalAnalysis as fa
import progressbar
import settings


if __name__ == "__main__":
    client = MongoClient(settings.MONGO_URL)
    db = client.get_default_database()
    collection = db['tickersq']

    print("Collect tickers")
    with open("tinkoff_tickers.json") as f:
        tickers = json.load(f)
    print(f"Found {len(tickers)} tickers")

    print("Removing old tickers")
    _ = collection.delete_many({"_id": {"$in": tickers}})
    # print(res)

    print("Start loading")
    for ticker in progressbar.progressbar(tickers):
        res = collection.find_one({"_id": ticker})
        if res:
            print(f"skip {ticker}: exists")
            continue
        api_key = settings.FUNDAMENTAL_ANALYSIS_API_KEY
        profile = fa.profile(ticker, api_key)
        if profile.empty:
            print(f"skip {ticker}: empty profile")
            continue

        income_statement = fa.income_statement(ticker, api_key,
                                               period="quarter")
        if income_statement.empty:
            print(f"skip {ticker}: empty income_statement")
            continue

        balance_sheet_statement = fa.balance_sheet_statement(
            ticker, api_key, period="quarter", limit=4
        )
        if balance_sheet_statement.empty:
            print(f"skip {ticker}: empty balance_sheet_statement")
            continue

        drop_columns = ['description', 'address', 'website', 'image']

        doc = {
            'profile': profile.drop(drop_columns).to_json(),
            'income_statement': income_statement.to_json(),
            'balance_sheet_statement': balance_sheet_statement.to_json(),
        }

        _ = collection.replace_one({"_id": ticker}, doc, upsert=True)
        # print(
        #     f"inserted {ticker}: acknowledged={res.acknowledged}"
        #     f", modified={res.modified_count}"
        # )
