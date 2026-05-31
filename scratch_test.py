import plotly.graph_objects as go
fig = go.Figure(go.Bar(
    x=[250], y=["RT"],
    orientation="h",
    marker_color="red",
    width=0.2
))
fig.write_html("test.html")
