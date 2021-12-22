![!](/images/sectors-1.png)
![!](/images/sectors-2.png)
![!](/images/sectors-3.png)


"Rating" is calculated by the formula

```
Enterprise Value / Ebitda / 5 Year Revenue CAGR
```

CAGR - Compound Annual Growth Rate

The lower value of the "Rating" the more undervalued company is


# Quickstart

## Get API Keys

#### Financial Modeling Prep

https://site.financialmodelingprep.com/developer/docs/pricing

You need at least "Starter" plan

#### Free Currency Conversion API

https://freecurrencyapi.net/register


## Environment variables

Copy .env_sample to .env

Paste api keys

## Build image

```
docker-compose build
```

## Load financial data

Load yearly and quarterly financial data

```
bash load.sh
```

## Generate report

Load actual stock prices, calculate metrics, generate report

```
bash run.sh
```
