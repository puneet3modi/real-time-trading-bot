# 🚀 real-time-trading-bot
A real-time trading bot that connects a client to a server and executes via a trader buy and sell orders based on a given strategy.

**DISCLAIMER: Use our trading strategies for educational purposes only; real-world application involves significant risk and requires professional advice.**

Our example uses QQQ to make buy and sell trade decisions.

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/90b6ca1a-c278-4e58-a9d9-948829513c18)

## 📃 Files

* **server.py**: Simple TCP server that takes a CSV file and streams it to a connected client
* **client.py**: Connects to server to retrieve price updates and creates servers that apply a given decision-making strategy to placing orders with the server
* **strategies.py**: Consolidates multiple strategies that were used and tested.

## 🧠 Strategies

###  📈  Moving Average (MA)

Widely used trading strategy due to its simplicity and effectiveness in trend identification. A moving average smoothes out price data by creating a constantly updated average price over the respective periods (20 and 50 days). 

* Buy signals occur when MA20 crosses above MA50, often interpreted as a bullish sign
* Sell signals occur when MA20 crosses below MA50, often interpreted as a bearish sign
* Signals can also be interpreted from current stock price being above or below the MA20 or 50 thresholds
* MA are lagging indicators, based on past price performance

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/34be0fe4-d24d-48d6-9677-35f174dca64a)

### ⚡ Momentum

Based on the momentum of stock prices, looks to buy securities that are rising and then sell them when they appear to have “peaked” or lost momentum.

* Considers specific number of past periods – often set to 50 previous price points kept in a rolling window – called “lookback period”
* Momentum is calculated as the percentage change between the most recent price and the price at the start of the lookback period
* Uses buy and sell “thresholds” and calculated momentum percent changes that pass through thresholds result in buy or sell signals.
* Assumes past price movements are indicative of future performance, which may not always be the case

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/81bbdf70-88d3-41f0-8af5-1c48a08c6983)

### 📊 Bollinger Bands

Bollinger Bands are a volatility indicator. They consist of a moving average (usually the 20-day moving average) and two standard deviation lines (one above and one below the moving average). Trading signals are generated based on the position of the stock price in relation to the bands. 

* Buy Signal: When the price touches or goes below the lower band, it might indicate that the security is oversold and due for a rise.
* Sell Signal: Conversely, when the price touches or exceeds the upper band, it might suggest the security is overbought and could be poised to drop.

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/2add373b-2f1f-41f1-a35d-1e4a3e1bf561)

### 💊 Moving Average Convergence Divergence

The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price - typically 12-day and 26-day moving averages. A 'signal line', which is the 9-day EMA of the MACD, is also used. Buy signals occur when the MACD crosses above its signal line and sell signals when it crosses below the signal line. Key components:

* **MACD Line**: The difference between the 12-period exponential moving average (EMA) and the 26-period.
* **Signal Line**: A 9-period EMA of the MACD Line.
* **Histogram**: The difference between the MACD line and the Signal line.

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/72fb50f2-00a3-4b31-8f8b-0cf717b8562f)

### 📉 Mean Reversion

Mean Reversion is when returns eventually move back towards the mean or average. 
* **Buy Signal**: When the current price is significantly lower than the historical average, the strategy assumes the price is undervalued and will increase back to the mean. Therefore, it generates a buy order.
* **Sell Signal**: Conversely, when the price is significantly higher than the historical average, the strategy assumes the price is overvalued and will decrease back to the mean. Hence, it generates a sell order.

![image](https://github.com/puneet3modi/real-time-trading-bot/assets/51543073/8074d88d-08d3-4344-ab79-27257f6cb090)

## 🧐 Results

Given a trading period of 4 years specifically for symbol QQQ (Invesco), here are the final balances.

Note: Final balances were calculated by using the Cash at the end of the 4 year period, and liquidating whatever existing holdings. If an exit had been built into the trading strategy for the end of the four year period, it is possible the holdings could have been liquidated earlier at a higher price.

Starting cash at the start of the trading period was $1,000,000. Difference in cash at end of tradind period is shown below.

* Moving Average (MA): + $55,027
* Momentum: + $677,596
* Bollinger Bands: + $395,644
* Mean Reversion: + $644,636
* MACD: + $381,987
