import streamlit as st
import pandas as pd
import aip

aip.build(page_title='Bulk upload', page_icon='📤')
sf = aip.get_snowflake()
userid = sf.current_user()

if sf.connected():
    st.info('🪄 You can use bulk upload by selecting the csv file, \n'
            'please verify the data and push it into the Preview table by clicking \'Submit\' button')

    config = aip.get_yaml()

    delimiter = config['file_upload']['delimiter']
    uploaded_file = st.file_uploader('Upload CSV', type='.csv')

    if uploaded_file:
        try:
            csv_data = pd.read_csv(uploaded_file,
                                   delimiter=delimiter,
                                   header=None,
                                   names=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE',
                                          'VERSION', 'FL_NOTE',
                                          'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'FA_NOTE'],
                                   dtype={'FUNDING_LINE_ID': int, 'FISCAL_YEAR': int, 'AMOUNT': float},  # 'VERSION':
                                   # int,
                                   skiprows=1)

            csv_df = pd.DataFrame(csv_data,
                                  columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE',
                                           'VERSION', 'FL_NOTE',
                                           'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                           'SOURCE_URL', 'FA_NOTE']
                                  )

            # csv_df['FUNDING_TYPE'] = csv_df['FUNDING_TYPE'].fillna('')
            # csv_df['VERSION'] = csv_df['VERSION'].fillna(0)
            csv_df['AMOUNT_TYPE'] = csv_df['AMOUNT_TYPE'].fillna('')
            csv_df['SOURCE_URL'] = csv_df['SOURCE_URL'].fillna('')
            csv_df['FA_NOTE'] = csv_df['FA_NOTE'].fillna('')

            st.dataframe(csv_df)

            st.write('')
            st.write('### Upload from ', uploaded_file.name)
            st.write('')

            # st.info(csv_df)

            if st.button('Submit'):

                if not csv_df.empty:
                    for row in csv_df.itertuples():
                        funding_line_id = row.FUNDING_LINE_ID
                        fiscal_year = row.FISCAL_YEAR
                        step = row.STEP
                        amount = row.AMOUNT
                        amount_type = row.AMOUNT_TYPE
                        source_url = row.SOURCE_URL
                        note = row.FA_NOTE

                        df_amount_upload = sf.exist_funding_amount_upload(userid, int(funding_line_id),
                                                                          int(fiscal_year), step, amount_type)
                        df_amount_upload = pd.DataFrame(df_amount_upload)

                        if not df_amount_upload.empty:
                            sf.update_funding_amount_upload(userid, int(funding_line_id), int(fiscal_year), step,
                                                            amount_type, int(fiscal_year), step, float(amount),
                                                            amount_type, source_url, note)
                            st.warning("""
                                            Existing FUNDING AMOUNT PREVIEW was updated for '{}': 
                                            FUNDING_LINE_ID = {}, 
                                            FISCAL_YEAR = {}, STEP = '{}', 
                                            AMOUNT_TYPE = '{}' 
                                        """.format(userid, int(funding_line_id), int(fiscal_year), step, amount_type))
                        else:
                            sf.insert_funding_amount_upload(userid, int(funding_line_id), int(fiscal_year), step,
                                                            float(amount), amount_type, source_url, note)
                            st.info("""
                                        New record added to FUNDING AMOUNT PREVIEW for '{}': "
                                        FUNDING_LINE_ID = {}, "
                                        FISCAL_YEAR = {}, "
                                        STEP = '{}', "
                                        AMOUNT_TYPE = '{}'
                                    """.format(userid, int(funding_line_id), int(fiscal_year), step, amount_type))

                    st.success('Upload was successfully completed.')

        except Exception as e:
            st.error(str(e))
