import streamlit as st
import pandas as pd
from aip_db import *
import streamlit.components.v1 as stc
from st_on_hover_tabs import on_hover_tabs
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime, timedelta

HTML_BANNER = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:16px;border-radius:10px\">\n"
               "        <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "        <h1 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">Snowflake Data Management"
               "        </h1>\n"
               "        <h2 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">version 1.0"
               "        </h2>\n"
               "    </div>\n"
               "    ")

# This should be on top of your script
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="localhost/",
    # prefix="",   # no prefix will show all your cookies for this domain
    # You should setup COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    # password=os.environ.get("COOKIES_PASSWORD", "My secret password"),
    password='streamlit'
)

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()


def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
    stc.html(HTML_BANNER, height=225)

    sf = Snowflake()
    userid = cookies.get('userid')
    password = cookies.get('password')
    role = cookies.get('role')
    value = cookies.get('expire_datetime')

    expire = datetime.now()

    if value is not None:
        expire = datetime.strptime(value, "%d-%b-%Y-%H:%M:%S")

    # st.info(expire)

    if expire < datetime.now():
        cookies['userid'] = ''
        cookies['password'] = ''
        cookies['role'] = ''
        userid = ''
        password = ''
        role = ''
        cookies.save()

    if userid is None:
        userid = ''

    if password is None:
        password = ''

    if userid != '' and password != '':
        try:
            sf.authorization(userid, password, role)
        except Exception as e:
            st.error(str(e))

    if sf.not_connected():
        st.subheader('🧑‍💻 Authorization')
        userid = st.text_input('Username').lower()
        password = st.text_input('Password', type="password")
        role = st.selectbox('Snowflake role',
                            ('PUBLIC', 'ACCOUNTADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN'),
                            index=1,
                            disabled=True)

        col1, col2 = st.columns(2)

        with col1:
            st.text_input('Snowflake account', 'lib13297.us - east - 1', disabled=True)
            st.text_input('Snowflake database', 'FYI_BUDGET_TRACKER', disabled=True)
        with col2:
            st.text_input('Snowflake schema', 'TEST', disabled=True)
            st.text_input('Snowflake warehouse', 'FYI_COMPUTE_WH', disabled=True)

        if st.button('Login'):
            if userid == '' or password == '':
                st.warning('Please provide account and password to login.')
            else:
                try:
                    sf.authorization(userid, password, role)
                    with open("config.yaml") as f:
                        config = yaml.load(f, Loader=yaml.FullLoader)

                    minutes = config['cookie']['expiry_minutes']
                    expire = datetime.now() + timedelta(minutes=minutes)

                    cookies['password'] = password
                    cookies['userid'] = userid
                    cookies['role'] = role
                    cookies['expire_datetime'] = expire.strftime("%d-%b-%Y-%H:%M:%S")
                    cookies.save()
                    st.experimental_rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        with st.sidebar:
            tabs = on_hover_tabs(
                tabName=['Organization', 'Funding Line', 'Edit Line', 'Funding Amount', 'Bulk download',
                         'Bulk upload', 'Logout',
                         'About'],
                iconName=['table', 'table', 'edit', 'table', 'download', 'upload',
                          'logout'],
                default_choice=0,
                styles={'navtab': {'background-color': '#111',
                                   'color': '#818181',
                                   'font-size': '16px',
                                   'transition': '.3s',
                                   'white-space': 'nowrap',
                                   'text-transform': 'uppercase'},
                        'tabOptionsStyle': {':hover :hover': {'color': 'white',
                                                              'cursor': 'pointer'}},
                        'iconStyle': {'position': 'fixed',
                                      'left': '7.5px',
                                      'text-align': 'left'},
                        'tabStyle': {'list-style-type': 'none',
                                     'margin-bottom': '30px',
                                     'padding-left': '30px'}},
                key="1")

        if tabs == 'Organization':
            st.subheader('🏢 Organization list')

            df = sf.view_data_organization()
            df = pd.DataFrame(df,
                              columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])

            # df = df.set_index('ORG_ID')
            df_selected = st.multiselect("Select ORG_ID:",
                                         [str(i[0]) for i in sf.view_all_org_ids()])  # set(df.index))
            df_selected = sf.view_data_organization(df_selected)  # df.loc[df_selected]

            # if not df_selected.empty:
            #     st.dataframe(df_selected, use_container_width=True)
            # else:
            df_selected = pd.DataFrame(df_selected,
                                       columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])
            st.dataframe(df_selected,
                         use_container_width=True)

            st.subheader('➕ Add new record')
            col1, col2 = st.columns(2)

            with col1:
                org = st.text_input('ORG')
                list_of_records = ['<NA>'] + [str(i[0]) for i in sf.view_all_org_ids()]
                parent = st.selectbox('PARENT', list_of_records, index=0)
                if parent == '<NA>':
                    org_id = st.text_input('ORG_ID', disabled=True, value=org.upper())
                else:
                    org_id = st.text_input('ORG_ID', disabled=True, value=parent + "-" + org.upper())

            with col2:
                if parent == '<NA>':
                    parent_level = [-1]
                else:
                    parent_level = sf.get_parent_level(parent)
                parent_level = pd.DataFrame(parent_level)
                level = st.text_input('LEVEL', int(parent_level[0].values + 1), disabled=True)
                name = st.text_input('NAME', 'Dummy name')

            if st.button('Submit'):
                df = sf.view_all_org_ids()
                df = pd.DataFrame(df)

                if org_id in set(df.values[:, 0]):
                    st.error("ORGANIZATION is already exists: ORG_ID = '{}' ".format(org_id))
                else:
                    sf.insert_organization(org.upper(), parent, org_id, int(level), name)
                    st.success("New record added to ORGANIZATION: ORG_ID = '{}'".format(org_id))
                    st.experimental_rerun()

        elif tabs == 'Funding Line':
            st.subheader('📁 Funding Line list')

            df = sf.view_data_funding_line()
            df = pd.DataFrame(df,
                              columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])

            col1, col2 = st.columns(2)
            with col1:
                df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
            with col2:
                df_name = st.multiselect("Select NAME:", set(df['NAME']))

            df_selected = sf.view_data_funding_line(df_org, df_name)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected,
                         use_container_width=True)

            st.subheader('➕ Add new record')
            col1, col2 = st.columns(2)

            with col1:
                last_row = sf.get_last_row_funding_line()
                last_row = pd.DataFrame(last_row)
                # st.info(last_row[0].values)
                st.text_input('ID', int(last_row[0].values + 1), disabled=True)
                list_of_records = [i[0] for i in sf.view_all_org_ids()]
                org_id = st.selectbox('ORG_ID', list_of_records)
                name = st.text_input('NAME', 'Dummy name')

            with col2:
                funding_type = st.text_input('FUNDING_TYPE', 'Dummy funding type')
                version = st.number_input('VERSION', 0)
                top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'))
                note = st.text_area('NOTE', 'Dummy note')

            if st.button('Submit'):
                df = sf.exists_funding_line(org_id, name, version)
                df = pd.DataFrame(df)

                if not df.empty:
                    st.error("FUNDING LINE is already exists: ORG_ID = '{}', NAME = '{}', VERSION = {} ".format(
                        org_id, name, version))
                else:
                    sf.insert_funding_line(int(last_row[0].values + 1), org_id, name, funding_type, version,
                                                  top_line, note)
                    st.success("New record added to FUNDING LINE: ORG_ID = '{}', NAME = '{}', VERSION = {}".format(
                        org_id, name, version))
                    st.experimental_rerun()

        elif tabs == 'Edit Line':
            st.subheader('📁 Edit Funding Line')

            df = sf.view_data_funding_line()
            df = pd.DataFrame(df,
                              columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])

            col1, col2 = st.columns(2)
            with col1:
                df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
            with col2:
                df_name = st.multiselect("Select NAME:", set(df['NAME']))

            df_selected = sf.view_data_funding_line(df_org, df_name)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected,
                         use_container_width=True)

            df_line_id = st.selectbox("Select ID:", set(df_selected['ID']))
            df_selected = sf.view_data_funding_line(None, None, df_line_id)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected, use_container_width=True)

            st.subheader('✏️ Edit record')
            col1, col2 = st.columns(2)

            with col1:
                id = st.text_input('ID', df_selected['ID'][0], disabled=True)
                list_of_records = [i[0] for i in sf.view_all_org_ids()]

                org_id = st.selectbox('ORG_ID', list_of_records, index=0)
                # org_id = df_selected['ORG_ID']
                name = st.text_input('NAME', df_selected['NAME'][0])

            with col2:
                funding_type = st.text_input('FUNDING_TYPE', df_selected['FUNDING_TYPE'][0])
                version = st.number_input('VERSION', df_selected['VERSION'][0])
                top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'), bool(df_selected['TOP_LINE'][0]))
                note = st.text_area('NOTE', df_selected['NOTE'][0])

            if st.button('Submit'):
                sf.update_funding_line(id, org_id, name, funding_type, version, top_line, note)
                st.success("Existing FUNDING LINE record was updated: "
                           "ID = {}, ORG_ID = '{}', NAME = '{}', FUNDING_TYPE = '{}', VERSION = {}, TOP_LINE = {}, "
                           "NOTE = '{}' ".format(
                    id, org_id, name, funding_type, version, top_line, note))
                st.experimental_rerun()

        elif tabs == 'Funding Amount':
            st.subheader('💵 Funding Amount list')

            df = sf.view_data_funding_amount()
            df = pd.DataFrame(df,
                              columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                       'SOURCE_URL',
                                       'NOTE', 'ORG_ID', 'NAME'])

            col1, col2 = st.columns(2)
            with col1:
                df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
                df_name = st.multiselect("Select NAME:", set(df['NAME']))
            with col2:
                df_year = st.multiselect("Select FISCAL_YEAR:", set(df['FISCAL_YEAR']))
                df_step = st.multiselect("Select STEP:", set(df['STEP']))

            df_selected = sf.view_data_funding_amount(df_org, df_name, df_year, df_step)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                                'SOURCE_URL',
                                                'NOTE', 'ORG_ID', 'NAME'])
            st.dataframe(df_selected,
                         use_container_width=True)

            st.subheader('➕ Add new record')
            col1, col2 = st.columns(2)

            with col1:
                list_of_records = [i[0] for i in sf.view_all_funding_ids()]
                funding_line_id = st.selectbox('FUNDING_LINE_ID', set(df_selected['FUNDING_LINE_ID']))  # list_of_records)
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
                                            '2098', '2099'))
                step = st.selectbox('STEP', ('Request', 'House', 'Senate', 'Enacted'))

            with col2:
                amount = st.number_input('AMOUNT')
                amount_type = st.text_input('AMOUNT_TYPE', 'Dummy amount type')
                source_url = st.text_input('SOURCE_URL', 'Dummy source url')
                note = st.text_area('NOTE', 'Dummy note')

            if st.button('Submit'):
                df = sf.exists_funding_amount(funding_line_id, int(fiscal_year), step, amount_type)
                df = pd.DataFrame(df)

                if not df.empty:
                    st.error("FUNDING AMOUNT is already exists: FUNDING_LINE_ID = '{}', FISCAL_YEAR = {}, STEP = '{}', "
                             "AMOUNT_TYPE = '{}' ".format(
                        funding_line_id, int(fiscal_year), step, amount_type))
                else:
                    sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount, amount_type,
                                                    source_url, note)
                    st.success("New record added to FUNDING AMOUNT: "
                               "FUNDING_LINE_ID = '{}', "
                               "FISCAL_YEAR = {}, "
                               "STEP = '{}', "
                               "AMOUNT_TYPE = '{}'".format(
                        funding_line_id, fiscal_year, step, amount_type))
                    st.experimental_rerun()

        elif tabs == 'Bulk download':
            st.subheader('📥 Bulk download')

            df = sf.view_data_funding_amount()
            df = pd.DataFrame(df,
                              columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                       'SOURCE_URL',
                                       'NOTE', 'ORG_ID', 'NAME'])

            col1, col2 = st.columns(2)
            with col1:
                df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
                df_name = st.multiselect("Select NAME:", set(df['NAME']))
            with col2:
                df_year = st.multiselect("Select FISCAL_YEAR:", set(df['FISCAL_YEAR']))
                df_step = st.multiselect("Select STEP:", set(df['STEP']))

            df_selected = sf.view_data_funding_amount(df_org, df_name, df_year, df_step)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                                'SOURCE_URL',
                                                'NOTE', 'ORG_ID', 'NAME'])
            st.dataframe(df_selected,
                         use_container_width=True)

            @st.experimental_memo
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(df_selected)

            if st.download_button(
                    "Press to Download",
                    csv,
                    "funding_amount.csv",
                    "text/csv",
                    key='download-csv'
            ):
                st.success('The file successfully downloaded.')

        elif tabs == 'Bulk upload':
            st.subheader('📤 Bulk upload')

            uploaded_file = st.file_uploader('Upload CSV', type='.csv')

            if uploaded_file:
                try:
                    csv_df = pd.read_csv(uploaded_file,
                                         delimiter=';',
                                         header=None,
                                         names=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                                'SOURCE_URL',
                                                'NOTE', 'ORG_ID', 'NAME'],
                                         dtype={'FUNDING_LINE_ID': int, 'FISCAL_YEAR': int, 'STEP': str,
                                                'AMOUNT': float,
                                                'NOTE': str},
                                         skiprows=1)

                    with st.expander('File data preview'):
                        csv_df = pd.DataFrame(csv_df,
                                              columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT',
                                                       'AMOUNT_TYPE',
                                                       'SOURCE_URL', 'NOTE'])

                        st.dataframe(csv_df)

                    st.write('')
                    st.write('### Upload from ', uploaded_file.name)
                    st.write('')

                    if st.button('Submit'):

                        if not csv_df.empty:
                            for row in csv_df.itertuples():
                                funding_line_id = row.FUNDING_LINE_ID
                                fiscal_year = row.FISCAL_YEAR
                                step = row.STEP
                                amount = row.AMOUNT
                                amount_type = row.AMOUNT_TYPE
                                source_url = row.SOURCE_URL
                                note = row.NOTE

                                df_amount = sf.exists_funding_amount(funding_line_id, int(fiscal_year), step,
                                                                            amount_type)
                                df_amount = pd.DataFrame(df_amount)

                                if not df_amount.empty:
                                    sf.update_funding_amount(funding_line_id, int(fiscal_year), step,
                                                                    amount_type,
                                                                    int(fiscal_year), step, amount,
                                                                    amount_type, source_url, note)
                                    st.warning("Existing FUNDING AMOUNT record was updated: "
                                               "FUNDING_LINE_ID = '{}', "
                                               "FISCAL_YEAR = {}, STEP = '{}', "
                                               "AMOUNT_TYPE = '{}' ".format(
                                                funding_line_id, int(fiscal_year), step, amount_type))
                                else:
                                    sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount,
                                                                    amount_type,
                                                                    source_url, note)
                                    st.info("New record added to FUNDING AMOUNT: "
                                            "FUNDING_LINE_ID = '{}', "
                                            "FISCAL_YEAR = {}, "
                                            "STEP = '{}', "
                                            "AMOUNT_TYPE = '{}'".format(
                                        funding_line_id, fiscal_year, step, amount_type))

                            st.success('Upload was successfully completed.')
                except Exception as e:
                    st.error(str(e))

        elif tabs == 'Logout':
            cookies['password'] = ''
            cookies['userid'] = ''
            cookies['role'] = ''
            cookies.save()
            st.experimental_rerun()

        else:
            st.subheader('About')
            st.info('Build for AIP.ORG by Dmitry Taranenko@dPrism')


if __name__ == '__main__':
    main()
