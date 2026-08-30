## PROBLEM_FORMULATION_DIRECTIVE

# Stage 1: Problem Reframing & Formulation Directive

This document defines the formal problem reframing and formulation directive for the research project, establishing the mathematical foundations for robust multi-horizon forecasting under sequential geopolitical shocks.

---

## 1. Research Theme & Paradigm Shift

### 1.1 The Theme
The core research theme is defined as:
> **"Theory-Informed Robust Forecasting under Sequential Geopolitical Tail Risks"**

### 1.2 Paradigm Shift from Normal-Regime to Tail-Risk Regimes
* **Traditional Forecasting Paradigm**: Deep learning models for energy markets are typically trained and validated on standard, high-probability periods ("normal regimes") where pricing dynamics are governed by mean-reverting or trend-following behaviors. They optimize for average metrics (e.g., global MAE or RMSE).
* **Robust Tail-Risk Paradigm**: Petroleum retail prices are highly vulnerable to macro-geopolitical disruptions. These events trigger structural breaks and sudden regime changes (tail-risk windows) where historical correlations break down. This research reframes forecasting as a task of robust generalization across a sequence of distinct geopolitical shocks, prioritizing model reliability and directional accuracy during high-volatility tail events.

---

## 2. Sequential Geopolitical Tail-Risk Windows

The research identifies five major geopolitical tail-risk windows. These are formalized as **sequential structural break windows** that serve as the primary testbeds for verifying model robustness.

```
+------------------+     +------------------+     +------------------+     +------------------+     +------------------+
|     Window 1     |     |     Window 2     |     |     Window 3     |     |     Window 4     |     |     Window 5     |
|    2014 OPEC     |     |    2020 COVID    |     |   2022 Russia-   |     |  2024 Red Sea    |     |   2026 US-Iran   |
|    Price War     |     |      Shock       |     |   Ukraine War    |     |  Shipping Crisis |     |    Escalation    |
| (06/14 - 12/14)  | --> | (03/20 - 06/20)  | --> | (02/22 - 05/22)  | --> | (11/23 - 04/24)  | --> | (01/26 - 05/26*) |
+------------------+     +------------------+     +------------------+     +------------------+     +------------------+
                                                                                                    *Dataset ends 02/26
```

### 2.1 Window 1: 2014 OPEC Price War (06/2014 - 12/2014)
* **Geopolitical Catalyst**: OPEC (led by Saudi Arabia) refused to cut crude oil production, choosing to maintain high export volumes to defend market share and price out high-cost US shale producers.
* **Pricing Dynamic**: This triggered a massive supply glut, causing international crude oil prices (WTI and Brent) to plunge from over $100/barrel to under $50/barrel in less than six months.
* **Vietnamese Retail Impact**: Domestic retail prices faced continuous, sharp downward adjustments. The BOG stabilization fund was actively used to moderate the speed of the retail price collapse.

### 2.2 Window 2: 2020 COVID-19 Shock (03/2020 - 06/2020)
* **Geopolitical Catalyst**: The rapid global spread of COVID-19 prompted widespread national lockdowns, paralyzing transportation networks and causing unprecedented global demand destruction. The shock was amplified by a temporary price war between Saudi Arabia and Russia.
* **Pricing Dynamic**: Brent oil fell below $20/barrel, and WTI futures prices famously plunged into negative territory (-$37.63/barrel on April 20, 2020) due to storage capacity exhaustion.
* **Vietnamese Retail Impact**: Domestic demand collapsed alongside prices. Retail fuel prices fell to historical lows, putting severe pressure on local oil distributors and requiring extreme regulatory interventions.

### 2.3 Window 3: 2022 Russia-Ukraine War (02/2022 - 05/2022)
* **Geopolitical Catalyst**: Russia invaded Ukraine in February 2022, prompting the US and EU to impose sweeping financial sanctions and embargoes on Russian energy exports.
* **Pricing Dynamic**: This triggered global supply disruption fears, causing Brent to spike to $139/barrel in March 2022. It led to high volatility and a structural split in global oil trade flows.
* **Vietnamese Retail Impact**: Domestic retail prices surged to all-time highs (MG95 exceeded 32,000 VND/Liter). The government intervened by cutting environmental taxes and depleting the BOG fund to avoid severe inflationary shocks.

