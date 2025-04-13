from dash import Dash, dcc, html, register_page, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

register_page(__name__, path="/Objectics")

# --- Data Loading ---
df_payments = pd.read_csv("exchange_rates.csv")
df_payments['date'] = pd.to_datetime(df_payments['date'])
df_payments = df_payments.sort_values(by='date')

df_pledges = pd.read_csv("one-for-the-world-pledges.csv")
df_pledges['pledge_created_at'] = pd.to_datetime(df_pledges['pledge_created_at'], errors='coerce')

# --- Fiscal Year Logic ---
df_payments['fiscal_year'] = df_payments['date'].apply(lambda x: x.year if x.month >= 7 else x.year - 1)
df_payments['fiscal_year_label'] = df_payments['fiscal_year'].apply(lambda x: f"FY {x}-{x+1}")
df_payments['fiscal_month_num'] = df_payments['date'].apply(lambda x: x.month - 6 if x.month >= 7 else x.month + 6)

# --- Monthly Aggregation ---
monthly_totals = df_payments.groupby(['fiscal_year_label', 'fiscal_month_num'])['amount_usd'].sum().reset_index()
monthly_totals = monthly_totals.sort_values(['fiscal_year_label', 'fiscal_month_num'])

month_names = {1: 'Jul', 2: 'Aug', 3: 'Sep', 4: 'Oct', 5: 'Nov', 6: 'Dec',
               7: 'Jan', 8: 'Feb', 9: 'Mar', 10: 'Apr', 11: 'May', 12: 'Jun'}
monthly_totals['month_name'] = monthly_totals['fiscal_month_num'].map(month_names)

# --- KPI Calculations ---
money_moved_total = df_payments['amount_usd'].sum()
monthly_avg = df_payments.groupby(df_payments['date'].dt.to_period('M'))['amount_usd'].sum().mean()
active_annualized_run_rate = monthly_avg * 12 if not pd.isna(monthly_avg) else 0
total_pledges = df_pledges['pledge_id'].nunique()
active_pledges = df_pledges[df_pledges['pledge_status'] == 'Active donor']['pledge_id'].nunique()
pledge_attrition_rate = 1 - (active_pledges / total_pledges) if total_pledges > 0 else 0
active_donors = df_pledges[df_pledges['pledge_status'].isin(['one-time', 'Active donor'])]['donor_id'].nunique()

# --- KPI Card Component ---
def kpi_card(title, value, prefix="", suffix=""):
    formatted_value = f"{prefix}{value:,.2f}{suffix}" if isinstance(value, (int, float)) else value
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.P(formatted_value, className="card-text", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ]),
        style={'backgroundColor': '#333', 'color': 'white', 'borderRadius': '12px', 'textAlign': 'center'}
    )

# --- Layout ---
layout = dbc.Container([
    html.Br(),

    dbc.Row([
        dbc.Col(html.Div(id='kpi-money-moved'), width="auto"),
        dbc.Col(html.Div(id='kpi-arr'), width="auto"),
        dbc.Col(html.Div(id='kpi-attrition-rate'), width="auto"),
        dbc.Col(html.Div(id='kpi-active-donors'), width="auto"),
        dbc.Col(html.Div(id='kpi-active-pledges'), width="auto")  # NEW KPI CARD
    ], justify="center", className="mb-4", style={'gap': '20px'}),

    dbc.Row([
        dbc.Col([
            html.Label("Select Fiscal Year:", style={'color': 'white'}),
            dcc.Dropdown(
                id='fiscal-year-dropdown',
                options=[{'label': fy, 'value': fy} for fy in sorted(monthly_totals['fiscal_year_label'].unique())],
                multi=True,
                placeholder='Filter by fiscal year...',
                style={'color': 'black'}
            )
        ], width=4)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Chart Type:", style={'color': 'white'}),
            dcc.RadioItems(
                id='chart-type-radio',
                options=[
                    {'label': 'Line Chart', 'value': 'line'},
                    {'label': 'Grouped Bar Chart', 'value': 'bar'}
                ],
                value='line',
                labelStyle={'color': 'white'}
            )
        ], width=4)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-fig'), width=12)
    ])
], fluid=True, style={"backgroundColor": "black", "padding": "40px"})

