import yaml
import json
from json import JSONDecodeError
from aip_db import Snowflake
import extra_streamlit_components as stx
import streamlit as st
from datetime import datetime, timedelta
import base64
import streamlit.components.v1 as stc

cookie_name = 'streamlit_cookie'


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_snowflake():
    return Snowflake()


def get_yaml():
    with open("config.yaml") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def save_cookie(userid, password, role, schema, database, account, warehouse):
    config = get_yaml()
    minutes = config['cookie']['expiry_minutes']
    expire = datetime.now() + timedelta(minutes=minutes)
    value = expire.strftime("%Y-%m-%d %H:%M:%S")
    streamlit_cookie = {
        "userid": userid,
        "password": password,
        "role": role,
        "expire": value,
        "schema": schema,
        "database": database,
        "account": account,
        "warehouse": warehouse
    }
    json_string = json.dumps(streamlit_cookie)
    message_bytes = json_string.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    get_manager().set(cookie_name, base64_message, expires_at=datetime.max)


def get_cookie_values():
    user_value, password_value, role_value, expire_value, schema_value, database_value, account_value, warehouse_value \
        = None, None, None, None, None, None, None, None

    json_data = get_manager().get(cookie_name)

    if json_data:
        base64_bytes = json_data.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        streamlit_cookie = json.loads(message)
        try:
            user_value = streamlit_cookie['userid']
            password_value = streamlit_cookie['password']
            role_value = streamlit_cookie['role']
            expire_value = streamlit_cookie['expire']
            schema_value = streamlit_cookie['schema']
            database_value = streamlit_cookie['database']
            account_value = streamlit_cookie['account']
            warehouse_value = streamlit_cookie['warehouse']
        except JSONDecodeError:
            pass

    return [user_value, password_value, role_value, expire_value, schema_value, database_value, account_value,
            warehouse_value]


def clear_cookie_manager():
    get_manager().get_all()
    if get_manager().get(cookie_name):
        get_manager().delete(cookie_name)

    get_snowflake().clear_authorization()


def build(page_title, page_icon):
    # Config
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout='wide')

    # Style
    with open('style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # col1, col2 = st.columns((6, 1))
    # col1.title(page_icon + " " + page_title)
    # col2.image("assets/aip-logo-180.png", width=120)

    sf = get_snowflake()
    cookie_manager = get_manager()
    cookie_manager.get_all()

    [userid, password, role, value, schema, database, account, warehouse] = get_cookie_values()

    if schema:
        schema_str = schema + ", version 2.0"
    else:
        schema_str = "version 2.0"

    html_banner = ("    \n"
                   "    <div style=\"background-color:#0B074E;padding:16px;border-radius:10px\">\n"
                   "        <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
                   "        <h1 style=\"color:white;"
                   "            text-align:center;"
                   "            font-family:Trebuchet MS, sans-serif;\">FYI Budget Tracker "
                   "        </h1>\n"
                   "        <h2 style=\"color:white;"
                   "            text-align:center;"
                   "            font-family:Trebuchet MS, sans-serif;\">" + schema_str + ""
                                                                                         "        </h2>\n"
                                                                                         "    </div>\n"
                                                                                         "    ")

    stc.html(html_banner, height=225)

    st.title(page_icon + " " + page_title)

    expire = datetime.now()

    st.info('Log: expire {}'.format(value))

    if value is not None:
        expire = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    if expire < datetime.now():
        if cookie_manager.get(cookie_name):
            # cookie_manager.delete(cookie_name)
            clear_cookie_manager()

        userid = ''
        password = ''
        role = ''

    if userid is None:
        userid = ''

    if password is None:
        password = ''

    if userid != '' and password != '':
        try:
            sf.authorization(userid, password, role, schema, database, account, warehouse)
            save_cookie(userid, password, role, schema, database, account, warehouse)
        except Exception as e:
            st.error(str(e))

    if sf.not_connected():
        st.subheader('🧑‍💻 Authorization')

        config = get_yaml()

        sf_account = config['snowflake']['account']
        sf_database = config['snowflake']['database']
        sf_schema = config['snowflake']['schema']
        sf_warehouse = config['snowflake']['warehouse']
        sf_role = config['snowflake']['role']

        userid = st.text_input('Username').lower()
        password = st.text_input('Password', type="password")
        role = st.selectbox('Snowflake role',
                            sf_role,
                            index=2,
                            disabled=False)  # True)

        col1, col2 = st.columns(2)

        with col1:
            st.text_input('Snowflake database', sf_database, disabled=True)
            st.text_input('Snowflake account', sf_account, disabled=True)
        with col2:
            select_schema = st.selectbox('Snowflake schema', sf_schema, index=3)
            st.text_input('Snowflake warehouse', sf_warehouse, disabled=True)

        if st.button('Login'):
            if userid == '' or password == '':
                st.warning('Please provide account and password to login.')
            else:
                try:
                    sf.authorization(userid, password, role, select_schema, sf_database, sf_account,
                                     sf_warehouse)
                    save_cookie(userid, password, role, select_schema, sf_database, sf_account,
                                sf_warehouse)

                except Exception as e:
                    st.error(str(e))
