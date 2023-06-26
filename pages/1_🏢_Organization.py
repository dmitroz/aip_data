import pandas as pd
import aip
from aip import *

aip.build(page_title='Organization list', page_icon='🏢')
sf = aip.get_snowflake()

if sf.connected():

    sf_org = sf.view_data_organization()
    pd.DataFrame(sf_org, columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])

    sf_org_ids = sf.view_all_org_ids()
    if sf_org_ids is not None:
        select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf_org_ids])
    else:
        select_org = st.multiselect("Select ORG_ID:", [])

    sf_select_org = sf.view_child_org_ids(select_org)
    df_select_org = pd.DataFrame(sf_select_org,
                                 columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])
    st.dataframe(df_select_org,
                 use_container_width=True)

    st.subheader('➕ Add new record')
    col1, col2 = st.columns(2)

    with col1:
        org = st.text_input('ORG')
        list_of_records = ['<NA>'] + [str(i[0]) for i in sf_org_ids]
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
        name = st.text_input('NAME')  # , 'Dummy name')

    if st.button('Submit'):
        df_org_ids = pd.DataFrame(sf_org_ids)

        if org_id in set(df_org_ids.values[:, 0]):
            st.error("ORGANIZATION is already exists: ORG_ID = '{}' ".format(org_id))
        else:
            sf.insert_organization(org.upper(), parent, org_id, int(level), name)
            st.success("New record added to ORGANIZATION: ORG_ID = '{}'".format(org_id))
