from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd
from datetime import datetime

# Regisztrálás a fő app számára
register_page(__name__, path="/Pledge")

# Load and preprocess data
file_path = "one-for-the-world-pledges.csv"
df = pd.read_csv(file_path, parse_dates=['pledge_created_at', 'pledge_ended_at'])

# Ensure pledge_starts_at is properly converted to datetime
df['pledge_starts_at'] = pd.to_datetime(df['pledge_starts_at'], errors='coerce')

# Define fiscal year function
def get_fiscal_year(date):
    if pd.isna(date):  # Handle NaT (Not a Time) values
        return "Unknown"
    return f"FY{date.year + 1}" if date.month >= 7 else f"FY{date.year}"

df['fiscal_year'] = df['pledge_starts_at'].apply(get_fiscal_year)

df['monthly_contribution'] = df['contribution_amount'] / 12  # Normalize to monthly

# Filtering
active_pledges = df[df['pledge_status'] == 'Active donor']
future_pledges = df[df['pledge_starts_at'] > pd.Timestamp.today()]

# ARR calculations
active_arr = active_pledges['contribution_amount'].sum()
future_arr = future_pledges['contribution_amount'].sum()
total_arr = active_arr + future_arr

# Monthly contribution calculations
active_monthly = active_pledges['monthly_contribution'].sum()
future_monthly = future_pledges['monthly_contribution'].sum()
total_monthly = active_monthly + future_monthly

# Monthly Attrition Rate (simplified: % of donors lost per month)
attrition_rate = (df['pledge_status'] == 'Lapsed donor').mean() * 100

# Aggregation by fiscal year
fiscal_pledges = df.groupby('fiscal_year', as_index=False)['monthly_contribution'].sum()
fiscal_active = active_pledges.groupby('fiscal_year', as_index=False)['monthly_contribution'].sum()
fiscal_future = future_pledges.groupby('fiscal_year', as_index=False)['monthly_contribution'].sum()

# Add category column
fiscal_pledges['Type'] = 'All Pledges'
fiscal_active['Type'] = 'Active Pledges'
fiscal_future['Type'] = 'Future Pledges'

# Combine data
combined_df = pd.concat([fiscal_pledges, fiscal_active, fiscal_future])

# Color palette
colors = {
    'primary': 'pink',           # All Pledges
    'secondary': '#FFAA80',      # Future Pledges
    'highlight': '#FF5580',      # Active Pledges
    'accent': '#FF0080',         # Extra color if needed
}

# Layout
layout = html.Div([

    # KPI Section
    html.Div([  # KPI Section Here ...
        html.Div(f"ALL ARR: ${total_arr:,.2f} monthly", style={'fontSize': 24, 'fontWeight': 'bold', 'color': 'white', 'padding': '20px', 'borderRadius': '12px', 'backgroundColor': '#333', 'width': '300px', 'textAlign': 'center'}) if total_arr > 0 else None,
        html.Div(f"Future ARR: ${future_arr:,.2f} monthly", style={'fontSize': 24, 'fontWeight': 'bold', 'color': 'white', 'padding': '20px', 'borderRadius': '12px', 'backgroundColor': '#333', 'width': '300px', 'textAlign': 'center'}) if future_arr > 0 else None,
        html.Div(f"Active ARR: ${active_arr:,.2f} monthly", style={'fontSize': 24, 'fontWeight': 'bold', 'color': 'white', 'padding': '20px', 'borderRadius': '12px', 'backgroundColor': '#333', 'width': '300px', 'textAlign': 'center'}) if active_arr > 0 else None,
        html.Div(f"Monthly Attrition Rate: {attrition_rate:.2f}%", style={'fontSize': 24, 'fontWeight': 'bold', 'color': 'red', 'padding': '20px', 'borderRadius': '12px', 'backgroundColor': '#333', 'width': '300px', 'textAlign': 'center'}) if attrition_rate > 0 else None,
    ], style={
        'marginBottom': '20px',
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'center',
        'gap': '30px',
        'flexWrap': 'wrap'
    }),

    # Line Chart
    dcc.Graph(
        id='pledges-line-chart',
        figure=px.line(
            combined_df,
            x='fiscal_year',
            y='monthly_contribution',
            color='Type',
            title='Monthly Contributions by Pledge Type (Line Chart)',
            labels={'monthly_contribution': 'Monthly Contribution ($)', 'fiscal_year': 'Fiscal Year'},
            markers=True,
            color_discrete_map={
                'All Pledges': colors['primary'],
                'Active Pledges': colors['highlight'],
                'Future Pledges': colors['secondary']
            }
        )
        .update_traces(line=dict(width=4))  # Thicker lines
        .update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            title={'font': {'color': 'white'}},
            xaxis=dict(showgrid=False),  # Grid removed
            yaxis=dict(showgrid=False)   # Grid removed
        )
    )

], style={
    'backgroundColor': 'black',
    'color': 'white',
    'padding': '20px',
    'minHeight': '100vh'
})
