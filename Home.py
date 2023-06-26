import aip
from aip import *

# Trick to preserve the state of your widgets across pages
for k, v in st.session_state.items():
    st.session_state[k] = v
##

aip.build(page_title='Home page', page_icon='🏠')
sf = aip.get_snowflake()

if sf.connected():
    # Content
    st.write(
        """Welcome to the **AIP FYI Budget Tracker App** \n - The app provides a management interface for accessing and 
        maintaining multi-level government agency budget request/approval data. \n - The expandable menu items on the 
        left (hover over the icons) serve as the primary navigation for the app. \n - Organization provides a list of the 
        multi-leveled agencies tracked by the FYI team.  The filter at the top allows for the filtering/drill down 
        viewing of an organization/agency and its \'children\' committees and sub-committees that are tracked by the FYI 
        team.  When hovering over the list (dataframe) an icon appears to the upper right - clicking allows you to view 
        the dataframe at full screen width.  Below the dataframe, there is a form to add an organization to the list. 
        **Note** - there is purposely no means to edit and delete organizations due to impact to legacy data and low 
        need. Edits and deletes will be handled by qualified staff directly in the database. \n - Funding Line is 
        analogous screen to the Organization.  Allows viewing of funding lines related to organizations.  There are 
        filters to drill down into the dataframe at the top, expand the view, and a form at the bottom to add a funding 
        line. \n - Edit Line - directly below Funding Line - is analogous the Funding Line screen - but allows for drill 
        down to a particular funding line along with an edit form at the bottom for making changes. \n - Funding Amount 
        is analogous to Organization and Funding Line screens - drill down filters, dataframe, and a form for adding new 
        funding amounts.  Editing and upload of new funding amount data in bulk is handled by the following screens. 
        \n - Bulk Download allows for a csv file download of Funding Amounts for spreadsheet style editing.  Drill down 
        filters at the top allow for the selection of an Org, Funding Name, Fiscal Year and/or Step in the budget 
        approval process.  Download a fully populated csv ready for editing, or check the \'Download blank values\' and 
        get an org and its funding lines ready to populate for a full fiscal year and step. \n - Bulk Upload is intended 
        to allow for the re-upload of edited csv files originally downloaded from Bulk Download. The uploaded data will 
        be saved in a preview table - not the final table. \n - Sync All allows for the viewing of all data uploaded and 
        staged in the preview table.  Filter the preview data, review and either submit or clear the data (if preview 
        finds errors or issues - then clear, correct issues in the csv file, and re-upload). \n - Log out will exit a 
        user from the app.  Also, there is an automated timeout to logout stale sessions after 2 hours.) """
    )
