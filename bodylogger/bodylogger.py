#!/usr/bin/env python3

### Body Logger

import click # need colorama for colors
import sqlite3
import datetime
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pathlib import Path

from statsmodels.tsa.arima_model import ARIMA # need version higher than 0.8.0 to remove future warning

_ROOT = str(Path.home()) + '/.bodylogger'

now = datetime.datetime.now()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# Init App Entry
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.4.1')
def bodylogger():
    """
    Maintains a user database of personal measurements while giving
    stats and predictions based on trends.
    """
    pass

# Add
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date', default=now.strftime("%Y-%m-%d"), help="Specify date to add record (Default: Today)")
@click.option('-w', '--weight', type=float, prompt="Enter in weight", help='Weight to log')
def add(user, date, weight):
    """
    Adds a record for a specific date
    """

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Create table if doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS records (date text, weight float)")

    # Check for Date
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

# Deleterecord
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date', prompt="What day would you like to delete (YYYY-mm-dd)", help="Specify date to delete record")
def delete(user, date):
    """
    Deletes a record for a specific date
    """

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    date_sql = (date,)
    c.execute("SELECT date FROM records WHERE date=?", date_sql)
    date_exists = c.fetchone()
    if date_exists is not None:
        c.execute("DELETE FROM records WHERE date = '" + str(date) + "'")
        click.echo("[" + click.style('DELETED', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date))
    else:
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Record with that date does not exist")

    conn.commit()
    conn.close()

@bodylogger.command()
@click.argument('user')
def deleteuser(user):
    """
    Deletes a user database
    """

    user_db = _ROOT + "/users/" + str(user) + '.db'

    if os.path.isfile(user_db):
        os.remove(user_db)
        click.echo("[" + click.style('DELETED USER', fg='green', bold=True) + "] - user: " + str(user))
    else:
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User does not exist")


# list
@bodylogger.command()
@click.argument('user')
@click.option('-n', default=7, help="Number of past records to show (Default: 7)")
def list(user, n):
    """
    Lists records
    """
    print(_ROOT + '/users/' + str(user) + '.db')
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    click.echo("[" + click.style("DISPLAYING LAST " + str(n) + " RECORDS", fg='green') + "]")

    n = (n,)
    for row in c.execute('SELECT * FROM records ORDER BY date DESC LIMIT ?', n):
        click.echo(str(row[0]) + ": " + str(row[1]))

    conn.commit()
    conn.close()

# Stats
@bodylogger.command()
@click.argument('user')
def stats(user):
    """
    Gives user stats and predictions
    """

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    click.echo("[" + click.style("BODY STATISTICS FOR USER - " + str(user), fg='green') + "]")

    # Current Weight and Total Weight lost
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date'):
        records.append(row)

    click.echo("\nCurrent Weight: " + str(records[-1][1]) + " ( " + str(records[-1][0]) + " )")

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
    stddev = np.std(weights)[0]
    sem = stddev / np.sqrt(len(weights))

    ema_90 = np.round(records_df.ewm(span=90).mean().iloc[-1].values[0], 1)
    ema_30 = np.round(records_df.ewm(span=30).mean().iloc[-1].values[0], 1)
    ema_7 = np.round(records_df.ewm(span=7).mean().iloc[-1].values[0], 1)

    model = ARIMA(records_df, order=(1,0,0))
    model_fit = model.fit(disp=0)

    ARIMA_30 = model_fit.forecast(30)
    predict_ARIMA_30 = np.round(ARIMA_30[0][-1], 1)
    conf_ARIMA_30 = np.round(ARIMA_30[2][-1], 1)

    ARIMA_7 = model_fit.forecast(7)
    predict_ARIMA_7 = np.round(ARIMA_7[0][-1], 1)
    conf_ARIMA_7 = np.round(ARIMA_7[2][-1], 1)

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

    # Standard Deviation and Standard Error
    click.echo("\n1 Sigma: " + str(np.round(stddev,1)) + " (68%)")
    click.echo("2 Sigma: " + str(np.round(stddev*2,1)) + " (95%)")
    click.echo("3 Sigma: " + str(np.round(stddev*3,1)) + " (99.7%)")
    click.echo("SEM: " + str(np.round(sem, 1)))

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

# Plot
@bodylogger.command()
@click.argument('user')
@click.option('-o', '--output', default=False, help="Specify output filename")
def plot(user, output):
    """
    Plots records
    """

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Current Weight and Total Weight lost
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date'):
        records.append(row)

    # DataFrames for Calculations
    records_df = pd.DataFrame(records, columns=['date','weight'])
    #records_df['date'] = pd.to_datetime(records_df['date'])
    records_df['weight'] = records_df['weight'].apply(pd.to_numeric)
    records_df = records_df.set_index('date')

    # EMA
    ema_90_plot = records_df.ewm(span=90).mean()
    ema_30_plot = records_df.ewm(span=30).mean()
    ema_7_plot = records_df.ewm(span=7).mean()

    # ARIMA
    model = ARIMA(records_df, order=(1,0,0))
    model_fit = model.fit(disp=0)
    ARIMA_30 = model_fit.forecast(30)
    ARIMA_7 = model_fit.forecast(7)

    # ARIMA 30
    start = pd.to_datetime(records[-1][0])
    step = datetime.timedelta(days=1)
    start += step # Start tomorrow

    result30 = []
    count = 0
    while count < len(ARIMA_30[0]):
        result30.append(start.strftime('%Y-%m-%d'))
        start += step
        count += 1

    # ARIMA 7
    start = pd.to_datetime(records[-1][0])
    step = datetime.timedelta(days=1)
    start += step # Start tomorrow

    result7 = []
    count = 0
    while count < len(ARIMA_7[0]):
        result7.append(start.strftime('%Y-%m-%d'))
        start += step
        count += 1
        
    # Plots
    fig, ax = plt.subplots()
    ax.plot(records_df, "b-", label='Weight')
    ax.plot(ema_90_plot, "r-", label='EMA 90')
    ax.plot(ema_30_plot, "y-", label='EMA 30')
    ax.plot(ema_7_plot, "g-", label='EMA 7')
    ax.plot(result30, ARIMA_30[0], 'r--', label="ARIMA 30 Day Forecast")
    ax.plot(result7, ARIMA_7[0], 'g--', label='ARIMA 7 Day Forecast')

    ax.set(xlabel='Date', ylabel='Weight',
           title='Weight over Time - ' + str(user) + " (Generated: " + str(records[-1][0]) + ")")
    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper right')

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
            label.set_linewidth(1.5)  # the legend line width

    # Only show every nth label
    n = 7
    [l.set_visible(False) for (i,l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]

    # Rotate label 90 degree and turn on grid
    plt.xticks(rotation=90, size='x-small')
    plt.grid()
    
    if output:
        fig.set_size_inches(12,10)
        fig.savefig(output)
    else:
        plt.show()




# Main
if __name__ == '__main__':
    bodylogger()
