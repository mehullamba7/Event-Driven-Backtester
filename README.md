Strategies Implemented: 

1. SMA = Simple Moving Average = mean of the last N closing prices.
	•	Short SMA reacts quickly (e.g., 50 bars).
	•	Long SMA reacts slowly (e.g., 200 bars).

A crossover happens when the short SMA crosses the long SMA:
	•	Bullish (Golden Cross): short SMA goes above long SMA → trend turning up → go long (buy).
	•	Bearish (Death Cross): short SMA goes below long SMA → trend turning down → go short (or exit long).

Tiny numeric example

Closes: ... 98, 99, 100, 101, 102
	•	SMA(3) = mean of last 3 = (100+101+102)/3 = 101
	•	SMA(5) = mean of last 5 = 100
Since 101 > 100 → bullish → signal long.