# --- Callback to update the chart ---
@callback(
    Output('line-fig', 'figure'),
    [Input('fiscal-year-dropdown', 'value'),
     Input('chart-type-radio', 'value')]
)
def update_chart(selected_years, chart_type):
    if not selected_years:
        filtered = monthly_totals
    else:
        filtered = monthly_totals[monthly_totals['fiscal_year_label'].isin(selected_years)]

    y_col = 'amount_usd'

    if chart_type == 'line':
        fig = px.line(
            filtered,
            x='fiscal_month_num',
            y=y_col,
            color='fiscal_year_label',
            title='Monthly Donations by Fiscal Year',
            labels={'fiscal_month_num': 'Month of Fiscal Year', y_col: 'Total Donations (USD)', 'fiscal_year_label': 'Fiscal Year'},
            markers=True,
            line_shape='spline'
        )
        fig.update_traces(
            line=dict(width=4),
            hovertemplate='Month: %{x}<br>Amount: $%{y:.2f}<extra>%{customdata}</extra>',
            customdata=filtered['fiscal_year_label'].tolist(),
            marker=dict(size=10)
        )
    elif chart_type == 'bar':
        fig = px.bar(
            filtered,
            x='fiscal_month_num',
            y=y_col,
            color='fiscal_year_label',
            title='Monthly Donations by Fiscal Year (Grouped)',
            labels={'fiscal_month_num': 'Month of Fiscal Year', y_col: 'Total Donations (USD)', 'fiscal_year_label': 'Fiscal Year'},
            barmode='group'
        )

    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=[month_names[i] for i in range(1, 13)],
        showgrid=False
    )

    fig.update_yaxes(showgrid=False)

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Total Donations (USD)',
        legend_title='Fiscal Year',
        hovermode='closest',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )

    return fig

# --- Callback to update KPIs ---
@callback(
    Output('kpi-money-moved', 'children'),
    Output('kpi-arr', 'children'),
    Output('kpi-attrition-rate', 'children'),
    Output('kpi-active-donors', 'children'),
    Output('kpi-active-pledges', 'children'),  # NEW OUTPUT
    Input('fiscal-year-dropdown', 'value')
)
def update_kpis(selected_years):
    if not selected_years:
        df_filtered = df_payments
        pledges_filtered = df_pledges
    else:
        fiscal_years = [int(fy.split()[1].split('-')[0]) for fy in selected_years]
        df_filtered = df_payments[df_payments['fiscal_year'].isin(fiscal_years)]
        pledges_filtered = df_pledges[df_pledges['pledge_created_at'].dt.year.isin(fiscal_years)]

    money_moved = df_filtered['amount_usd'].sum()
    monthly_avg = df_filtered.groupby(df_filtered['date'].dt.to_period('M'))['amount_usd'].sum().mean()
    active_arr = monthly_avg * 12 if not pd.isna(monthly_avg) else 0
    active_donors = pledges_filtered[pledges_filtered['pledge_status'].isin(['one-time', 'Active donor'])]['donor_id'].nunique()
    active_pledges_count = pledges_filtered[pledges_filtered['pledge_status'] == 'Active donor']['donor_id'].nunique()

    return (
        kpi_card("Money Moved (Total)", money_moved, "$"),
        kpi_card("Active ARR", active_arr, "$"),
        kpi_card("Pledge Attrition Rate", pledge_attrition_rate * 100, "", "%"),
        kpi_card("Total Active Donors", active_donors),
        kpi_card("Total Active Pledges", active_pledges_count)
    )
