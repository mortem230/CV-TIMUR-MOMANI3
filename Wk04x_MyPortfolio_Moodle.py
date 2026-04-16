# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.22.4",
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

    return go, px


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
def _(count, filtered_portfolio, mo, px):
    # 2D Scatter
    fig_2d = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Company',
        title=f"Cost of Debt vs. Z-Score ({count} observations)",
        labels={'Z_Score_lag': 'Altman Z-Score', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation',
        width=900,
        height=500
    )
    fig_2d.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(text="Distress (Z=1.81)", font=dict(color="red"),
                        x=1.5, xref="x", y=1.07, yref="paper", showarrow=False, yanchor="top"))
    fig_2d.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(text="Safe (Z=2.99)", font=dict(color="green"),
                        x=3.10, xref="x", y=1.02, yref="paper", showarrow=False, yanchor="top"))

    chart_2d = mo.ui.plotly(fig_2d)
    return (chart_2d,)


@app.cell
def _(filtered_portfolio, go, mo):
    # 3D Scatter
    fig_3d_scatter = go.Figure(data=[
        go.Scatter3d(
            x=filtered_portfolio['Z_Score_lag'],
            y=filtered_portfolio['Debt_Cost_Percent'],
            z=filtered_portfolio['Market_Cap_B'],
            mode='markers',
            marker=dict(
                size=8,
                color=filtered_portfolio['Market_Cap_B'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Market Cap (B)")
            ),
            text=filtered_portfolio['Company'],
            hovertemplate='<b>%{text}</b><br>Z-Score: %{x:.2f}<br>Debt Cost: %{y:.2f}%<br>Market Cap: %{z:.0f}B<extra></extra>'
        )
    ])
    fig_3d_scatter.update_layout(
        title="3D View: Z-Score vs Debt Cost vs Market Cap",
        scene=dict(
            xaxis_title='Altman Z-Score',
            yaxis_title='Debt Cost (%)',
            zaxis_title='Market Cap ($B)'
        ),
        template='presentation',
        height=500
    )
    chart_3d_scatter = mo.ui.plotly(fig_3d_scatter)
    return (chart_3d_scatter,)


@app.cell
def _(filtered_portfolio, go, mo):
    # Bar Chart
    sector_avg = filtered_portfolio.groupby('Sector_Key', as_index=False)['Debt_Cost_Percent'].mean()
    fig_3d_bar = go.Figure(data=[
        go.Bar(
            x=sector_avg['Sector_Key'],
            y=sector_avg['Debt_Cost_Percent'],
            marker=dict(color=sector_avg['Debt_Cost_Percent'], colorscale='Reds'),
            text=sector_avg['Debt_Cost_Percent'].round(2),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Avg Debt Cost: %{y:.2f}%<extra></extra>'
        )
    ])
    fig_3d_bar.update_layout(
        title="Average Cost of Debt by Sector",
        xaxis_title="Sector",
        yaxis_title="Debt Cost (%)",
        template='presentation',
        height=500
    )
    chart_3d_bar = mo.ui.plotly(fig_3d_bar)
    return (chart_3d_bar,)


@app.cell
def _(
    cap_slider,
    chart_2d,
    chart_3d_bar,
    chart_3d_scatter,
    mo,
    sector_dropdown,
):
    tab_data = mo.vstack([
        mo.md("## 📊 Interactive Credit Risk Analyzer"),
        mo.callout(
            mo.md("Use filters to explore borrowing costs vs. credit risk."),
            kind="info"
        ),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        mo.md("### 2D Scatter Plot"),
        chart_2d,
        mo.md("### 3D Scatter Plot (Z‑Score, Debt Cost, Market Cap)"),
        chart_3d_scatter,
        mo.md("### Bar Chart – Average Debt Cost by Sector"),
        chart_3d_bar
    ])
    return (tab_data,)


@app.cell
def _(mo):
    tab_cv = mo.vstack([
        mo.md(
            """
            # Timur Momani
            ### BSc Accounting & Finance Student
            📍 London, UK | 📧 tmomani@bk.ru | 📞 077780399668  
            🇰🇿 Kazakhstan | 🎂 17 February 2006
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
    return (tab_cv,)


@app.cell
def _(mo):
    # Trading Simulator - UI Creation Only
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
    # Silver Trading Chart
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
    # Bitcoin Loss Journey Data (UI creation)
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
    # 3D Bitcoin Loss Chart (using slider value)
    highlight_trade = trade_slider.value
    fig_btc_3d = go.Figure()
    # Add line connecting portfolio values in 3D (Trade index, Time, Value)
    fig_btc_3d.add_trace(go.Scatter3d(
        x=btc_trades['Trade'],
        y=[1,2,3,4,5],  # Dummy time dimension for 3D effect
        z=btc_trades['Portfolio Value ($)'],
        mode='lines+markers',
        line=dict(color='red', width=5),
        marker=dict(size=8, color=btc_trades['Portfolio Value ($)'], colorscale='RdBu', showscale=True),
        name='Portfolio Value',
        hovertemplate='Trade %{x}<br>Value: $%{z:,.0f}<extra></extra>'
    ))
    # Highlight selected trade with a larger marker
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
            yaxis=dict(visible=False)  # Hide dummy axis
        ),
        template='presentation',
        height=500
    )
    btc_chart_3d = mo.ui.plotly(fig_btc_3d)

    # Build Passion Projects tab
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
    return (tab_passion,)


@app.cell
def _(mo, pd):
    # Expanded Travel Data
    travel_data = pd.DataFrame([
        # Original
        {'City': 'Almaty', 'Country': 'Kazakhstan', 'Lat': 43.222, 'Lon': 76.851, 'Year': 2006, 'Status': 'Home'},
        {'City': 'Kuala Lumpur', 'Country': 'Malaysia', 'Lat': 3.139, 'Lon': 101.686, 'Year': 2015, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2019, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2020, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2021, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2022, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2023, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2024, 'Status': 'Lived'},
        {'City': 'Istanbul', 'Country': 'Turkey', 'Lat': 41.008, 'Lon': 28.978, 'Year': 2025, 'Status': 'Lived'},
        {'City': 'Dubai', 'Country': 'UAE', 'Lat': 25.204, 'Lon': 55.270, 'Year': 2024, 'Status': 'Visited'},
        {'City': 'Los Angeles', 'Country': 'USA', 'Lat': 34.052, 'Lon': -118.243, 'Year': 2017, 'Status': 'Visited'},
        {'City': 'Los Angeles', 'Country': 'USA', 'Lat': 34.052, 'Lon': -118.243, 'Year': 2018, 'Status': 'Visited'},
        {'City': 'London', 'Country': 'United Kingdom', 'Lat': 51.507, 'Lon': -0.128, 'Year': 2025, 'Status': 'Current'},
        # New additions
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
    ])

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
    return (tab_hobbies,)


@app.cell
def _(mo):
    name_input = mo.ui.text(label="Your Name")
    email_input = mo.ui.text(label="Your Email")
    message_input = mo.ui.text_area(label="Message")
    submit_btn = mo.ui.button(label="Send Message")

    tab_contact_form = mo.vstack([
        mo.md("## 📬 Contact Me"),
        name_input,
        email_input,
        message_input,
        submit_btn
    ])
    return name_input, submit_btn, tab_contact_form


@app.cell
def _(mo, name_input, submit_btn):
    if submit_btn.value:
        contact_response = mo.callout(
            mo.md(f"✅ Thanks {name_input.value or 'visitor'}! (Simulated)"),
            kind="success"
        )
    else:
        contact_response = mo.md("")
    return (contact_response,)


@app.cell
def _(
    contact_response,
    mo,
    tab_contact_form,
    tab_cv,
    tab_data,
    tab_hobbies,
    tab_passion,
):
    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Data Demo": tab_data,
        "🏆 Passion Projects": tab_passion,
        "✈️ Hobbies": tab_hobbies,
        "📬 Contact": mo.vstack([tab_contact_form, contact_response])
    })

    mo.md(
        f"""
        # **Timur Momani** – Personal Portfolio
        ---
        {app_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
