import requests
import json
from datetime import datetime
import boto3

# set variables
bucket = "tvsignalscrape"
response = {}
exchange = "BINANCE"
market = "NEOUSDT"
candle = "|15"  # options "|15" = minutes; "" = day; "|1M" = month; "|W" = week
folder = "15"

def get_signal(exchange, market, candle):
    
    url = "https://scanner.tradingview.com/crypto/scan"

    payload = {
        "symbols": {
            "tickers": ["{}:{}".format(exchange, market)],
            "query": {"types": []}
        },
        "columns": [
            "Recommend.Other{}".format(candle),
            "Recommend.All{}".format(candle),
            "Recommend.MA{}".format(candle),
            "RSI{}".format(candle),
            "RSI[1]{}".format(candle),
            "Stoch.K{}".format(candle),
            "Stoch.D{}".format(candle),
            "Stoch.K[1]{}".format(candle),
            "Stoch.D[1]{}".format(candle),
            "CCI20{}".format(candle),
            "CCI20[1]{}".format(candle),
            "ADX{}".format(candle),
            "ADX+DI{}".format(candle),
            "ADX-DI{}".format(candle),
            "ADX+DI[1]{}".format(candle),
            "ADX-DI[1]{}".format(candle),
            "AO{}".format(candle),
            "AO[1]{}".format(candle),
            "Mom{}".format(candle),
            "Mom[1]{}".format(candle),
            "MACD.macd{}".format(candle),
            "MACD.signal{}".format(candle),
            "Rec.Stoch.RSI{}".format(candle),
            "Stoch.RSI.K{}".format(candle),
            "Rec.WR{}".format(candle),
            "W.R{}".format(candle),
            "Rec.BBPower{}".format(candle),
            "BBPower{}".format(candle),
            "Rec.UO{}".format(candle),
            "UO{}".format(candle),
            "EMA10{}".format(candle),
            "close{}".format(candle),
            "SMA10{}".format(candle),
            "EMA20{}".format(candle),
            "SMA20{}".format(candle),
            "EMA30{}".format(candle),
            "SMA30{}".format(candle),
            "EMA50{}".format(candle),
            "SMA50{}".format(candle),
            "EMA100{}".format(candle),
            "SMA100{}".format(candle),
            "EMA200{}".format(candle),
            "SMA200{}".format(candle),
            "Rec.Ichimoku{}".format(candle),
            "Ichimoku.BLine{}".format(candle),
            "Rec.VWMA{}".format(candle),
            "VWMA{}".format(candle),
            "Rec.HullMA9{}".format(candle),
            "HullMA9{}".format(candle),
            "Pivot.M.Classic.S3{}".format(candle),
            "Pivot.M.Classic.S2{}".format(candle),
            "Pivot.M.Classic.S1{}".format(candle),
            "Pivot.M.Classic.Middle{}".format(candle),
            "Pivot.M.Classic.R1{}".format(candle),
            "Pivot.M.Classic.R2{}".format(candle),
            "Pivot.M.Classic.R3{}".format(candle),
            "Pivot.M.Fibonacci.S3{}".format(candle),
            "Pivot.M.Fibonacci.S2{}".format(candle),
            "Pivot.M.Fibonacci.S1{}".format(candle),
            "Pivot.M.Fibonacci.Middle{}".format(candle),
            "Pivot.M.Fibonacci.R1{}".format(candle),
            "Pivot.M.Fibonacci.R2{}".format(candle),
            "Pivot.M.Fibonacci.R3{}".format(candle),
            "Pivot.M.Camarilla.S3{}".format(candle),
            "Pivot.M.Camarilla.S2{}".format(candle),
            "Pivot.M.Camarilla.S1{}".format(candle),
            "Pivot.M.Camarilla.Middle{}".format(candle),
            "Pivot.M.Camarilla.R1{}".format(candle),
            "Pivot.M.Camarilla.R2{}".format(candle),
            "Pivot.M.Camarilla.R3{}".format(candle),
            "Pivot.M.Woodie.S3{}".format(candle),
            "Pivot.M.Woodie.S2{}".format(candle),
            "Pivot.M.Woodie.S1{}".format(candle),
            "Pivot.M.Woodie.Middle{}".format(candle),
            "Pivot.M.Woodie.R1{}".format(candle),
            "Pivot.M.Woodie.R2{}".format(candle),
            "Pivot.M.Woodie.R3{}".format(candle),
            "Pivot.M.Demark.S1{}".format(candle),
            "Pivot.M.Demark.Middle{}".format(candle),
            "Pivot.M.Demark.R1{}".format(candle)
        ]
    }

    resp = requests.post(url, data=json.dumps(payload)).json()
    return dict(zip(payload["columns"], resp["data"][0]["d"]))


def create_csv_string(response):
    """
    This function takes the list returned by the scrape and converts it
    into CSV file format - i.e. comma separated with one row per
    signal. It also writes headers at the top of the file.
    """
    # join response values together to form a CSV.
    text = "\n".join([",".join([market, key, str(val)]) for key, val in response.items()])

    # add the file headers
    text = "\n".join([",".join(["signal", "value"]), text])

    return text


def write_to_s3(text, exchange, market, candle, timestamp):
    """
    This function writes the results to S3 bucket specified at the top of the
    file. Be sure the bucket exists and the Lambda function role has the
    correct permissions otherwise this will fail. The results are stored with
    the naming convention <exchange>/<market>/<candle>/<timestamp>.csv.
    """
    # initialise S3 resource
    s3 = boto3.resource('s3')

    # write object to S3
    s3.Object(
        bucket,
        "{}/{}/{}/{}.csv".format(
            exchange,
            market,
            folder,
            timestamp
        )
    ).put(
        Body=text
    )


def main(timestamp):
    """
    This function puts it all together and performs the whole workflow
    """
    # perform scrape
    response = get_signal(exchange, market, candle)
    text = create_csv_string(response)
    write_to_s3(text, exchange, market, candle, timestamp)


def handle(event, context):
    """
    This is the function actually called by Lambda. It requires the arguments
    'event' and 'context', though we don't actually need to use them here.
    """
    # current time in UTC to create filenames
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")

    # query pairs
    result = main(timestamp)

    return result
