from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("outputs/extracts/forecast_daily_revenue.csv")

df.columns = ["ds", "y"]

model = Prophet()
model.fit(df)

future = model.make_future_dataframe(periods=90)

forecast = model.predict(future)

# Save forecast data
forecast.to_csv(
    "outputs/forecast/revenue_forecast.csv",
    index=False
)

# Forecast chart
fig = model.plot(forecast)
plt.savefig("outputs/forecast/revenue_forecast.png")

# Components chart
fig2 = model.plot_components(forecast)
plt.savefig("outputs/forecast/revenue_components.png")

print("Forecast complete")