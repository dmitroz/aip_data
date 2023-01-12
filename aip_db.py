import streamlit
import pandas
import snowflake.connector
from urllib.error import URLError

connect = snowflake.connector.connect(
    user='DMITRYT', password='789321QWEqaz',
    account='xxb05879.us-east-1',
    database='AIP_TEST',
    schema='AIP',
    warehouse='AIP_WAREHOUSE_TEST',
    role='ACCOUNTADMIN',
    insecure_mode=True,
    #ocsp_fail_open=False,
    use_openssl_only=False)

cx = connect.cursor()
#cx.execute('SELECT * FROM FUNDINGAMOUNTS')

#row_data = pandas.DataFrame(cx.fetchall())
#streamlit.text('Funding Amounts:')

#row_data = row_data.set_index(0)
#lineids_selected = streamlit.multiselect('Pick lineid(s):', list(row_data.index))
#lineids_to_show = row_data.loc[lineids_selected]

# Display the table on the page.
#streamlit.dataframe(lineids_to_show)


# def create_table():
#	c.execute('CREATE TABLE IF NOT EXISTS FUNDINGAMOUNTS(KEY NUMBER,
#														 FUNDINGLINEID VARCHAR,
#														 FISCALYEAR NUMBER,
#														 STEP VARCHAR)
#														 AMOUNT NUMBER,
#														 NOTES VARCHAR')

def insert_record(key, funding_line_id, fiscal_year, step, amount, notes):
    cx.execute("INSERT INTO FUNDINGAMOUNTS(KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2) VALUES ({}, '{}','{}','{}',{},'{}')".format(
        key, funding_line_id, fiscal_year, step, amount, notes))
    connect.commit()


def view_data():
    cx.execute('SELECT * FROM FUNDINGAMOUNTS WHERE FUNDINGLINEID = \'DOE-OS\' AND FISCALYEAR = 2022')
    data = cx.fetchall()
    return data


def view_all_ids():
    cx.execute('SELECT DISTINCT KEY FROM FUNDINGAMOUNTS')
    data = cx.fetchall()
    return data

def get_record(key):
    cx.execute('SELECT KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2 FROM FUNDINGAMOUNTS WHERE KEY ={}'.format(key))
    #FUNDINGLINEID ="{}" AND STEP ="{}" AND FISCALYEAR ="{}"'.format(funding_line_id, step, fiscal_year))

    data = cx.fetchall()
    return data


def update_record(new_amount, new_notes, funding_line_id, step, fiscal_year):
    cx.execute("UPDATE FUNDINGAMOUNTS SET AMOUNT ={}, NOTES='{}' WHERE FUNDINGLINEID='{}' and STEP='{}' and FISCALYEAR='{}'",
               (new_amount, new_notes, funding_line_id, step, fiscal_year))
    connect.commit()
    data = cx.fetchall()
    return data


def delete_record(key):
    cx.execute('DELETE FROM FUNDINGAMOUNTS WHERE KEY ={}'.format(key))
    connect.commit()
