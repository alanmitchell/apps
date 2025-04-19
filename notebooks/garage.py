# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "humanize==4.12.2",
#     "pandas==2.2.3",
#     "requests==2.32.3",
# ]
# ///

import marimo

__generated_with = "0.12.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    import urllib.parse
    import datetime as dt

    import marimo as mo
    import requests
    import pandas as pd
    import humanize
    return (
        ZoneInfo,
        datetime,
        dt,
        humanize,
        mo,
        pd,
        requests,
        timedelta,
        urllib,
    )


@app.cell
def _(mo):
    box_size = 150
    def create_box(box_color, box_text):
        return mo.Html(
            f"<div style='min-width: {box_size}px; min-height: {box_size}px; background-color: {box_color}; text-align: center;'><span style='font-size: 50px; color: white;'>{box_text}</span></div>"
        )

    refresh = mo.ui.refresh(default_interval=300)
    refresh
    return box_size, create_box, refresh


@app.cell
def _(mo):
    mo.md(r"""<span style='font-size: 50px;'>Garage Door:</span>""")
    return


@app.cell
def _(
    ZoneInfo,
    create_box,
    datetime,
    humanize,
    pd,
    refresh,
    requests,
    timedelta,
    urllib,
):
    print(refresh.value)
    # Define the Alaska time zone
    alaska_tz = ZoneInfo("America/Anchorage")

    # Get the current time in Alaska time
    now_alaska = datetime.now(alaska_tz).replace(tzinfo=None)

    # Subtract 24 hours from the current time
    start_ts = now_alaska - timedelta(hours=24)

    # Convert to an ISO formatted string
    start_ts_str = start_ts.strftime("%Y-%m-%d %H:%M:%S")
    # Create the query parameters dictionary
    params = {"start_ts": start_ts_str}

    # Encode the parameters into a query string
    query_string = urllib.parse.urlencode(params)

    url = f"https://bmon.analysisnorth.com/api/v1/readings/A84041D54182DC7B_door/?{query_string}"
    res = requests.get(url)
    readings = res.json()['data']['readings']
    df = pd.DataFrame(readings, columns=['ts', 'val'])
    df['ts'] = pd.to_datetime(df['ts'])
    if df.iloc[-1].val == 1.0:
        df['val_chg'] = df.val.diff()
        df_close = df.query('val_chg == 1.0')
        if len(df_close):
            ago = now_alaska - df_close.iloc[-1].ts
            ago_str = humanize.precisedelta(ago, minimum_unit='minutes', format='%.1f')
        else:
            ago_str = 'more than 1 day'
        bx = create_box('green', f'CLOSED {ago_str} ago')

    else:
        bx = create_box('red', 'OPEN')

    bx
    return (
        ago,
        ago_str,
        alaska_tz,
        bx,
        df,
        df_close,
        now_alaska,
        params,
        query_string,
        readings,
        res,
        start_ts,
        start_ts_str,
        url,
    )


if __name__ == "__main__":
    app.run()
