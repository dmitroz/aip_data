import pandas as pd
import aip
from aip import *

aip.build(page_title='Funding Line', page_icon='📁')
sf = aip.get_snowflake()

if sf.connected():
    sf_line = sf.view_data_funding_line()
    df_line = pd.DataFrame(sf_line,
                           columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])

    col1, col2 = st.columns(2)
    with col1:
        sf_org_ids = sf.view_all_org_ids()
        if sf_org_ids is not None:
            select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf_org_ids])
        else:
            select_org = st.multiselect("Select ORG_ID:", [])
    with col2:
        select_name = st.multiselect("Select NAME:", set(df_line['NAME']))

    df_selected = sf.view_data_funding_line(df_org=select_org, df_name=select_name)
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
        list_of_records = [i[0] for i in sf_org_ids]
        org_id = st.selectbox('ORG_ID', list_of_records)
        name = st.text_input('NAME')  # , 'Dummy name')

    with col2:
        funding_type = st.text_input('FUNDING_TYPE')
        version = st.number_input('VERSION', 0)
        top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'))
        note = st.text_area('NOTE')  # , 'Dummy note')

    if st.button('Submit'):
        sf_line = sf.exist_funding_line(org_id, name, version)
        df_line = pd.DataFrame(sf_line)

        if not df_line.empty:
            st.error("FUNDING LINE is already exists: ORG_ID = '{}', NAME = '{}', VERSION = {} ".format(
                org_id, name, version))
        else:
            sf.insert_funding_line(int(last_row[0].values + 1), org_id, name, funding_type, version,
                                   top_line, note)
            st.success("New record added to FUNDING LINE: ORG_ID = '{}', NAME = '{}', VERSION = {}".format(
                org_id, name, version))
