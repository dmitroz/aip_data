import streamlit as st
import pandas as pd

import aip

aip.build(page_title='Funding Amount list', page_icon='💵')
sf = aip.get_snowflake()

if sf.connected():

    df_amount = pd.DataFrame(sf.view_data_funding_amount(),
                             columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'FL_NOTE',
                                      'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'FA_NOTE']
                             )

    col1, col2 = st.columns(2)
    with col1:
        sf_org_ids = sf.view_all_org_ids()
        if sf_org_ids is not None:
            select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf.view_all_org_ids()])
        else:
            select_org = st.multiselect("Select ORG_ID:", [])
        select_name = st.multiselect("Select NAME:", set(df_amount['NAME']))
    with col2:
        select_year = st.multiselect("Select FISCAL_YEAR:", set(df_amount['FISCAL_YEAR']))
        select_step = st.multiselect("Select STEP:", set(df_amount['STEP']))

    df_selected = sf.view_data_funding_amount(df_org=select_org,
                                              df_name=select_name,
                                              df_year=select_year,
                                              df_step=select_step)
    df_selected = pd.DataFrame(df_selected,
                               columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'FL_NOTE',
                                        'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'FA_NOTE']
                               )
    st.dataframe(df_selected,
                 use_container_width=True)

    st.subheader('➕ Add new record')
    col1, col2 = st.columns(2)

    with col1:
        funding_line_id = st.selectbox('FUNDING_LINE_ID',
                                       set(df_selected['FUNDING_LINE_ID']))
        fiscal_year = st.selectbox('FISCAL_YEAR',
                                   ('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
                                    '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025',
                                    '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033',
                                    '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041',
                                    '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049',
                                    '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057',
                                    '2058', '2059', '2060', '2061', '2062', '2063', '2064', '2065',
                                    '2066', '2067', '2068', '2069', '2070', '2071', '2072', '2073',
                                    '2074', '2075', '2076', '2077', '2078', '2079', '2080', '2081',
                                    '2082', '2083', '2084', '2085', '2086', '2087', '2088', '2089',
                                    '2090', '2091', '2092', '2093', '2094', '2095', '2096', '2097',
                                    '2098', '2099'),
                                   index=13)
        step = st.selectbox('STEP', ('Request', 'House', 'Senate', 'Enacted', 'Authorized'))

    with col2:
        amount = st.number_input('AMOUNT')
        amount_type = st.text_input('AMOUNT_TYPE')
        source_url = st.text_input('SOURCE_URL')
        note = st.text_area('NOTE')

    if st.button('Submit'):
        df = sf.exist_funding_amount(funding_line_id, int(fiscal_year), step, amount_type)
        df = pd.DataFrame(df)

        if not df.empty:
            st.error("FUNDING AMOUNT is already exists: FUNDING_LINE_ID = '{}', FISCAL_YEAR = {}, STEP = '{}', "
                     "AMOUNT_TYPE = '{}' ".format(funding_line_id, int(fiscal_year), step, amount_type))
        else:
            sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount, amount_type,
                                     source_url, note)
            st.success("New record added to FUNDING AMOUNT: "
                       "FUNDING_LINE_ID = '{}', "
                       "FISCAL_YEAR = {}, "
                       "STEP = '{}', "
                       "AMOUNT_TYPE = '{}'".format(funding_line_id, fiscal_year, step, amount_type))
