#!/usr/bin/env python3
"""
Main Module for Bodylogger

Maintains a database of body weight measurements while giving stats and predictions based on trends.
"""

import click  # need colorama for colors
import sqlite3
import datetime
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pathlib import Path
from os import listdir
from os.path import isfile, join

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    # need version higher than 0.8.0 to remove future warning
    # 0.8.0 is highest in pip as of 11-24-2017
    from statsmodels.tsa.arima_model import ARIMA

_ROOT = str(Path.home()) + '/.bodylogger'

NOW = datetime.datetime.now()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# =============================================================================
# Utility Functions
# =============================================================================

def is_user(user):
    """
    Checks to see is a user is a created user database
    """
   
    files = [f for f in listdir(_ROOT + '/users/') if isfile(join(_ROOT + '/users/', f))]
    users = [s.split('.')[0] for s in files]

    if not users:  # List is empty
        return False

    if user in users:
        return True
    else:
        return False

def check_date(date_string):
    """
    Checks to see if date is in YYYY-MM-DD format
    """

    try:
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        date = str(date.year) + '-' + str(date.month) + '-' + str(date.day)
    except ValueError:
        return False

    return date

def get_sec(time_str):
    '''
    Converts duration string (HH:MM:SS) to total seconds
    '''
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def sec_to_str(sec):
    '''
    Converts total seconds to duration string (HH:MM:SS)
    '''

    hours = int(sec // 3600)
    minutes = int((sec // 60) - (hours * 60))
    seconds = int(sec - (minutes * 60) - (hours * 3600))
   
    # force numbers to include leading zeros
    hours = "%02d" % (hours,)
    minutes = "%02d" % (minutes,)
    seconds = "%02d" % (seconds,)

    return str(hours) + ":" + str(minutes) + ":" + str(seconds)

# Init App Entry
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.7.1')
def bodylogger():
    """
    Maintains a user database of personal measurements while giving
    stats and predictions based on trends.
    """
    pass

# =============================================================================
# Record Commands
# =============================================================================
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date',
              default=NOW.strftime("%Y-%m-%d"),
              help="Specify date to add record (Default: Today)")
@click.option('-w', '--weight',
              type=float,
              prompt="Enter in weight",
              help='Weight to log')
def add(user, date, weight):
    """
    Adds a record for a specific date
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1

    # Check for proper date format
    if not check_date(date):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Date " + str(date) + " is in an incorrect format. Please use YYYY-MM-DD")
        return 1
  
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Check for date in db
    date_sql = (date,)
    c.execute("SELECT date FROM records WHERE date=?", date_sql)
    date_exists = c.fetchone()

    if date_exists is not None:  # SQL UPDATE
        c.execute("UPDATE records SET weight=" + str(weight) + " WHERE date = '" + str(date) + "'")
        click.echo("[" + click.style('Updated', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", weight: " + str(weight))
    else: # SQL ADD
        c.execute("INSERT INTO records VALUES ('" + str(date) + "', "+ str(weight) + ")")
        click.echo("[" + click.style('Added', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", weight: " + str(weight))

    conn.commit()
    conn.close()

# Deleterecord
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date',
              prompt="What day would you like to delete (YYYY-mm-dd)",
              help="Specify date to delete record")
def delete(user, date):
    """
    Deletes a record for a specific date
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1

    # Check for proper date format
    if not check_date(date):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Date " + str(date) + " is in an incorrect format. Please use YYYY-MM-DD")
        return 1
    
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

# =============================================================================
# Run Commands
# =============================================================================
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date',
              default=NOW.strftime("%Y-%m-%d"),
              help="Specify date to add record (Default: Today)")
@click.option('-di', '--distance',
              type=float,
              prompt="Enter in distance (mi)",
              help='Distance ran')
@click.option('-t', '--time',
              type=str,
              prompt="Enter in time (HH:MM:SS)",
              help='Duration of run')
def addrun(user, date, distance, time):
    """
    Adds a run for a specific date
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1

    # Check for proper date format
    if not check_date(date):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Date " + str(date) + " is in an incorrect format. Please use YYYY-MM-DD")
        return 1
  
    # convert duration to seconds
    time = get_sec(time)

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Check for date in db
    date_sql = (date,)
    c.execute("SELECT date FROM runs WHERE date=?", date_sql)
    date_exists = c.fetchone()

    if date_exists is not None:  # SQL UPDATE
        c.execute("UPDATE runs SET distance=" + str(distance) + ", time=" + str(time) + " WHERE date = '" + str(date) + "'")
        click.echo("[" + click.style('Updated', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", distance: " + str(distance) + ", time: " + sec_to_str(time))
    else: # SQL ADD
        c.execute("INSERT INTO runs VALUES ('" + str(date) + "', "+ str(distance) + ", "+ str(time) + ")")
        click.echo("[" + click.style('Added', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date) + ", distance: " + str(distance) + ", time: " + sec_to_str(time))

    conn.commit()
    conn.close()

# Deleterun
@bodylogger.command()
@click.argument('user')
@click.option('-d', '--date',
              prompt="What day would you like to delete (YYYY-mm-dd)",
              help="Specify date to delete run")
def deleterun(user, date):
    """
    Deletes a run for a specific date
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1

    # Check for proper date format
    if not check_date(date):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Date " + str(date) + " is in an incorrect format. Please use YYYY-MM-DD")
        return 1
    
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    date_sql = (date,)
    c.execute("SELECT date FROM runs WHERE date=?", date_sql)
    date_exists = c.fetchone()
    if date_exists is not None:
        c.execute("DELETE FROM runs WHERE date = '" + str(date) + "'")
        click.echo("[" + click.style('DELETED', fg='green', bold=True) + "] - user: " + str(user) + ", date: " + str(date))
    else:
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - Run with that date does not exist")

    conn.commit()
    conn.close()

# list
@bodylogger.command()
@click.argument('user')
@click.option('-n',
              default=7,
              help="Number of past records to show (Default: 7)")
def list(user, n):
    """
    Lists records
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1
   
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    n_wrap = (n,) # wrap to prevent SQL injection

    # Weight
    click.echo("[" + click.style("DISPLAYING LAST " + str(n) + " RECORDS", fg='green') + "]")
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date DESC LIMIT ?', n_wrap):
        records.append(row)

    if not records:  # is_empty check
        click.echo("\n[" + click.style('NOTICE', fg='yellow', bold=True) + "] - No weights recorded.")
    else:
        for r in records:
            click.echo(str(r[0]) + ": " + str(r[1]))

    # Run
    click.echo("\n[" + click.style("DISPLAYING LAST " + str(n) + " RUNS", fg='green') + "]")
    runs = []
    for row in c.execute('SELECT * FROM runs ORDER BY date DESC LIMIT ?', n_wrap):
        runs.append(row)
        
    if not runs:  #is_empty check
        click.echo("\n[" + click.style('NOTICE', fg='yellow', bold=True) + "] - No runs recorded.")
    else:
        for r in runs:
            click.echo(str(r[0]) + ": " + str(r[1]) + ", " + sec_to_str(r[2]))


    conn.commit()
    conn.close()


@bodylogger.command()
@click.argument('user')
def stats(user):
    """
    Gives user stats and predictions
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1
   
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    click.echo("[" + click.style("BODY STATISTICS FOR USER - " + str(user), fg='green') + "]")

    # Current Weight and Total Weight lost
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date'):
        records.append(row)

    if len(records) != 0:
        click.echo("\nCurrent Weight: " + str(records[-1][1]) + " ( " + str(records[-1][0]) + " )")

        total_weight_lost = round(records[-1][1] - records[0][1], 1)
        if total_weight_lost < 0:
            click.echo('Total Weight +/-: ' + click.style(str(total_weight_lost), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )\n")
        else:
            click.echo('Total Weight +/-: ' + click.style(str(total_weight_lost), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )\n")

        # DataFrames for Calculations
        records_df = pd.DataFrame(records, columns=['date', 'weight'])
        records_df['date'] = pd.to_datetime(records_df['date'])
        records_df['weight'] = records_df['weight'].apply(pd.to_numeric)
        records_df = records_df.set_index('date')
        weights = pd.DataFrame([row[1] for row in records])

        # Weight Lost in Past 90 Days
        records = []
        for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-90 days') AND datetime('now', 'localtime') ORDER BY date;"):
            records.append(row)

        if len(records) == 1:
            click.echo('Weight +/- in Past 90 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 90 DAYS **", fg='yellow'))
        elif not records:
            click.echo('Weight +/- in Past 90 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 90 DAYS **", fg='yellow'))
        else:
            weight_lost_90 = round(records[-1][1] - records[0][1], 1)
            if weight_lost_90 < 0:
                click.echo('Weight +/- in Past 90 Days: ' + click.style(str(weight_lost_90), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
            else:
                click.echo('Weight +/- in Past 90 Days: ' + click.style(str(weight_lost_90), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")

        # Weight Lost in Past 30 Days
        records = []
        for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-30 days') AND datetime('now', 'localtime') ORDER BY date;"):
            records.append(row)

        if len(records) == 1:
            click.echo('Weight +/- in Past 30 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 30 DAYS **", fg='yellow'))
        elif not records:
            click.echo('Weight +/- in Past 30 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 30 DAYS **", fg='yellow'))
        else:
            weight_lost_30 = round(records[-1][1] - records[0][1], 1)
            if weight_lost_30 < 0:
                click.echo('Weight +/- in Past 30 Days: ' + click.style(str(weight_lost_30), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
            else:
                click.echo('Weight +/- in Past 30 Days: ' + click.style(str(weight_lost_30), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")


        # Weight Lost in Past 7 Days
        records = []
        for row in c.execute("SELECT * FROM records WHERE date BETWEEN datetime('now', '-7 days') AND datetime('now', 'localtime') ORDER BY date;"):
            records.append(row)

        if len(records) == 1:
            click.echo('Weight +/- in Past  7 Days: ' + click.style("0.0", fg='yellow') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " ) " + click.style("** ONLY 1 RECORD IN PAST 7 DAYS **", fg='yellow'))
        elif not records:
            click.echo('Weight +/- in Past  7 Days: ' + click.style("0.0", fg='yellow') + click.style(" ** NO RECORDS IN PAST 7 DAYS **", fg='yellow'))
        else:
            weight_lost_7 = round(records[-1][1] - records[0][1], 1)
            if weight_lost_7 < 0:
                click.echo('Weight +/- in Past  7 Days: ' + click.style(str(weight_lost_7), fg='green') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")
            else:
                click.echo('Weight +/- in Past  7 Days: ' + click.style(str(weight_lost_7), fg='red') + " ( " + str(records[0][0]) + " -> " + str(records[-1][0]) + " )")

        # Standard Deviation and Standard Error
        if len(records_df) > 1: # Can't calculate much on 1 record
            stddev = np.std(weights)[0]
            sem = stddev / np.sqrt(len(weights))

            click.echo("\n1 Sigma: " + str(np.round(stddev, 1)) + " (68%)")
            click.echo("2 Sigma: " + str(np.round(stddev*2, 1)) + " (95%)")
            click.echo("3 Sigma: " + str(np.round(stddev*3, 1)) + " (99.7%)")
            click.echo("SEM: " + str(np.round(sem, 1)))

            # EMA
            ema_90 = np.round(records_df.ewm(span=90).mean().iloc[-1].values[0], 1)
            ema_30 = np.round(records_df.ewm(span=30).mean().iloc[-1].values[0], 1)
            ema_7 = np.round(records_df.ewm(span=7).mean().iloc[-1].values[0], 1)
        
            click.echo('\nEMA 90: ' + str(ema_90))
            click.echo('EMA 30: ' + str(ema_30))
            click.echo('EMA  7: ' + str(ema_7))

            if ema_30 < ema_7:
                click.echo("[" + click.style('WARNING', fg='yellow', bold=True) + "] - 7 Day EMA is higher than 30 day -- Indicates an upward trend.")
            if ema_90 < ema_30:
                click.echo("[" + click.style('WARNING', fg='yellow', bold=True) + "] - 30 Day EMA is higher than 90 day -- Indicates a prolonged upward trend.")
        else:
            click.echo("\n[" + click.style('NOTICE', fg='yellow', bold=True) + "] - Need more than 1 data point to run calculations.")
    else:
        click.echo("\n[" + click.style('NOTICE', fg='yellow', bold=True) + "] - No weights recorded.")


    # Runs
    click.echo("\n[" + click.style("RUN STATISTICS FOR USER - " + str(user), fg='green') + "]")

    runs = []
    for row in c.execute('SELECT * FROM runs ORDER BY date DESC'):
        runs.append(row)

    total_runs = len(runs)

    if total_runs != 0:
        total_miles = 0
        total_time = 0
        for r in runs:
            total_miles += r[1]
            total_time += r[2]

        # Total Stats
        click.echo('Total Miles Ran: ' + str(total_miles))
        click.echo('Total Time Ran: ' + sec_to_str(total_time))

        # Avg Stats
        click.echo('\nAvg. Miles Per Run: ' + str(total_miles / total_runs))
        click.echo('Avg. Time Per Run: ' + sec_to_str(total_time / total_runs))
        click.echo('Avg. Pace per Mile: ' + sec_to_str(total_time / total_miles))
    else:
        click.echo("\n[" + click.style('NOTICE', fg='yellow', bold=True) + "] - No runs recorded.")

    conn.close()


@bodylogger.command()
@click.argument('user')
@click.option('-o', '--output',
              default=False,
              help="Specify output filename")
def plot(user, output):
    """
    Plots records
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1
    
    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Current Weight and Total Weight lost
    records = []
    for row in c.execute('SELECT * FROM records ORDER BY date'):
        records.append(row)

    # Check for weights for plot
    if len(records) == 0:
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " has no weights recorded. Please see 'add' to add weight records.")
        return 1

    # DataFrames for Calculations
    records_df = pd.DataFrame(records, columns=['date', 'weight'])
    #records_df['date'] = pd.to_datetime(records_df['date'])
    records_df['weight'] = records_df['weight'].apply(pd.to_numeric)
    records_df = records_df.set_index('date')

    # EMA
    ema_90_plot = records_df.ewm(span=90).mean()
    ema_30_plot = records_df.ewm(span=30).mean()
    ema_7_plot = records_df.ewm(span=7).mean()

    # Plots
    fig, ax = plt.subplots()
    ax.plot(records_df, "b-", label='Weight')
    ax.plot(ema_90_plot, "r-", label='EMA 90')
    ax.plot(ema_30_plot, "y-", label='EMA 30')
    ax.plot(ema_7_plot, "g-", label='EMA 7')

    ax.set(xlabel='Date', ylabel='Weight',
           title='Weight over Time - ' + str(user))
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
    [l.set_visible(False) for (i, l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]

    # Rotate label 90 degree and turn on grid
    plt.xticks(rotation=90, size='x-small')
    plt.grid()

    if output:
        fig.set_size_inches(12, 10)
        fig.savefig(output)
    else:
        plt.show()


# =============================================================================
# User Commands
# =============================================================================

@bodylogger.command()
@click.argument('user')
def createuser(user):
    """
    Creates a user database
    """

    # Check to see if it already exists
    if is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - " + str(user) + " is already a user.")
        return 1

    conn = sqlite3.connect(_ROOT + '/users/' + str(user) + '.db')
    c = conn.cursor()

    # Create table if doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS records (date text, weight float)")
    c.execute("CREATE TABLE IF NOT EXISTS runs (date text, distance float, time float)")

    conn.commit()
    click.echo("[" + click.style('CREATED USER', fg='green', bold=True) + "] - user: " + str(user))
           
    conn.close()
   

@bodylogger.command()
def listusers():
    """
    Lists user databases
    """

    files = [f for f in listdir(_ROOT + '/users/') if isfile(join(_ROOT + '/users/', f))]
    users = [s.split('.')[0] for s in files]

    click.echo("[" + click.style("USER LIST", fg='green') + "]")
    if not users:  # List is empty
        click.echo("No users found. See command 'createuser' to initialize.")
    else:
        for u in users:
            click.echo(u)


@bodylogger.command()
@click.argument('user')
def deleteuser(user):
    """
    Deletes a user database
    """

    # Check for user
    if not is_user(user):
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User " + str(user) + " not found. Please see 'listusers' for a user list, or 'createuser' to create one.")
        return 1

    user_db = _ROOT + "/users/" + str(user) + '.db'

    if os.path.isfile(user_db):
        os.remove(user_db)
        click.echo("[" + click.style('DELETED USER', fg='green', bold=True) + "] - user: " + str(user))
    else:
        click.echo("[" + click.style('ERROR', fg='red', bold=True) + "] - User does not exist")


# Main
if __name__ == '__main__':
    bodylogger()
