#!/usr/bin/env python3

import click # need colorama for colors
import sqlite3
import datetime
import numpy as np
import pandas as pd

from statsmodels.tsa.arima_model import ARIMA

now = datetime.datetime.now()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def bodylogger():
    pass

@bodylogger.command()
@click.argument('user')
@click.option('--date', default=now.strftime("%Y-%m-%d"))
@click.option('--weight', type=float, help='weight to log')
def add(user, date, weight):
    conn = sqlite3.connect('users/' + str(user) + '.db')
    c = conn.cursor()

    # Create table if doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS records (date text, weight float)")

    date_sql = (date,)
    c.execute("SELECT date FROM records WHERE date=?", date_sql)
    date_exists = c.fetchone()
    if date_exists is not None: # Update
        c.execute("UPDATE records SET weight=" + str(weight) + " WHERE date = '" + str(date) + "'")
        click.echo("[" + click.style('Updated', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", weight: " + str(weight))
    else: # Add
        c.execute("INSERT INTO records VALUES ('" + str(date) + "', "+ str(weight) + ")")
        click.echo("[" + click.style('Added', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", weight: " + str(weight))

    conn.commit()
    conn.close()



@bodylogger.command()
@click.argument('user')
def stats(user):
    conn = sqlite3.connect('users/' + str(user) + '.db')
    c = conn.cursor()

    # Total Weight lost
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date'):
        records.append(row)

    total_weight_lost = round(records[-1][1] - records[0][1], 1)
    if total_weight_lost < 0:
        click.echo('Total Weight Lost: ' + click.style(str(total_weight_lost), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )\n")
    else:
        click.echo('Total Weight Lost: ' + click.style(str(total_weight_lost), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )\n")

    # DataFrames for Calculations
    records_df = pd.DataFrame(records, columns=['date','weight'])
    records_df['date'] = pd.to_datetime(records_df['date'])
    records_df['weight'] = records_df['weight'].apply(pd.to_numeric)
    records_df = records_df.set_index('date')
    weights = pd.DataFrame([row[1] for row in records])

    # Calculatations
    ema_90 = weights.ewm(span=90).mean().iloc[-1].values[0]
    ema_30 = weights.ewm(span=30).mean().iloc[-1].values[0]
    ema_7 = weights.ewm(span=7).mean().iloc[-1].values[0]

    model = ARIMA(records_df, order=(1,0,0))
    model_fit = model.fit(disp=0)

    ARIMA_30 = model_fit.forecast(30)
    predict_ARIMA_30 = ARIMA_30[0][-1]
    conf_ARIMA_30 = ARIMA_30[2][-1]

    ARIMA_7 = model_fit.forecast(7)
    predict_ARIMA_7 = ARIMA_7[0][-1]
    conf_ARIMA_7 = ARIMA_7[2][-1]

    # Weight Lost in Past 90 Days
    records = []
    for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-90 days') AND datetime('now', 'localtime') ORDER BY date;"):
        records.append(row)

    weight_lost_90 = round(records[-1][1] - records[0][1], 1)
    if len(records) == 1:
        click.echo('Weight +/- in Past 90 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 90 DAYS **", fg='yellow'))
    elif len(records) == 0:
        click.echo('Weight +/- in Past 90 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 90 DAYS **", fg='yellow'))
    else:
        if weight_lost_90 < 0:
            click.echo('Weight +/- in Past 90 Days: ' + click.style(str(weight_lost_90), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
        else:
            click.echo('Weight +/- in Past 90 Days: ' + click.style(str(weight_lost_90), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")

    # Weight Lost in Past 30 Days
    records = []
    for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-30 days') AND datetime('now', 'localtime') ORDER BY date;"):
        records.append(row)

    weight_lost_30 = round(records[-1][1] - records[0][1], 1)
    if len(records) == 1:
        click.echo('Weight +/- in Past 30 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 30 DAYS **", fg='yellow'))
    elif len(records) == 0:
        click.echo('Weight +/- in Past 30 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 30 DAYS **", fg='yellow'))
    else:
        if weight_lost_30 < 0:
            click.echo('Weight +/- in Past 30 Days: ' + click.style(str(weight_lost_30), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
        else:
            click.echo('Weight +/- in Past 30 Days: ' + click.style(str(weight_lost_30), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")

    # Weight Lost in Past 7 Days
    records = []
    for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-7 days') AND datetime('now', 'localtime') ORDER BY date;"):
        records.append(row)

    weight_lost_7 = round(records[-1][1] - records[0][1], 1)
    if len(records) == 1:
        click.echo('Weight +/- in Past  7 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 7 DAYS **", fg='yellow'))
    elif len(records) == 0:
        click.echo('Weight +/- in Past  7 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 7 DAYS **", fg='yellow'))
    else:
        if weight_lost_7 < 0:
            click.echo('Weight +/- in Past  7 Days: ' + click.style(str(weight_lost_7), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
        else:
            click.echo('Weight +/- in Past  7 Days: ' + click.style(str(weight_lost_7), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")

    # EMA
    click.echo('\nEMA 90: ' + str(ema_90))
    click.echo('EMA 30: ' + str(ema_30))
    click.echo('EMA  7: ' + str(ema_7))

    if ema_30 < ema_7:
        click.secho("** WARNING 7 DAY EMA IS HIGHER THAN 30 DAY -- INDICATES AN UPWARD WEIGHT TREND", fg='red')
    if ema_90 < ema_30:
        click.secho("** WARNING 30 DAY EMA IS HIGHER THAN 90 DAY -- INDICATES AN PROLONGED UPWARD WEIGHT TREND", fg='red')

    # ARIMA
    click.echo("\nARIMA 30 Day Forecast: " + click.style(str(conf_ARIMA_30[0]) + " (Lower 95% Conf. Bound)", fg='red') + " <- " + str(predict_ARIMA_30) + " -> " + click.style(str(conf_ARIMA_30[1]) + " (Upper 95% Conf. Bound)", fg='red'))
    click.echo("ARIMA 7 Day Forecast: " + click.style(str(conf_ARIMA_7[0]) + " (Lower 95% Conf. Bound)", fg='red') + " <- " + str(predict_ARIMA_7) + " -> " + click.style(str(conf_ARIMA_7[1]) + " (Upper 95% Conf. Bound)", fg='red'))

    conn.close()

if __name__ == '__main__':
    bodylogger()
