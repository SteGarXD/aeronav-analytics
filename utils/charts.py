import plotly.express as px
import pandas as pd

custom_palette = ["#1f77b4", "#5fa2dd", "#a3c9f7", "#cce4ff", "#e6f2ff"]

def format_russian_number(x):
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f} млн."
    elif x >= 1_000:
        return f"{x / 1_000:.0f} тыс."
    else:
        return str(int(x))

def render_chart(df, group_col, chart_title, kind="bar", showlegend=False):
    agg_data = df.groupby(group_col)["passengers"].sum().reset_index(name="value")

    if agg_data.empty:
        agg_data = pd.DataFrame({group_col: ["Нет данных"], "value": [0]})

    top5 = agg_data.nlargest(5, "value")
    top5["pct"] = top5["value"] / top5["value"].sum()

    if kind == "pie":
        fig = px.pie(
            top5,
            values="value",
            names=group_col,
            hole=0.3,
            color_discrete_sequence=custom_palette
        )
        fig.update_traces(
            textposition="inside",
            textinfo="label+percent+value",
            hovertemplate="<b>%{label}</b><br>Пассажиры: %{value:,}<br>%{percent:.1%}<extra></extra>"
        )
    else:
        if group_col == "contract_short":
            text_labels = top5.apply(lambda r: f"{format_russian_number(r['value'])} ({r['pct']:.1%})", axis=1)
        else:
            text_labels = top5["value"].apply(format_russian_number)

        fig = px.bar(
            top5,
            x="value",
            y=group_col,
            orientation="h",
            text=text_labels,
            color=group_col,
            color_discrete_sequence=custom_palette,
            labels={"value": "Пассажиры", group_col: chart_title}
        )
        fig.update_traces(
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(color="black"),
            hovertemplate="<b>%{y}</b><br>Пассажиры: %{x:,}<extra></extra>"
        )

    fig.update_layout(
        title=chart_title,
        margin=dict(t=50, l=50, r=50, b=50),
        hovermode="closest",
        showlegend=showlegend,
        font=dict(family="Arial", size=14, color="black")
    )

    return fig