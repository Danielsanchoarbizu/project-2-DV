import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

df = pd.read_csv("data/ds_salaries.csv")

experience_labels = {
    "EN": "Entry Level",
    "MI": "Mid Level",
    "SE": "Senior Level",
    "EX": "Executive Level"
}

df["experience_name"] = df["experience_level"].map(experience_labels)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Data Science Salary Explorer"),

    html.P(
        "This dashboard helps users compare salaries in data science jobs. "
        "Use the filters to explore how salary changes by country, experience, year, "
        "remote work, job title, and company size."
    ),

    html.Label("Company location:"),
    dcc.Dropdown(
        id="country-dropdown",
        options=[{"label": country, "value": country} for country in sorted(df["company_location"].unique())],
        value="US"
    ),

    html.Label("Experience level:"),
    dcc.Dropdown(
        id="experience-dropdown",
        options=[{"label": experience_labels[exp], "value": exp} for exp in sorted(df["experience_level"].unique())],
        value="SE"
    ),

    html.Label("Work year:"),
    dcc.Slider(
        id="year-slider",
        min=df["work_year"].min(),
        max=df["work_year"].max(),
        step=1,
        value=df["work_year"].max(),
        marks={int(year): str(year) for year in sorted(df["work_year"].unique())}
    ),

    html.Label("Remote work type:"),
    dcc.RadioItems(
        id="remote-radio",
        options=[
            {"label": "On-site", "value": 0},
            {"label": "Hybrid", "value": 50},
            {"label": "Fully remote", "value": 100}
        ],
        value=100
    ),

    html.H2("Top Job Titles by Average Salary"),
    dcc.Graph(id="salary-bar"),

    html.H2("Salary Distribution by Company Size"),
    dcc.Graph(id="salary-box"),

    html.H2("Salary by Job Title and Experience"),
    dcc.Graph(id="salary-scatter")
])


@app.callback(
    Output("salary-bar", "figure"),
    Output("salary-box", "figure"),
    Output("salary-scatter", "figure"),
    Input("country-dropdown", "value"),
    Input("experience-dropdown", "value"),
    Input("year-slider", "value"),
    Input("remote-radio", "value")
)
def update_charts(country, experience, year, remote):
    filtered_df = df[
        (df["company_location"] == country) &
        (df["experience_level"] == experience) &
        (df["work_year"] == year) &
        (df["remote_ratio"] == remote)
    ]

    if filtered_df.empty:
        empty_fig = px.bar(title="No data available for these filters")
        return empty_fig, empty_fig, empty_fig

    avg_salary = (
        filtered_df.groupby("job_title")["salary_in_usd"]
        .mean()
        .reset_index()
        .sort_values("salary_in_usd", ascending=False)
        .head(10)
    )

    bar_fig = px.bar(
        avg_salary,
        x="salary_in_usd",
        y="job_title",
        orientation="h",
        title="Top 10 Average Salaries by Job Title",
        labels={
            "salary_in_usd": "Average Salary in USD",
            "job_title": "Job Title"
        }
    )

    box_fig = px.box(
        filtered_df,
        x="company_size",
        y="salary_in_usd",
        title="Salary Distribution by Company Size",
        labels={
            "company_size": "Company Size",
            "salary_in_usd": "Salary in USD"
        }
    )

    scatter_fig = px.scatter(
        filtered_df,
        x="job_title",
        y="salary_in_usd",
        color="company_size",
        size="salary_in_usd",
        hover_data=["employment_type", "employee_residence"],
        title="Individual Salaries by Job Title",
        labels={
            "job_title": "Job Title",
            "salary_in_usd": "Salary in USD",
            "company_size": "Company Size"
        }
    )

    scatter_fig.update_layout(xaxis_tickangle=-45)

    return bar_fig, box_fig, scatter_fig

if __name__ == "__main__":
    app.run(debug=True)
