from dash import Dash, dcc, html, register_page, Input, Output, callback
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
from datetime import datetime

register_page(__name__, path="/Money_Moved")

# Load exchange rates-enhanced payments data
df_payments = pd.read_csv("exchange_rates.csv")
df_payments['date'] = pd.to_datetime(df_payments['date'])

# Load pledges
df_pledges = pd.read_csv("one-for-the-world-pledges.csv")
df_pledges['pledge_created_at'] = pd.to_datetime(df_pledges['pledge_created_at'], errors='coerce')

# Fiscal year window
start_fy = datetime(2024, 7, 1)
end_fy = datetime(2025, 6, 30)

# Source detection
if 'source' in df_payments.columns:
    source_field = 'source'
elif 'chapter_name' in df_payments.columns:
    source_field = 'chapter_name'
elif 'payment_source' in df_payments.columns:
    source_field = 'payment_source'
else:
    df_payments['derived_source'] = df_payments['payment_platform'].apply(
        lambda x: 'Corporate' if x == 'Benevity' else 'Individual' if x == 'Stripe' else 'Other'
    )
    source_field = 'derived_source'

# Pink color palette (no red)
colors = ['#FFB6C1', '#FF69B4', '#FF85A2', '#FFC0CB', '#FFA6C9', '#FFD1DC']

# FILTERS
filter_section = html.Div([
    html.Div([
        html.Label("Platform", style={"color": "white"}),
        dcc.Dropdown(
            id='platform-filter',
            options=[{"label": x, "value": x} for x in sorted(df_payments['payment_platform'].dropna().unique())],
            multi=True,
            placeholder="Choose Platform",
            style={'color': 'black', 'width': '200px'}
        )
    ])
], style={
    'display': 'flex',
    'flexDirection': 'row',
    'gap': '30px',
    'marginBottom': '40px',
    'justifyContent': 'center'
})

# Add Row Number column
df_payments['Row Number'] = range(1, len(df_payments) + 1)

# AG Grid
grid = dag.AgGrid(
    id='payments-table',
    rowData=df_payments.to_dict("records"),
    columnDefs=[{"field": i, "checkboxSelection": True, "headerCheckboxSelection": True, "rowSelection": "multiple", 'filter': True, 'sortable': True} for i in df_payments.columns] + 
               [{"field": "Row Number", "headerName": "Row Number", "sortable": True, "filter": True}],  # Add row number column
    dashGridOptions={"pagination": True},
    className="ag-theme-alpine-dark"
)

# KPI Card
def kpi_card(title, value, prefix="$", suffix=""):
    formatted_value = f"{prefix}{value:,.2f}{suffix}" if isinstance(value, (int, float)) else value
    return html.Div([
        html.H5(title, style={'color': 'white', 'fontSize': '16px'}),
        html.P(formatted_value, style={'color': 'white', 'fontSize': '24px', 'fontWeight': 'bold'})
    ], style={
        'backgroundColor': '#333',
        'padding': '20px',
        'borderRadius': '12px',
        'width': '250px',
        'textAlign': 'center',
        'margin': '10px'
    })

# KPI placeholders (initial values)
df_payments_ytd = df_payments[(df_payments['date'] >= start_fy) & (df_payments['date'] <= end_fy)]
money_moved_total = df_payments_ytd['amount_usd'].sum()
monthly_avg = df_payments_ytd.groupby(df_payments_ytd['date'].dt.to_period('M'))['amount_usd'].sum().mean()
counterfactual_mm = df_payments_ytd['counterfactuality'].sum()

# INITIAL GRAPHS
platform_totals = df_payments_ytd.groupby('payment_platform')['amount_usd'].sum().reset_index()
source_totals = df_payments_ytd.groupby(source_field)['amount_usd'].sum().reset_index()

