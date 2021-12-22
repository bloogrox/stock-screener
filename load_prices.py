import json
from pymongo import MongoClient
import FundamentalAnalysis as fa
import progressbar
import settings


def chunker(seq, size):
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]


if __name__ == "__main__":
    client = MongoClient(settings.MONGO_URL)
    db = client.get_default_database()
    collection = db['tickers']
    collection_output = db['prices']

    print("Clean old data")
    collection_output.delete_many({})

    print("Collect tickers")
    with open("tinkoff_tickers.json") as f:
        tickers = json.load(f)
    print(f"Found {len(tickers)} tickers")

    print("Start sync")
    CHUNK_SIZE = 100
    for chunk in progressbar.progressbar(chunker(tickers, size=CHUNK_SIZE)):
        comma_sep_tickers = ",".join(chunk)
        df = fa.quote(comma_sep_tickers, settings.FUNDAMENTAL_ANALYSIS_API_KEY)
        df.columns = df.loc["symbol"]
        docs = []
        for ticker in chunk:
            try:
                price = float(df[ticker]["price"])
                marketCap = float(df[ticker]["marketCap"])
            except KeyError as e:
                print("No such ticker:", e)
                continue
            doc = {"_id": ticker, "price": price, "marketCap": marketCap}
            docs.append(doc)
        inserted_ids = collection_output.insert_many(docs).inserted_ids
        print(f"inserted {len(inserted_ids)} tickers: {chunk}")
