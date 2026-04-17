# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.1",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _(mo):
    mo.md("""
    ---
    ## 🎓 Personal Portfolio Webpage
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip

    return micropip, mo, pd


@app.cell
async def _(micropip):
    await micropip.install('plotly')
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np

    return go, np


@app.cell
def _(pd):
    # S&P 500 Sample Data
    df_final = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ"],
        "Company": ["Apple Inc.", "Microsoft Corp.", "Alphabet Inc.", "Amazon.com Inc.",
                    "NVIDIA Corp.", "Meta Platforms", "Tesla Inc.", "JPMorgan Chase", "Visa Inc.", "Johnson & Johnson"],
        "Sector_Key": ["Technology", "Technology", "Communication Services", "Consumer Cyclical",
                       "Technology", "Communication Services", "Consumer Cyclical", "Financial Services",
                       "Financial Services", "Healthcare"],
        "Market_Cap": [2850e9, 3100e9, 1950e9, 1800e9, 2200e9, 1250e9, 550e9, 480e9, 520e9, 380e9],
        "Revenue": [383e9, 227e9, 307e9, 574e9, 60e9, 134e9, 97e9, 158e9, 35e9, 85e9],
        "Z_Score_lag": [4.2, 5.1, 3.8, 2.9, 6.5, 3.2, 1.9, 2.1, 4.8, 3.0],
        "AvgCost_of_Debt": [0.025, 0.018, 0.022, 0.035, 0.015, 0.028, 0.045, 0.032, 0.020, 0.027]
    })
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9
    df_final['Revenue_B'] = df_final['Revenue'] / 1e9
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100
    return (df_final,)


@app.cell
def _(df_final, mo):
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3],
        label="Filter by Sector",
    )
    max_cap = int(df_final['Market_Cap_B'].max())
    cap_slider = mo.ui.slider(
        start=0,
        stop=max_cap,
        step=50,
        value=0,
        label="Min Market Cap ($ Billions)"
    )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
    ]
    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
def _(count, filtered_portfolio, go, mo):
    # ===== 3D Chart 1: Scatter (Z-Score vs Debt Cost vs Market Cap) =====
    fig_d1 = go.Figure(data=[
        go.Scatter3d(
            x=filtered_portfolio['Z_Score_lag'],
            y=filtered_portfolio['Debt_Cost_Percent'],
            z=filtered_portfolio['Market_Cap_B'],
            mode='markers+text',
            text=filtered_portfolio['Symbol'],
            textposition='top center',
            marker=dict(
                size=10,
                color=filtered_portfolio['Market_Cap_B'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Mkt Cap (B)", x=1.02)
            ),
            hovertemplate='<b>%{text}</b><br>Z-Score: %{x:.2f}<br>Debt Cost: %{y:.2f}%<br>Market Cap: %{z:.0f}B<extra></extra>'
        )
    ])
    fig_d1.update_layout(
        title=f"1) 3D Scatter – Z-Score × Debt Cost × Market Cap ({count} companies)",
        scene=dict(
            xaxis_title='Altman Z-Score',
            yaxis_title='Debt Cost (%)',
            zaxis_title='Market Cap ($B)'
        ),
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_d1 = mo.ui.plotly(fig_d1)
    return (chart_d1,)


@app.cell
def _(filtered_portfolio, go, mo):
    # ===== 3D Chart 2: 3D Bar Chart – Market Cap & Revenue per Company =====
    fig_d2 = go.Figure()
    # Use unique loop variable names to avoid marimo redefinition errors
    for idx2, row2 in enumerate(filtered_portfolio.itertuples()):
        # Bar for Market Cap
        fig_d2.add_trace(go.Mesh3d(
            x=[idx2-0.3, idx2+0.3, idx2+0.3, idx2-0.3, idx2-0.3, idx2+0.3, idx2+0.3, idx2-0.3],
            y=[-0.3, -0.3, 0.3, 0.3, -0.3, -0.3, 0.3, 0.3],
            z=[0, 0, 0, 0, row2.Market_Cap_B, row2.Market_Cap_B, row2.Market_Cap_B, row2.Market_Cap_B],
            i=[0, 0, 0, 4, 4, 4, 1, 1, 2, 2, 3, 3],
            j=[1, 2, 4, 5, 6, 7, 2, 5, 3, 6, 0, 7],
            k=[2, 3, 5, 6, 7, 4, 5, 6, 6, 7, 7, 4],
            color='royalblue',
            opacity=0.85,
            name=row2.Symbol,
            hovertext=f"{row2.Symbol}: ${row2.Market_Cap_B:.0f}B",
            showscale=False
        ))
        # Bar for Revenue
        fig_d2.add_trace(go.Mesh3d(
            x=[idx2-0.3, idx2+0.3, idx2+0.3, idx2-0.3, idx2-0.3, idx2+0.3, idx2+0.3, idx2-0.3],
            y=[0.7, 0.7, 1.3, 1.3, 0.7, 0.7, 1.3, 1.3],
            z=[0, 0, 0, 0, row2.Revenue_B, row2.Revenue_B, row2.Revenue_B, row2.Revenue_B],
            i=[0, 0, 0, 4, 4, 4, 1, 1, 2, 2, 3, 3],
            j=[1, 2, 4, 5, 6, 7, 2, 5, 3, 6, 0, 7],
            k=[2, 3, 5, 6, 7, 4, 5, 6, 6, 7, 7, 4],
            color='tomato',
            opacity=0.85,
            name=f"{row2.Symbol} Rev",
            hovertext=f"{row2.Symbol}: ${row2.Revenue_B:.0f}B Rev",
            showscale=False
        ))
    fig_d2.update_layout(
        title="2) 3D Bars – Market Cap (blue) vs Revenue (red) by Company",
        scene=dict(
            xaxis=dict(
                title='Company',
                tickmode='array',
                tickvals=list(range(len(filtered_portfolio))),
                ticktext=filtered_portfolio['Symbol'].tolist()
            ),
            yaxis=dict(title='Metric', tickvals=[0, 1], ticktext=['Mkt Cap', 'Revenue']),
            zaxis_title='$ Billions'
        ),
        showlegend=False,
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_d2 = mo.ui.plotly(fig_d2)
    return (chart_d2,)


@app.cell
def _(filtered_portfolio, go, mo, np):
    # ===== 3D Chart 3: 3D Surface – Interpolated Debt Cost Landscape =====
    if len(filtered_portfolio) >= 3:
        xg = np.linspace(filtered_portfolio['Z_Score_lag'].min(),
                         filtered_portfolio['Z_Score_lag'].max(), 25)
        yg = np.linspace(filtered_portfolio['Revenue_B'].min(),
                         filtered_portfolio['Revenue_B'].max(), 25)
        Xg, Yg = np.meshgrid(xg, yg)
        Zg = np.zeros_like(Xg)
        for ix in range(Xg.shape[0]):
            for iy in range(Xg.shape[1]):
                dx = filtered_portfolio['Z_Score_lag'].values - Xg[ix, iy]
                dy = (filtered_portfolio['Revenue_B'].values - Yg[ix, iy]) / \
                     max(filtered_portfolio['Revenue_B'].max(), 1)
                d = np.sqrt(dx**2 + dy**2) + 1e-6
                w = 1.0 / d**2
                Zg[ix, iy] = np.sum(w * filtered_portfolio['Debt_Cost_Percent'].values) / np.sum(w)
        fig_d3 = go.Figure(data=[
            go.Surface(x=Xg, y=Yg, z=Zg, colorscale='Turbo',
                       colorbar=dict(title="Debt Cost %", x=1.02))
        ])
        fig_d3.add_trace(go.Scatter3d(
            x=filtered_portfolio['Z_Score_lag'],
            y=filtered_portfolio['Revenue_B'],
            z=filtered_portfolio['Debt_Cost_Percent'],
            mode='markers+text',
            text=filtered_portfolio['Symbol'],
            marker=dict(size=6, color='black'),
            textposition='top center',
            showlegend=False
        ))
    else:
        fig_d3 = go.Figure()
    fig_d3.update_layout(
        title="3) 3D Surface – Debt Cost Landscape (Z-Score × Revenue)",
        scene=dict(
            xaxis_title='Altman Z-Score',
            yaxis_title='Revenue ($B)',
            zaxis_title='Debt Cost (%)'
        ),
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_d3 = mo.ui.plotly(fig_d3)
    return (chart_d3,)


@app.cell
def _(filtered_portfolio, go, mo):
    # ===== 3D Chart 4: 3D Cones – Risk-Return Vector Field =====
    fig_d4 = go.Figure(data=[
        go.Cone(
            x=filtered_portfolio['Z_Score_lag'],
            y=filtered_portfolio['Debt_Cost_Percent'],
            z=filtered_portfolio['Market_Cap_B'],
            u=[1]*len(filtered_portfolio),
            v=filtered_portfolio['Revenue_B'] / filtered_portfolio['Revenue_B'].max(),
            w=filtered_portfolio['Market_Cap_B'] / filtered_portfolio['Market_Cap_B'].max(),
            sizemode='absolute',
            sizeref=1.2,
            colorscale='Plasma',
            colorbar=dict(title="Intensity", x=1.02),
            text=filtered_portfolio['Symbol'],
            hovertemplate='<b>%{text}</b><br>Z: %{x:.2f}<br>Debt: %{y:.2f}%<br>Cap: %{z:.0f}B<extra></extra>'
        )
    ])
    fig_d4.update_layout(
        title="4) 3D Cones – Risk/Return Vectors (direction ∝ Revenue & Market Cap)",
        scene=dict(
            xaxis_title='Altman Z-Score',
            yaxis_title='Debt Cost (%)',
            zaxis_title='Market Cap ($B)'
        ),
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_d4 = mo.ui.plotly(fig_d4)
    return (chart_d4,)


@app.cell
def _(
    cap_slider,
    chart_d1,
    chart_d2,
    chart_d3,
    chart_d4,
    df_final,
    filtered_portfolio,
    mo,
    sector_dropdown,
):
    full_data_table = mo.ui.table(
        df_final[['Symbol', 'Company', 'Sector_Key', 'Market_Cap_B',
                  'Revenue_B', 'Z_Score_lag', 'Debt_Cost_Percent']],
        selection=None,
        label="Full S&P 500 Sample Dataset"
    )
    filtered_table = mo.ui.table(
        filtered_portfolio[['Symbol', 'Company', 'Sector_Key', 'Market_Cap_B',
                            'Revenue_B', 'Z_Score_lag', 'Debt_Cost_Percent']],
        selection=None,
        label="Filtered View"
    )

    tab_data = mo.vstack([
        mo.md("## 📊 Interactive Credit Risk Analyzer – 3D Edition"),
        mo.callout(
            mo.md("Four interactive 3D charts. Rotate by dragging. Filters below update every chart."),
            kind="info"
        ),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),

        mo.hstack([chart_d1, chart_d2], widths="equal", gap=1),
        mo.hstack([chart_d3, chart_d4], widths="equal", gap=1),

        mo.md("### 📋 Full Dataset"),
        full_data_table,
        mo.md("### 🔍 Current Filtered View"),
        filtered_table,
    ])
    return


@app.cell
def _(mo):
    tab_cv = mo.vstack([
        mo.md(
            """
            # Timur Momani
            ### BSc Accounting & Finance Student
            📍 London, UK | 📧 tmomani@bk.ru | 📞 077780399668  
            🇰🇿 Kazakhstan | 🎂 17 February 2007
            """
        ),
        mo.md(
            """
            ## Profile
            Analytical and globally experienced business student with expertise in operations, marketing, and finance.
            Fluent in English and Russian.
            """
        ),
        mo.md(
            """
            ## Core Skills
            - Operations & Administrative Management
            - Financial Reporting & Data Analysis
            - Campaign Coordination & Marketing Support
            - Client Service & Communication
            - Process Optimisation & Team Collaboration
            """
        ),
        mo.md(
            """
            ## Experience
            **Operations Intern** — Friedrich-Ebert-Stiftung, Almaty (Jun–Aug 2022)  
            - Increased task accuracy 20%, reduced reporting errors 30%

            **Marketing Assistant** — Coca-Cola, Istanbul (Nov 2022–Apr 2023)  
            - Executed campaigns reaching 15k+ consumers; +25% social engagement

            **Finance Apprentice** — KPMG, Almaty (May–Aug 2023)  
            - Processed 100+ invoices weekly; 20% workflow efficiency gain

            **Front-of-House Assistant** — Ferrero, Istanbul (Dec 2023–Feb 2024)  
            - 90%+ guest satisfaction; 15% wait-time reduction
            """
        ),
        mo.md(
            """
            ## Education
            **City, University of London** – BSc Accounting & Finance (Ongoing)  
            **MEF International School, Istanbul** – High School Diploma + IB  
            **Kazakhstan International School, Almaty** – Diploma
            """
        ),
        mo.md(
            """
            ## Technical Skills
            <span style="background:#e9ecef; padding:5px 10px; border-radius:20px; margin:3px; display:inline-block;">Excel</span>
            <span style="background:#e9ecef; padding:5px 10px; border-radius:20px; margin:3px; display:inline-block;">Data Handling</span>
            <span style="background:#e9ecef; padding:5px 10px; border-radius:20px; margin:3px; display:inline-block;">Financial Docs</span>
            <span style="background:#e9ecef; padding:5px 10px; border-radius:20px; margin:3px; display:inline-block;">Social Media</span>
            <span style="background:#e9ecef; padding:5px 10px; border-radius:20px; margin:3px; display:inline-block;">Customer Service</span>
            """
        )
    ])
    return


@app.cell
def _(mo):
    monthly_profit_slider = mo.ui.slider(
        start=5000,
        stop=20000,
        step=1000,
        value=12500,
        label="Assumed Monthly Profit (USD)"
    )
    return (monthly_profit_slider,)


@app.cell
def _(go, mo, monthly_profit_slider, pd):
    def generate_trading_growth(monthly_profit):
        months = list(range(0, 16))
        initial = 1000
        values = [initial + monthly_profit * m for m in months]
        return pd.DataFrame({'Month': months, 'Portfolio Value (USD)': values})

    df_growth = generate_trading_growth(monthly_profit_slider.value)
    fig_trading = go.Figure()
    fig_trading.add_trace(go.Scatter(
        x=df_growth['Month'],
        y=df_growth['Portfolio Value (USD)'],
        mode='lines+markers',
        name='Portfolio Growth',
        line=dict(color='green', width=3)
    ))
    fig_trading.update_layout(
        title=f"Projected Growth (Initial $1,000 → ${df_growth['Portfolio Value (USD)'].iloc[-1]:,.0f})",
        xaxis_title="Month",
        yaxis_title="Value (USD)",
        template='presentation',
        height=400
    )
    fig_trading.add_hline(y=230000, line_dash="dash", line_color="gold",
                          annotation_text="Actual Achieved: $230k")
    trading_chart = mo.ui.plotly(fig_trading)
    return (trading_chart,)


@app.cell
def _(mo, pd):
    btc_trades = pd.DataFrame({
        'Trade': [1, 2, 3, 4, 5],
        'Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-01'],
        'Action': ['Buy', 'Sell', 'Buy', 'Sell', 'Sell'],
        'Amount ($)': [10000, -3000, -4000, 2000, -5000],
        'Portfolio Value ($)': [10000, 7000, 3000, 5000, -2000]
    })
    trade_slider = mo.ui.slider(
        start=1,
        stop=5,
        step=1,
        value=5,
        label="Select Trade to Highlight"
    )
    return btc_trades, trade_slider


@app.cell
def _(btc_trades, go, mo, monthly_profit_slider, trade_slider, trading_chart):
    highlight_trade = trade_slider.value
    fig_btc_3d = go.Figure()
    fig_btc_3d.add_trace(go.Scatter3d(
        x=btc_trades['Trade'],
        y=[1,2,3,4,5],
        z=btc_trades['Portfolio Value ($)'],
        mode='lines+markers',
        line=dict(color='red', width=5),
        marker=dict(size=8, color=btc_trades['Portfolio Value ($)'], colorscale='RdBu', showscale=True),
        name='Portfolio Value',
        hovertemplate='Trade %{x}<br>Value: $%{z:,.0f}<extra></extra>'
    ))
    highlight_row = btc_trades[btc_trades['Trade'] == highlight_trade].iloc[0]
    fig_btc_3d.add_trace(go.Scatter3d(
        x=[highlight_trade],
        y=[highlight_trade],
        z=[highlight_row['Portfolio Value ($)']],
        mode='markers',
        marker=dict(size=15, color='yellow', symbol='diamond'),
        name=f'Trade {highlight_trade} Highlight',
        showlegend=False
    ))
    fig_btc_3d.update_layout(
        title="Bitcoin Trading Journey: $10,000 → -$2,000 (5 Trades)",
        scene=dict(
            xaxis_title='Trade Number',
            yaxis_title='Time Step',
            zaxis_title='Portfolio Value ($)',
            yaxis=dict(visible=False)
        ),
        template='presentation',
        height=500
    )
    btc_chart_3d = mo.ui.plotly(fig_btc_3d)

    tab_passion = mo.vstack([
        mo.md(
            """
            ## 🏆 Passion Projects

            ### 🚗 Drift Car Build: Nissan S2000 → 1500 HP
            Modified a Nissan S2000 into a manual drift champion with 1500 horsepower.
            """
        ),
        mo.md("### 📈 Silver Trading Portfolio"),
        mo.callout(
            mo.md("Grew **$1,000 → $230,000** in under 15 months, averaging **$10k–$15k monthly profit**."),
            kind="success"
        ),
        mo.md("**Interactive Simulator:** Adjust monthly profit to see growth trajectory."),
        monthly_profit_slider,
        trading_chart,
        mo.md("### ₿ Bitcoin Trading: The $10k Lesson"),
        mo.callout(
            mo.md("Turned **$10,000 into -$2,000** across five trades – a harsh but valuable lesson in risk management."),
            kind="warn"
        ),
        mo.md("**Interactive 3D Chart:** Drag to rotate. Use slider to highlight specific trades."),
        trade_slider,
        btc_chart_3d,
        mo.md(
            """
            ### 🥊 Professional Boxing Champion
            Light Heavyweight Division – Competed and won at professional level.
            """
        )
    ])
    return


@app.cell
def _(mo, pd):
    # Travel data with each city once (most recent year)
    travel_data = pd.DataFrame([
        {'City': 'Almaty', 'Country': 'Kazakhstan', 'Lat': 43.222, 'Lon': 76.851, 'Year': 2006, 'Status': 'Home'},
        {'City': 'Kuala Lumpur', 'Country': 'Malaysia', 'Lat': 3.139, 'Lon': 101.686, 'Year': 2015, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2025, 'Status': 'Lived'},
        {'City': 'Dubai', 'Country': 'UAE', 'Lat': 25.204, 'Lon': 55.270, 'Year': 2024, 'Status': 'Visited'},
        {'City': 'Los Angeles', 'Country': 'USA', 'Lat': 34.052, 'Lon': -118.243, 'Year': 2018, 'Status': 'Visited'},
        {'City': 'London', 'Country': 'United Kingdom', 'Lat': 51.507, 'Lon': -0.128, 'Year': 2025, 'Status': 'Current'},
        {'City': 'Lisbon', 'Country': 'Portugal', 'Lat': 38.722, 'Lon': -9.139, 'Year': 2022, 'Status': 'Visited'},
        {'City': 'Antalya', 'Country': 'Turkey', 'Lat': 36.896, 'Lon': 30.713, 'Year': 2021, 'Status': 'Visited'},
        {'City': 'Ankara', 'Country': 'Turkey', 'Lat': 39.933, 'Lon': 32.859, 'Year': 2020, 'Status': 'Visited'},
        {'City': 'San Diego', 'Country': 'USA', 'Lat': 32.715, 'Lon': -117.161, 'Year': 2019, 'Status': 'Visited'},
        {'City': 'Santa Monica', 'Country': 'USA', 'Lat': 34.019, 'Lon': -118.491, 'Year': 2018, 'Status': 'Visited'},
        {'City': 'Phuket', 'Country': 'Thailand', 'Lat': 7.880, 'Lon': 98.392, 'Year': 2023, 'Status': 'Visited'},
        {'City': 'Hong Kong', 'Country': 'Hong Kong', 'Lat': 22.319, 'Lon': 114.169, 'Year': 2024, 'Status': 'Visited'},
        {'City': 'New York', 'Country': 'USA', 'Lat': 40.712, 'Lon': -74.006, 'Year': 2022, 'Status': 'Visited'},
        {'City': 'Washington', 'Country': 'USA', 'Lat': 38.907, 'Lon': -77.037, 'Year': 2021, 'Status': 'Visited'},
        {'City': 'Austin', 'Country': 'USA', 'Lat': 30.267, 'Lon': -97.743, 'Year': 2023, 'Status': 'Visited'},
        {'City': 'Amman', 'Country': 'Jordan', 'Lat': 31.945, 'Lon': 35.926, 'Year': 2022, 'Status': 'Visited'},
        {'City': 'Tokyo', 'Country': 'Japan', 'Lat': 35.6762, 'Lon': 139.6503, 'Year': 2023, 'Status': 'Visited'},
        {'City': 'Paris', 'Country': 'France', 'Lat': 48.8566, 'Lon': 2.3522, 'Year': 2022, 'Status': 'Visited'},
        {'City': 'Rome', 'Country': 'Italy', 'Lat': 41.9028, 'Lon': 12.4964, 'Year': 2021, 'Status': 'Visited'},
        {'City': 'Rio de Janeiro', 'Country': 'Brazil', 'Lat': -22.9068, 'Lon': -43.1729, 'Year': 2024, 'Status': 'Visited'},
        {'City': 'Sydney', 'Country': 'Australia', 'Lat': -33.8688, 'Lon': 151.2093, 'Year': 2023, 'Status': 'Visited'},
        {'City': 'Cairo', 'Country': 'Egypt', 'Lat': 30.0444, 'Lon': 31.2357, 'Year': 2022, 'Status': 'Visited'},
        {'City': 'Cape Town', 'Country': 'South Africa', 'Lat': -33.9249, 'Lon': 18.4241, 'Year': 2024, 'Status': 'Visited'},
    ])

    travel_data = travel_data.drop_duplicates()

    min_year = int(travel_data['Year'].min())
    max_year = int(travel_data['Year'].max())
    year_slider = mo.ui.range_slider(
        start=min_year,
        stop=max_year,
        step=1,
        value=[min_year, max_year],
        label="Filter by Year Range"
    )
    return travel_data, year_slider


@app.cell
def _(go, mo, travel_data, year_slider):
    filtered_travel = travel_data[
        (travel_data['Year'] >= year_slider.value[0]) &
        (travel_data['Year'] <= year_slider.value[1])
    ]

    fig_globe = go.Figure()
    for status, color in {'Home': 'goldenrod', 'Lived': 'darkblue', 'Visited': 'purple', 'Current': 'crimson'}.items():
        subset = filtered_travel[filtered_travel['Status'] == status]
        if not subset.empty:
            fig_globe.add_trace(go.Scattergeo(
                lon=subset['Lon'],
                lat=subset['Lat'],
                text=subset['City'] + '<br>' + subset['Country'] + '<br>Year: ' + subset['Year'].astype(str),
                mode='markers',
                marker=dict(size=8, color=color, line=dict(width=1, color='white')),
                name=status,
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))

    fig_globe.update_layout(
        title=f"🌍 3D Globe – My Global Footprint ({len(filtered_travel)} records)",
        geo=dict(
            projection_type='orthographic',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            coastlinecolor='rgb(150,150,150)',
            showocean=True,
            oceancolor='rgb(220,240,255)',
        ),
        template='plotly_white',
        height=600
    )
    globe_chart = mo.ui.plotly(fig_globe)

    tab_hobbies = mo.vstack([
        mo.md(
            """
            ## 🌍 Hobbies: Travel & Photography
            When I'm not working, I explore the world with my camera.
            """
        ),
        mo.callout(
            mo.md("Use the slider to filter by years. **Drag the globe to rotate!**"),
            kind="info"
        ),
        year_slider,
        globe_chart,
        mo.md(
            """
            ### 📸 Photography
            Street, automotive, and landscape photography.
            """
        )
    ])
    return


@app.cell
def _(mo, pd):
    try:
        fls_df = pd.read_pickle('public/fls_sent_Moodle.pkl')
        fls_source = "**Source:** `fls_sent_Moodle.pkl` (provided in module)"
    except FileNotFoundError:
        fls_df = pd.DataFrame({
            'company_name': ['Airtel Africa', 'Babcock', 'Bunzl', 'Croda', 'Diageo',
                             'Airtel Africa', 'Babcock', 'Bunzl', 'Croda', 'Diageo',
                             'Airtel Africa', 'Babcock', 'Bunzl', 'Croda', 'Diageo'],
            'year': [2022]*5 + [2023]*5 + [2024]*5,
            'forward_looking_sentences': [
                "Growth opportunities remain strong across our markets.",
                "We face some uncertain conditions and risk in the year ahead.",
                "Our compounding strategy continues to deliver positive value.",
                "We expect a decline in certain segments due to weak demand.",
                "Challenging conditions persist but we remain confident.",
                "We continue to see strong growth and improve margins.",
                "Risk of decline in key markets is weighing on guidance.",
                "Consistent compounding supports continued value creation.",
                "We expect mid to high single digit sales growth.",
                "I continue to be confident in our future despite headwinds.",
                "Positive momentum across all regions; growth is strong.",
                "The Board is confident of making further progress.",
                "Opportunity pipeline is growing with improved visibility.",
                "Mid to high single digit growth expected in 2025.",
                "Challenging but we remain confident about long-term."
            ]
        })
        fls_source = "**Source:** Sample data (file `fls_sent_Moodle.pkl` not found – using built-in examples)."

    positive_words = ['growth', 'opportunity', 'strong', 'confident', 'improve', 'positive', 'increase']
    negative_words = ['decline', 'risk', 'uncertain', 'challeng', 'weak', 'loss', 'decrease']

    def count_pos(text):
        if not isinstance(text, str):
            return 0
        t = text.lower()
        return sum(t.count(w) for w in positive_words)

    def count_neg(text):
        if not isinstance(text, str):
            return 0
        t = text.lower()
        return sum(t.count(w) for w in negative_words)

    fls_df['pos_count'] = fls_df['forward_looking_sentences'].apply(count_pos)
    fls_df['neg_count'] = fls_df['forward_looking_sentences'].apply(count_neg)
    fls_df['sentiment_score'] = fls_df['pos_count'] - fls_df['neg_count']
    fls_df['word_count'] = fls_df['forward_looking_sentences'].apply(
        lambda x: len(str(x).split()) if isinstance(x, str) else 0
    )

    company_list = sorted(fls_df['company_name'].unique())
    company_dropdown = mo.ui.dropdown(
        options=company_list,
        value=company_list[0],
        label="Select Company"
    )
    return company_dropdown, company_list, fls_df, fls_source


@app.cell
def _(company_list, fls_df, go, mo, np):
    # ===== NLP 3D Chart 1: 3D Scatter – Sentiment by Company × Year =====
    fig_nlp1 = go.Figure(data=[
        go.Scatter3d(
            x=[company_list.index(c) for c in fls_df['company_name']],
            y=fls_df['year'],
            z=fls_df['sentiment_score'],
            mode='markers',
            marker=dict(
                size=10,
                color=fls_df['sentiment_score'],
                colorscale='RdYlGn',
                cmin=-3, cmax=3,
                showscale=True,
                colorbar=dict(title="Sentiment")
            ),
            text=fls_df['company_name'],
            hovertemplate='<b>%{text}</b><br>Year: %{y}<br>Sentiment: %{z}<extra></extra>'
        )
    ])
    fig_nlp1.update_layout(
        title="1) 3D Sentiment Cloud – Company × Year × Sentiment Score",
        scene=dict(
            xaxis=dict(
                title='Company',
                tickmode='array',
                tickvals=list(range(len(company_list))),
                ticktext=company_list
            ),
            yaxis_title='Year',
            zaxis_title='Sentiment Score'
        ),
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_nlp1 = mo.ui.plotly(fig_nlp1)

    # ===== NLP 3D Chart 2: 3D Surface – Sentiment Matrix =====
    years = sorted(fls_df['year'].unique())
    matrix = np.zeros((len(company_list), len(years)))
    for i_c, c in enumerate(company_list):
        for i_y, y in enumerate(years):
            sub = fls_df[(fls_df['company_name'] == c) & (fls_df['year'] == y)]
            matrix[i_c, i_y] = sub['sentiment_score'].mean() if len(sub) else 0
    fig_nlp2 = go.Figure(data=[
        go.Surface(
            x=years,
            y=company_list,
            z=matrix,
            colorscale='RdYlGn',
            cmin=-3, cmax=3,
            colorbar=dict(title="Sentiment")
        )
    ])
    fig_nlp2.update_layout(
        title="2) 3D Surface – Sentiment Matrix (Year × Company)",
        scene=dict(
            xaxis_title='Year',
            yaxis_title='Company',
            zaxis_title='Sentiment Score'
        ),
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_nlp2 = mo.ui.plotly(fig_nlp2)

    # ===== NLP 3D Chart 3: 3D Bar – Pos vs Neg word counts by Company =====
    agg = fls_df.groupby('company_name').agg(
        pos=('pos_count', 'sum'),
        neg=('neg_count', 'sum'),
        total=('word_count', 'sum')
    ).reset_index()
    fig_nlp3 = go.Figure()
    # Use unique loop variable to avoid redefinition
    for idx3, row3 in enumerate(agg.itertuples()):
        # Positive bar (green)
        fig_nlp3.add_trace(go.Mesh3d(
            x=[idx3-0.3, idx3+0.3, idx3+0.3, idx3-0.3, idx3-0.3, idx3+0.3, idx3+0.3, idx3-0.3],
            y=[-0.3, -0.3, 0.3, 0.3, -0.3, -0.3, 0.3, 0.3],
            z=[0, 0, 0, 0, row3.pos, row3.pos, row3.pos, row3.pos],
            i=[0, 0, 0, 4, 4, 4, 1, 1, 2, 2, 3, 3],
            j=[1, 2, 4, 5, 6, 7, 2, 5, 3, 6, 0, 7],
            k=[2, 3, 5, 6, 7, 4, 5, 6, 6, 7, 7, 4],
            color='seagreen', opacity=0.85, showscale=False,
            name=f"{row3.company_name} +",
            hovertext=f"{row3.company_name}: {row3.pos} positive"
        ))
        # Negative bar (red)
        fig_nlp3.add_trace(go.Mesh3d(
            x=[idx3-0.3, idx3+0.3, idx3+0.3, idx3-0.3, idx3-0.3, idx3+0.3, idx3+0.3, idx3-0.3],
            y=[0.7, 0.7, 1.3, 1.3, 0.7, 0.7, 1.3, 1.3],
            z=[0, 0, 0, 0, row3.neg, row3.neg, row3.neg, row3.neg],
            i=[0, 0, 0, 4, 4, 4, 1, 1, 2, 2, 3, 3],
            j=[1, 2, 4, 5, 6, 7, 2, 5, 3, 6, 0, 7],
            k=[2, 3, 5, 6, 7, 4, 5, 6, 6, 7, 7, 4],
            color='crimson', opacity=0.85, showscale=False,
            name=f"{row3.company_name} -",
            hovertext=f"{row3.company_name}: {row3.neg} negative"
        ))
    fig_nlp3.update_layout(
        title="3) 3D Bars – Positive (green) vs Negative (red) Words by Company",
        scene=dict(
            xaxis=dict(
                title='Company',
                tickmode='array',
                tickvals=list(range(len(agg))),
                ticktext=agg['company_name'].tolist()
            ),
            yaxis=dict(title='Polarity', tickvals=[0, 1], ticktext=['Positive', 'Negative']),
            zaxis_title='Word Count'
        ),
        showlegend=False,
        template='presentation',
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    chart_nlp3 = mo.ui.plotly(fig_nlp3)
    return chart_nlp1, chart_nlp2, chart_nlp3


@app.cell
def _(
    chart_nlp1,
    chart_nlp2,
    chart_nlp3,
    company_dropdown,
    fls_df,
    fls_source,
    mo,
):
    selected_company = company_dropdown.value
    company_data = fls_df[fls_df['company_name'] == selected_company]

    sentences_md = ""
    for _, row4 in company_data.iterrows():
        year = row4['year']
        sentences = row4['forward_looking_sentences']
        score = row4['sentiment_score']
        sentiment_label = "🟢 Positive" if score > 0 else ("🔴 Negative" if score < 0 else "⚪ Neutral")
        sentences_md += f"### {year} (Sentiment: {sentiment_label}, Score: {score})\n\n"
        sentences_md += f"{sentences}\n\n---\n\n"

    tab_nlp = mo.vstack([
        mo.md(
            """
            ## 💬 NLP & Sentiment Analysis

            This tab demonstrates skills from **Week 8–9** (LLMs & Prompt Engineering) using forward‑looking 
            statements extracted from UK corporate annual reports.
            """
        ),
        mo.callout(mo.md(fls_source), kind="info"),

        mo.md("### 🧭 Three 3D Views of the Sentiment Corpus"),
        mo.hstack([chart_nlp1, chart_nlp2], widths="equal", gap=1),
        chart_nlp3,

        mo.md("### 🔍 Explore by Company"),
        company_dropdown,
        mo.md(sentences_md) if sentences_md else mo.md("*No forward‑looking statements found for this company.*")
    ])
    return


app._unparsable_cell(
    """
    tab_week9 = mo.vstack([
        mo.md(\"## 🔌 Week 9: LLM APIs & AI‑as‑Judge\"),
        mo.callout(mo.md(\"Programmatic sentiment classification using Groq API (simulated output shown).\"), kind=\"warn\"),
        mo.md(\"**API Call Example (Python):**\"),
        mo.md(\"\"\"
        ```python
        from groq import Groq
        client = Groq(api_key=\"your-key-here\")
        response = client.chat.completions.create(
            model=\"llama-3.1-8b-instant\",
            messages=[{\"role\": \"user\", \"content\": \"Classify sentiment: ...\"}],
            temperature=0
        )
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