source_fig = px.bar(
    source_totals,
    x=source_field,
    y='amount_usd',
    title=f"Money Moved by {source_field.replace('_', ' ').title()}",
    labels={"amount_usd": "Total Money Moved (USD)"},
    color=source_field,
    color_discrete_sequence=['#1E90FF', '#4682B4', '#5F9EA0', '#ADD8E6', '#87CEFA']  # Kék árnyalatok
)
source_fig.update_layout(
    plot_bgcolor='#1a1a1a',  # Sötét háttér
    paper_bgcolor='#1a1a1a',  # Sötét háttér
    font=dict(color='white'),
    title_font=dict(color='white'),
    xaxis=dict(tickcolor='white', showgrid=True, gridcolor='gray'),
    yaxis=dict(tickcolor='white', showgrid=True, gridcolor='gray'),
    showlegend=False
)

pie_fig = px.pie(
    platform_totals,
    names='payment_platform',
    values='amount_usd',
    hole=0.4,
    title="Money Moved by Platform (Donut)",
    color_discrete_sequence=['#1E90FF', '#4682B4', '#5F9EA0', '#ADD8E6', '#87CEFA']  # Kék árnyalatok
)
pie_fig.update_layout(
    plot_bgcolor='#1a1a1a',  # Sötét háttér
    paper_bgcolor='#1a1a1a',  # Sötét háttér
    font=dict(color='white'),
    title_font=dict(color='white'),
    legend_font_color='white'
)

# LAYOUT
layout = html.Div([
    filter_section,

    html.Div([
        kpi_card("Money Moved (Total YTD)", money_moved_total),
        kpi_card("Counterfactual Money Moved", counterfactual_mm),
        kpi_card("Monthly Avg Money Moved", monthly_avg),
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '20px',
        'justifyContent': 'center',
        'padding': '10px',
    }),

    html.Br(),

    html.Div([
        dcc.Graph(id='pie-fig', figure=pie_fig),
        dcc.Graph(id='source-fig', figure=source_fig),
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '50px',
        'justifyContent': 'center',
        'alignItems': 'start',
    }),

    grid
], style={
    'backgroundColor': '#1a1a1a',  # Sötét háttér
    'color': 'white',
    'padding': '40px',
    'minHeight': '100vh'
})

# CALLBACK
@callback(
    Output('payments-table', 'rowData'),
    Output('pie-fig', 'figure'),
    Output('source-fig', 'figure'),
    Input('platform-filter', 'value')
)
def update_dashboard(selected_platforms):
    filtered = df_payments.copy()

    if selected_platforms:
        filtered = filtered[filtered['payment_platform'].isin(selected_platforms)]

    # Pie chart
    pie = px.pie(
        filtered.groupby('payment_platform')['amount_usd'].sum().reset_index(),
        names='payment_platform',
        values='amount_usd',
        hole=0.4,
        title="Money Moved by Platform (Donut)",
        color_discrete_sequence=['#1E90FF', '#4682B4', '#5F9EA0', '#ADD8E6', '#87CEFA']  # Kék árnyalatok
    )
    pie.update_layout(
        plot_bgcolor='#1a1a1a',  # Sötét háttér
        paper_bgcolor='#1a1a1a',  # Sötét háttér
        font=dict(color='white'),
        title_font=dict(color='white'),
        legend_font_color='white'
    )

    # Source bar chart
    source = px.bar(
        filtered.groupby(source_field)['amount_usd'].sum().reset_index(),
        x=source_field,
        y='amount_usd',
        title=f"Money Moved by {source_field.replace('_', ' ').title()}",
        labels={"amount_usd": "Total Money Moved (USD)"},
        color=source_field,
        color_discrete_sequence=['#1E90FF', '#4682B4', '#5F9EA0', '#ADD8E6', '#87CEFA']  # Kék árnyalatok
    )
    source.update_layout(
        plot_bgcolor='#1a1a1a',  # Sötét háttér
        paper_bgcolor='#1a1a1a',  # Sötét háttér
        font=dict(color='white'),
        title_font=dict(color='white'),
        xaxis=dict(tickcolor='white', showgrid=True, gridcolor='gray'),
        yaxis=dict(tickcolor='white', showgrid=True, gridcolor='gray'),
        showlegend=False
    )

    return filtered.to_dict("records"), pie, source
