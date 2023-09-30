# %%
import yfinance as yf
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from fredapi import Fred
from datetime import datetime, timedelta
from config import fred_api_key

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize FRED API
fred = Fred(api_key=fred_api_key)

# Setup app layout
app.layout = html.Div([
    html.H2("Russell 2000"),
    dcc.Graph(id='r2000-graph'),

    html.H2("S&P 500"),
    dcc.Graph(id='sp500-graph'),

    html.H2("T-bill Rates"),
    dcc.Graph(id='tbill-graph'),

    dcc.Interval(
            id='interval-component',
            interval=60*1000,  # in milliseconds (1 minute)
            n_intervals=0
    )
])

@app.callback(
    [Output('r2000-graph', 'figure'),
     Output('sp500-graph', 'figure'),
     Output('tbill-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Fetch Russell 2000 data
    r2000_df = yf.Ticker("^RUT").history(period="1y")
    r2000_trace = go.Candlestick(
        x=r2000_df.index,
        open=r2000_df['Open'],
        high=r2000_df['High'],
        low=r2000_df['Low'],
        close=r2000_df['Close']
    )
    r2000_layout = go.Layout(
        title='Russell 2000 - 1 Year History',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    # Fetch S&P 500 data
    sp500_df = yf.Ticker("^GSPC").history(period="1y")
    sp500_trace = go.Candlestick(
        x=sp500_df.index,
        open=sp500_df['Open'],
        high=sp500_df['High'],
        low=sp500_df['Low'],
        close=sp500_df['Close']
    )
    sp500_layout = go.Layout(
        title='S&P 500 - 1 Year History',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    # Fetch T-bill rates
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    durations = ["1 Mo", "3 Mo", "6 Mo", "1 Yr"]
    series_ids = ["DGS1MO", "DGS3MO", "DGS6MO", "DGS1"]
    tbill_traces = []

    for series_id in series_ids:
        tbill_data = fred.get_series(series_id, observation_start=one_year_ago)
        tbill_traces.append(go.Scatter(x=tbill_data.index, y=tbill_data.values, mode='lines', name=series_id))

    tbill_layout = go.Layout(
        title='T-bill Rates - 1 Year History',
        xaxis_title='Date',
        yaxis_title='Rate (%)',
        legend_title_text='Duration'
    )

    return ({'data': [r2000_trace], 'layout': r2000_layout},
            {'data': [sp500_trace], 'layout': sp500_layout},
            {'data': tbill_traces, 'layout': tbill_layout})

if __name__ == '__main__':
    app.run_server(debug=True)


# %%