### 2.4 Window 4: 2024 Red Sea Shipping Crisis (11/2023 - 04/2024)
* **Geopolitical Catalyst**: Yemen's Houthi rebels launched drone and missile attacks on commercial ships in the Bab al-Mandab Strait (Red Sea) in response to the Gaza conflict.
* **Pricing Dynamic**: Major shipping and tanker companies avoided the Suez Canal, rerouting around the Cape of Good Hope. This added 10-14 days to transit times, significantly raising shipping rates, bunker fuel costs, and insurance premiums.
* **Vietnamese Retail Impact**: While international crude oil price spikes were moderate compared to 2022, import costs (Platt's Singapore prices) rose sharply due to regional shipping premiums, creating a cost-push shock for Vietnamese oil companies.

### 2.5 Window 5: 2026 US-Iran Escalation (01/2026 - 05/2026)
* **Geopolitical Catalyst**: Rising military tensions and direct skirmishes in the Persian Gulf and Strait of Hormuz between US naval forces and Iranian military proxies.
* **Pricing Dynamic**: Threat of closure of the Strait of Hormuz (which carries ~20% of global petroleum consumption), causing sharp, sudden spikes in risk premiums.
* **Vietnamese Retail Impact**: *Econometric note:* The processed dataset (`unified_data.csv`) has been successfully extended to `2026-04-30` using the raw data pipeline. Therefore, the empirical validation of Window 5 fully covers the escalation phase up to the end of April 2026, capturing the tail-risk spikes with real-world observations.

---

## 3. Mathematical Problem Formulation

To avoid the cumulative error propagation inherent in recursive (autoregressive) forecasting models, we formulate the forecasting task as a **Direct Multi-Horizon Prediction** of cumulative log returns.

### 3.1 Direct Forecasting Framework
Let $P_t$ be the domestic retail price (e.g., MG95 or DO 0.05%) at trading day $t$.
Let $X_t$ represent the multi-dimensional vector of exogenous inputs (e.g., Platt's Singapore prices, WTI, Brent, USD Index, GPR) available at day $t$.
For a target horizon $H \in \{1, 3, 5, 10, 20, 60\}$, the forecasting model $f_H$ directly maps the historical look-back window of length $L$ to the future cumulative log return:

$$\hat{R}_{t \to t+H} = f_H(Y_{t-L+1:t}, X_{t-L+1:t})$$

Where the target cumulative log return is defined as:

$$R_{t \to t+H} = \log\left(\frac{P_{t+H}}{P_t}\right)$$

### 3.2 Target Price Reconstruction
The final predicted absolute price level at the future step $t+H$ is reconstructed via:

$$\hat{P}_{t+H} = P_t \cdot \exp\left(\hat{R}_{t \to t+H}\right)$$

### 3.3 Loss Function: Dual-MAE Formulation
To balance the individual errors of co-products (gasoline and diesel) and preserve their price spread relationship, the forecasting network is optimized using the **Dual-MAE loss**:

$$\mathcal{L}_{Dual-MAE} = \mathcal{L}_{individual} + \lambda \cdot \mathcal{L}_{spread}$$

Where:
* $\mathcal{L}_{individual} = \frac{1}{N \cdot M} \sum_{i=1}^N \sum_{j=1}^M |R_{i, j} - \hat{R}_{i, j}|$ for $M$ products.
* $\mathcal{L}_{spread} = \frac{1}{N} \sum_{i=1}^N |(R_{i, A} - R_{i, B}) - (\hat{R}_{i, A} - \hat{R}_{i, B})|$ for product pairs in the same cluster (e.g., MG95 and MG92).
* $\lambda = 0.5$ is the balancing hyperparameter.
