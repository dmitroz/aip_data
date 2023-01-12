import streamlit as st
import pandas as pd
from aip_db import *
import streamlit.components.v1 as stc

HTML_BANNER = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:10px;border-radius:10px\">\n"
               "    <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "    <h1 style=\"color:white;text-align:center;\">Datа management demo</h1>\n"
               "    <p style=\"color:white;text-align:center;\">Built with Streamlit</p>\n"
               "    </div>\n"
               "    ")


def main():
    stc.html(HTML_BANNER)

    menu = ['Upload', 'Create', 'Read', 'Update', 'Delete', 'About']
    choice = st.sidebar.selectbox('Menu', menu)
    # create_table()

    if choice == 'Upload':
        st.subheader('Bulk upload')

        uploaded_file = st.file_uploader('Upload CSV', type='.csv')

        use_example_file = st.checkbox(
            'Use example file', True, help='Use in-built example file to demo the app'
        )

        # If CSV is not uploaded and checkbox is filled, use values from the example file
        # and pass them down to the next if block
        if use_example_file:
            uploaded_file = 'demo_file.csv'

        if uploaded_file:
            columns = ['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES']
            df = pd.read_csv(uploaded_file, delimiter=',', header=None, names=columns, skiprows=1)  # , dtype={'AMOUNT': 'Number'})

            st.markdown('### File data preview')
            st.dataframe(df.head())

            # submit_button = st.form_submit_button(label='Submit')

            # type(uploaded_file) == str, means the example file was used
            name = (
                'demo_file.csv' if isinstance(uploaded_file, str) else uploaded_file.name
            )
            st.write('')
            st.write('### Bulk upload from ', name)
            st.write('')

            if st.button('Submit'):
                for row in df.itertuples():
                    key = row.ID
                    funding_line_id = row.FUNDINGLINEID
                    fiscal_year = row.FISCALYEAR
                    step = row.STEP
                    amount = row.AMOUNT
                    notes = row.NOTES
                    insert_record(key, funding_line_id, fiscal_year, step, amount, notes)
                    st.success('Added: {}, {}, {}, {}, {}, {} to FUNDINGAMOUNTS table'.format(
                        key, funding_line_id, fiscal_year, step,  amount, notes))

                # insert_record(key, funding_line_id, fiscal_year, step, amount, notes)
                # st.success('Added: {}, {}, {}, {}, {}, {} to FUNDINGAMOUNTS table'.format(
                #    key, funding_line_id, fiscal_year, step,  amount, notes)
                # )

    elif choice == 'Create':
        st.subheader('Add record')
        col1, col2 = st.columns(2)

        with col1:
            note = st.text_area('Funding amounts note')

        with col2:
            key = st.number_input('Key', 55555)
            funding_line_id = st.text_input('Funding Line ID', 'DOE-OS')
            fiscal_year = st.number_input('Fiscal Year', 2022)
            step = st.selectbox('Step', ['Enacted', 'Actual', 'Request',
                                         'Request Plus Mandatory', 'House', 'Senate', 'Request w Add',
                                         'House Stimulus'])
            amount = st.number_input('Amount', 7777)

        if st.button('Submit'):
            insert_record(key, funding_line_id, fiscal_year, step, amount, note)
            st.success(
                'Added: {}, {}, {}, {}, {} to FUNDINGAMOUNTS table'.format(key, funding_line_id, fiscal_year, step,
                                                                           amount))


    elif choice == 'Read':
        st.subheader('View records')
        with st.expander('View all records'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result, columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
            st.dataframe(clean_df)

        # with st.expander("STEP"):
        #    task_df = clean_df['STEP'].value_counts().to_frame()
        #    # st.dataframe(task_df)
        #    task_df = task_df.reset_index()
        #    st.dataframe(task_df)

        #    p1 = px.pie(task_df, names='index', values='STEP')
        #    st.plotly_chart(p1, use_container_width=True)


    elif choice == 'Update':
        st.subheader('Update record')
        with st.expander('Current record'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result,
                                    columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
            st.dataframe(clean_df)

        list_of_records = [i[0] for i in view_all_ids()]
        selected_id = st.selectbox('KEY', list_of_records)
        return_id = get_record(selected_id)
        # st.write(task_result)

        if return_id:
            key = return_id[0][0]
            # funding_line_id = return_id[0][1]
            # fiscal_year = return_id[0][2]
            # step = return_id[0][3]
            amount = return_id[0][4]
            notes = return_id[0][5]

            col1, col2 = st.columns(2)

            with col1:
                new_note = st.text_area('New note', notes)

            with col2:
                # new_step = st.selectbox(step, ["Enacted", "Actual", "Request",
                #                                "Request Plus Mandatory", "House", "Senate", "Request w Add",
                #                                "House Stimulus"])
                new_amount = st.number_input("Input amount", amount)

            if st.button('Update record'):
                update_record(new_amount, new_note, funding_line_id, fiscal_year, step)
                st.success('Updated ::{} ::to FUNDINGAMOUNTS table {}'.format(amount, new_amount))

            with st.expander('View updated record'):
                result = get_record(key)  # view_data()
                # st.write(result)
                clean_df = pd.DataFrame(result,
                                        columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
                st.dataframe(clean_df)


    elif choice == 'Delete':
        st.subheader('Delete record')
        with st.expander('View data'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result,
                                    columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
            st.dataframe(clean_df)

        unique_list = [i[0] for i in view_all_ids()]
        delete_by_id = st.selectbox('Select record', unique_list)
        if st.button('Delete'):
            delete_record(delete_by_id)
            st.warning('Deleted: {}'.format(delete_by_id))

        with st.expander('Updated record'):
            result = get_record(delete_by_id)  # view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result,
                                    columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
            st.dataframe(clean_df)

    else:
        st.subheader('About')
        st.info('Build for AIP.ORG by dPrism')
        # st.text('Dmitry Taranenko')


if __name__ == '__main__':
    main()