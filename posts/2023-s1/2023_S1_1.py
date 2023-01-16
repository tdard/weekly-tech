import altair as alt
import pandas as pd
import numpy as np


theta = 62 * np.pi / 180
theta = 0

rot_matrix = np.array([
    [np.cos(theta), np.sin(theta)],
    [-np.sin(theta), np.cos(theta)], 
])
stdev = [1, 3]
point_cloud_center = np.array([7.0, 9.0])
vector = np.random.normal(loc=point_cloud_center, scale=stdev, size=(500, 2))

center_rotated = rot_matrix.dot(point_cloud_center)
vector_rotated_transposed = rot_matrix.dot(vector.T)
x, y = vector_rotated_transposed
z = np.random.poisson(3.0, 500)

df = pd.DataFrame({
    "x": x, 
    "y": y, 
    "z": z
})

x_scale = alt.Scale(
    domain=(0, 12), 
    )

y_scale = alt.Scale(
    domain=(0, 20)
)

base = alt.Chart(df, title="Distribution of measurements").encode(
    x=alt.X("x:Q", scale=x_scale, title="X axis"), 
    y=alt.Y("y:Q", scale=y_scale, title="Y axis"), 
    tooltip=["x:Q", "y:Q"], 
)

# (h, k) center of the ellipse

h, k = center_rotated
a, b = stdev

df["within_ellipse"] = df.apply(
    lambda row: ((row.x - h) / a)**2  + ((row.y - k) / b)**2 <= 1, 
    axis=1
)

# Selection interval

brush = alt.selection_multi(encodings=["x", "y"])
brush_x = brush
brush_y = brush


# Display rules for the center of the point cloud
center_rotated = rot_matrix.dot(point_cloud_center)

rule_x = alt.Chart().mark_rule().encode(
    x=alt.datum(center_rotated[0])
)

rule_y = alt.Chart().mark_rule().encode(
    y=alt.datum(center_rotated[1])
)

rules = rule_x + rule_y


# Right chart: distribution of y (with density!)

y_hist = alt.Chart(df, width=100).mark_bar().encode(
    y=alt.Y("y:Q", bin=alt.Bin(step=0.5), 
    #axis=None, 
    title=None, scale=y_scale), 
    x=alt.X("count(y):Q"), 
    tooltip=["count(y):Q"]
).add_selection(brush_y)

# Bottom chart: distribution of x

x_hist = alt.Chart(df, height=100).mark_bar().encode(
    x=alt.X("x:Q", bin=alt.Bin(step=0.5), 
    #axis=None, 
    title=None, scale=x_scale), 
    y=alt.Y("count(x)"), 
    tooltip=["count(x):Q"]
).add_selection(brush_x)


# Display dots
dots = base.mark_point().encode(
    color=alt.condition(brush, "z:Q", alt.value("lightgray"))
)

# Final chart
hchart = alt.hconcat((dots + rules), y_hist)

chart = alt.vconcat(
    alt.hconcat((dots + rules).interactive(), y_hist.interactive()),
    x_hist.interactive()
)#.resolve_scale(x="")


# Display
#display(chart)

if __name__ == '__main__':
    chart.save('2023_S1_1.html')