import pandas as pd
import altair as alt
from altair import expr

df = pd.DataFrame({
    "x": [1, 2, 3, 4, 5, 6],
    "y": [15, 16, 5, 7, 3, 30],
    "z": [0.1, 0.4, 0.6, 0.2, 0.15, 0.8],
    "names": ["Pierre", "Paul", "Jacques", "Pierre", "Paul", "Jacques"]
})

chart = alt.Chart(
  df,
  title="Awesome chart 🧨",
  height=150,
  width=400
).encode(
    x=alt.X("x:O", title="Sample index", axis=alt.Axis(labelAngle=90, titleColor="#cc005c")),
    y=alt.Y("y:Q", title="Size", scale=alt.Scale(type="symlog", domainMax=100), axis=alt.Axis(tickCount=10, titleColor="#cc7000")),
    color=alt.Color("z:Q", title="Heat exposure", scale=alt.Scale(scheme="oranges"))
).mark_bar()

if __name__ == '__main__':
    chart.save("chart.html")

