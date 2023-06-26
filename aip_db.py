import snowflake.connector
import streamlit
import yaml


class Snowflake:
    def __init__(self):
        self.connect = None
        self.cx = None
        self.user = None

        with open("config.yaml") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def clear_authorization(self):
        self.connect = None
        self.cx = None
        self.user = None

    def not_connected(self):
        return self.cx is None

    def connected(self):
        return self.cx is not None

    def current_user(self):
        return self.user

    def authorization(self, user, password, role, schema, database, account, warehouse):
        self.connect = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            database=database,
            schema=schema,
            warehouse=warehouse,
            role=role,
            insecure_mode=self.config['snowflake']['insecure_mode'],
            # ocsp_fail_open=False,
            use_openssl_only=self.config['snowflake']['use_openssl_only'])
        self.cx = self.connect.cursor()
        self.cx.execute("SELECT CURRENT_VERSION()")
        self.user = user
        data = self.cx.fetchone()
        return data

    def insert_organization(self, org, parent, org_id, level, name):
        if parent == '<NA>':
            self.cx.execute("""
                                INSERT INTO ORGANIZATION(ORG, ORG_ID, LEVEL, NAME) VALUES ('{}', '{}', {}, '{}')
                            """.format(org, org_id, level, name))
        else:
            self.cx.execute("""
                                INSERT INTO ORGANIZATION(ORG, PARENT, ORG_ID, LEVEL, NAME) 
                                VALUES ('{}', '{}', '{}', {}, '{}')
                            """.format(org, parent, org_id, level, name))
        self.connect.commit()

    def view_all_org_ids(self):
        self.cx.execute("""
                            SELECT DISTINCT ORG_ID FROM ORGANIZATION ORDER BY ORG_ID
                        """)
        data = self.cx.fetchall()
        return data

    def view_data_organization(self, org_list=None):
        query_str = ''
        if org_list is None or org_list == []:
            self.cx.execute("SELECT * FROM ORGANIZATION ORDER BY ORG_ID")
        else:
            for index in org_list:
                if query_str is '':
                    query_str = "ORG_ID = '{}' ".format(index)
                else:
                    query_str += "OR ORG_ID = '{}' ".format(index)
            self.cx.execute("SELECT * FROM ORGANIZATION WHERE {} ORDER BY PARENT ASC".format(query_str))

        data = self.cx.fetchall()
        return data

    def view_child_org_ids(self, org_list=None):
        child_query = ''

        if org_list is None or org_list == []:
            self.cx.execute("SELECT * FROM ORGANIZATION ORDER BY ORG_ID")
        else:
            for index in org_list:
                if child_query is '':
                    # child_query = "B.ORG_ID = '{}' ".format(index)
                    child_query = "A.ORG_ID LIKE '%{}%' ".format(index)
                else:
                    # child_query += "OR B.ORG_ID = '{}' ".format(index)
                    child_query += "OR A.ORG_ID LIKE '%{}%' ".format(index)
            self.cx.execute("SELECT A.ORG, A.PARENT, A.ORG_ID, A.LEVEL, A.NAME FROM ORGANIZATION AS A "
                            # "LEFT JOIN ORGANIZATION AS B ON A.PARENT = B.ORG_ID "
                            "WHERE {} ORDER BY A.ORG_ID ASC".format(child_query))

        data = self.cx.fetchall()
        return data

    def get_parent_level(self, org):
        self.cx.execute("SELECT LEVEL FROM ORGANIZATION WHERE ORG_ID = '{}'".format(org))
        data = self.cx.fetchall()
        return data

    def get_last_row(self):
        self.cx.execute('SELECT MAX(ORG) FROM ORGANIZATION')
        data = self.cx.fetchall()
        return data

    def view_data_funding_line(self, df_org=None, df_name=None, df_id=None):
        query_org = ''
        query_name = ''

        if df_id:
            self.cx.execute("SELECT * FROM FUNDING_LINE WHERE ID = {} ORDER BY ID".format(df_id))
        else:
            if (df_org is None or df_org == []) and (df_name is None or df_name == []):
                self.cx.execute("SELECT * FROM FUNDING_LINE ORDER BY ID")
            else:
                if df_org:
                    for index in df_org:
                        if query_org is '':
                            # query_org = "B.ORG_ID = '{}' ".format(index)
                            query_org = "A.ORG_ID LIKE '%{}%' ".format(index)
                        else:
                            # query_org += "OR B.ORG_ID = '{}' ".format(index)
                            query_org += "OR A.ORG_ID LIKE '%{}%' ".format(index)
                    query_org = '(' + query_org + ')'
                else:
                    query_org = '(1 = 1)'

                if df_name:
                    for index in df_name:
                        if query_name is '':
                            query_name = "FL.NAME = '{}' ".format(index)
                        else:
                            query_name += "OR FL.NAME = '{}' ".format(index)
                    query_name = '(' + query_name + ')'
                else:
                    query_name = '(2 = 2)'

                self.cx.execute(
                    "SELECT FL.ID, FL.ORG_ID, FL.NAME, FL.FUNDING_TYPE, FL.VERSION, FL.TOP_LINE, FL.NOTE "
                    "FROM FUNDING_LINE AS FL "
                    "INNER JOIN ORGANIZATION AS A ON FL.ORG_ID = A.ORG_ID "
                    # "LEFT JOIN ORGANIZATION AS B ON A.PARENT = B.ORG_ID "
                    "WHERE {} ORDER BY ID ASC".format(query_org + ' AND ' + query_name))

        data = self.cx.fetchall()
        return data

    def view_data_funding_line_old(self, df_org=None, df_name=None, df_id=None):
        query_org = ''
        query_name = ''

        if df_id:
            self.cx.execute("SELECT * FROM FUNDING_LINE WHERE ID = {} ORDER BY ID".format(df_id))
        else:
            if (df_org is None or df_org == []) and (df_name is None or df_name == []):
                self.cx.execute("SELECT * FROM FUNDING_LINE ORDER BY ID")
            else:
                if df_org:
                    for index in df_org:
                        if query_org is '':
                            query_org = "ORG_ID = '{}' ".format(index)
                        else:
                            query_org += "OR ORG_ID = '{}' ".format(index)
                    query_org = '(' + query_org + ')'
                else:
                    query_org = '(1 = 1)'

                if df_name:
                    for index in df_name:
                        if query_name is '':
                            query_name = "NAME = '{}' ".format(index)
                        else:
                            query_name += "OR NAME = '{}' ".format(index)
                    query_name = '(' + query_name + ')'
                else:
                    query_name = '(2 = 2)'

                self.cx.execute(
                    "SELECT * FROM FUNDING_LINE WHERE {} ORDER BY ID ASC".format(query_org + ' AND ' + query_name))

        data = self.cx.fetchall()
        return data

    def get_last_row_funding_line(self):
        self.cx.execute('SELECT MAX(ID) FROM FUNDING_LINE')
        data = self.cx.fetchall()
        return data

    def exist_funding_line(self, org_id, name, version):
        self.cx.execute("""
                            SELECT ORG_ID, NAME, VERSION FROM FUNDING_LINE 
                            WHERE ORG_ID = '{}' AND NAME = '{}' AND VERSION = {}
                        """.format(org_id, name, version))
        data = self.cx.fetchall()
        return data

    def insert_funding_line(self, line_id, org_id, name, funding_type, version, top_line, note):
        self.cx.execute("""
                            INSERT INTO FUNDING_LINE(ID, ORG_ID, NAME, FUNDING_TYPE, VERSION, TOP_LINE, NOTE) 
                            VALUES ({}, '{}', '{}', '{}', {}, {}, '{}')
                        """.format(line_id, org_id, name, funding_type, version, top_line, note))
        self.connect.commit()

    def update_funding_line(self, line_id, org_id, name, funding_type, version, top_line, note):
        self.cx.execute("""
                            UPDATE FUNDING_LINE SET 
                            ORG_ID = '{}', 
                            NAME = '{}', 
                            FUNDING_TYPE = '{}', 
                            VERSION = {}, 
                            TOP_LINE = {}, 
                            NOTE = '{}' 
                            WHERE ID = {} 
                        """.format(org_id, name, funding_type, version, top_line, note, line_id))
        self.connect.commit()
        data = self.cx.fetchall()
        return data

    def view_all_funding_ids(self):
        self.cx.execute("SELECT DISTINCT ID FROM FUNDING_LINE ORDER BY ID")
        data = self.cx.fetchall()
        return data

    def view_data_funding_amount(self, isblank=False, df_org=None, df_name=None, df_year=None, df_step=None):
        query_org = ''
        query_name = ''
        query_year = ''
        query_step = ''

        if df_org:
            for index in df_org:
                if query_org is '':
                    # query_org = "FL.ORG_ID = '{}' ".format(index)
                    query_org = "FL.ORG_ID LIKE '%{}%' ".format(index)
                else:
                    # query_org += "OR FL.ORG_ID = '{}' ".format(index)
                    query_org += "OR FL.ORG_ID LIKE '%{}%' ".format(index)
            query_org = '(' + query_org + ')'
        else:
            query_org = '(1 = 1)'

        if df_name:
            for index in df_name:
                if query_name is '':
                    query_name = "FL.NAME = '{}' ".format(index)
                else:
                    query_name += "OR FL.NAME = '{}' ".format(index)
            query_name = '(' + query_name + ')'
        else:
            query_name = '(2 = 2)'

        if df_year:
            for index in df_year:
                if query_year is '':
                    query_year = "FA.FISCAL_YEAR = {} ".format(index)
                else:
                    query_year += "OR FA.FISCAL_YEAR = {} ".format(index)
            query_year = '(' + query_year + ')'
        else:
            query_year = '(3 = 3)'

        if df_step:
            for index in df_step:
                if query_step is '':
                    query_step = "FA.STEP = '{}' ".format(index)
                else:
                    query_step += "OR FA.STEP = '{}' ".format(index)
            query_step = '(' + query_step + ')'
        else:
            query_step = '(4 = 4)'

        if isblank:
            self.cx.execute("""
                            SELECT 
                            FA.FUNDING_LINE_ID, 
                            FL.ORG_ID,
                            FL.NAME, 
                            FL.FUNDING_TYPE, 
                            FL.VERSION,                            
                            FL.NOTE AS FL_NOTE, 
                            \'\' AS FISCAL_YEAR, 
                            \'\' AS STEP, 
                            \'\' AS AMOUNT, 
                            \'\' AS AMOUNT_TYPE, 
                            \'\' AS SOURCE_URL, 
                            \'\' AS FA_NOTE 
                            FROM FUNDING_AMOUNT AS FA 
                            JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID 
                            JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID 
                            WHERE {} 
                            GROUP BY FA.FUNDING_LINE_ID, FL.ORG_ID, FL.NAME, FL.FUNDING_TYPE, FL.VERSION, FL.NOTE 
                            ORDER BY FL.ORG_ID ASC 
                            """.format(query_org + ' AND ' + query_name + ' AND ' + query_year + ' AND ' + query_step))
        else:
            self.cx.execute("""
                            SELECT 
                            FA.FUNDING_LINE_ID, 
                            FL.ORG_ID,
                            FL.NAME, 
                            FL.FUNDING_TYPE,
                            FL.VERSION,                             
                            FL.NOTE AS FL_NOTE, 
                            FA.FISCAL_YEAR, 
                            FA.STEP, 
                            FA.AMOUNT, 
                            FA.AMOUNT_TYPE, 
                            FA.SOURCE_URL, 
                            FA.NOTE AS FA_NOTE
                            FROM FUNDING_AMOUNT AS FA 
                            JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID 
                            JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID 
                            WHERE {} 
                            ORDER BY FL.ORG_ID ASC 
                            """.format(query_org + ' AND ' + query_name + ' AND ' + query_year + ' AND ' + query_step))

        data = self.cx.fetchall()
        return data

    def exist_funding_amount(self, funding_line_id, fiscal_year, step, amount_type):
        self.cx.execute("""
                            SELECT * FROM FUNDING_AMOUNT 
                            WHERE FUNDING_LINE_ID = '{}' 
                            AND FISCAL_YEAR = {} 
                            AND STEP = '{}' 
                            AND AMOUNT_TYPE = '{}'
                        """.format(funding_line_id, fiscal_year, step, amount_type))
        data = self.cx.fetchall()
        return data

    def insert_funding_amount(self, funding_line_id, fiscal_year, step, amount, amount_type, source_url, note):
        self.cx.execute("""
                            INSERT INTO FUNDING_AMOUNT(FUNDING_LINE_ID, FISCAL_YEAR, STEP, AMOUNT, AMOUNT_TYPE, SOURCE_URL, 
                            NOTE)
                            VALUES ({}, {}, '{}', {}, '{}', '{}', '{}')
                        """.format(funding_line_id, fiscal_year, step, amount, amount_type, source_url, note))
        self.connect.commit()

    def update_funding_amount(self, funding_line_id, fiscal_year, step, amount_type, new_fiscal_year, new_step,
                              new_amount, new_amount_type, new_source_url, new_note):
        self.cx.execute("""
                            UPDATE FUNDING_AMOUNT SET 
                            FISCAL_YEAR = {}, 
                            STEP = '{}', 
                            AMOUNT = {}, 
                            AMOUNT_TYPE = '{}', 
                            SOURCE_URL = '{}', 
                            NOTE = '{}' 
                            WHERE FUNDING_LINE_ID = '{}' 
                            AND FISCAL_YEAR = {} 
                            AND STEP = '{}' 
                            AND AMOUNT_TYPE = '{}'
                        """.format(new_fiscal_year, new_step, new_amount, new_amount_type, new_source_url, new_note,
                                   funding_line_id, fiscal_year, step, amount_type))
        self.connect.commit()
        data = self.cx.fetchall()
        return data

    def get_funding_amount(self, funding_line_id):
        self.cx.execute("""
                            SELECT * FROM FUNDING_AMOUNT WHERE FUNDING_LINE_ID ={}
                        """.format(funding_line_id))
        data = self.cx.fetchall()
        return data

    def get_funding_amount_list(self, funding_line_list):
        for index, value in funding_line_list.items():
            if index == 0:
                query_str = 'FUNDING_LINE_ID = {}'.format(value)
            else:
                query_str += ' OR FUNDING_LINE_ID = {}'.format(value)

        self.cx.execute(
            'SELECT * FROM FUNDING_AMOUNT WHERE {}'.format(query_str))

        data = self.cx.fetchall()
        return data

    def view_data_funding_amount_upload(self, extended=False, df_org=None, df_name=None, df_year=None, df_step=None,
                                        df_user=None):
        query_org = ''
        query_name = ''
        query_year = ''
        query_step = ''
        query_user = ''

        if df_org:
            for index in df_org:
                if query_org is '':
                    query_org = "FL.ORG_ID = '{}' ".format(index)
                else:
                    query_org += "OR FL.ORG_ID = '{}' ".format(index)
            query_org = '(' + query_org + ')'
        else:
            query_org = '(1 = 1)'

        if df_name:
            for index in df_name:
                if query_name is '':
                    query_name = "FL.NAME = '{}' ".format(index)
                else:
                    query_name += "OR FL.NAME = '{}' ".format(index)
            query_name = '(' + query_name + ')'
        else:
            query_name = '(2 = 2)'

        if df_year:
            for index in df_year:
                if query_year is '':
                    query_year = "FA.FISCAL_YEAR = {} ".format(index)
                else:
                    query_year += "OR FA.FISCAL_YEAR = {} ".format(index)
            query_year = '(' + query_year + ')'
        else:
            query_year = '(3 = 3)'

        if df_step:
            for index in df_step:
                if query_step is '':
                    query_step = "FA.STEP = '{}' ".format(index)
                else:
                    query_step += "OR FA.STEP = '{}' ".format(index)
            query_step = '(' + query_step + ')'
        else:
            query_step = '(4 = 4)'

        if df_user:
            for index in df_user:
                if query_user is '':
                    query_user = "FA.USER = '{}' ".format(index)
                else:
                    query_user += "OR FA.USER = '{}' ".format(index)
            query_user = '(' + query_user + ')'
        else:
            query_user = '(5 = 5)'

        if extended:
            self.cx.execute("""
                                SELECT 
                                FA.USER, 
                                FA.FUNDING_LINE_ID, 
                                FL.ORG_ID,
                                FL.NAME, 
                                FA.FISCAL_YEAR, 
                                FA.STEP, 
                                FA.AMOUNT, 
                                FA.AMOUNT_TYPE, 
                                FA.SOURCE_URL, 
                                FA.NOTE 
                                FROM FUNDING_AMOUNT_UPLOAD AS FA 
                                JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID 
                                JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID 
                                WHERE {}
                            """.format(query_org + ' AND ' + query_name + ' AND ' + query_year + ' AND ' + query_step +
                                       ' AND ' + query_user))
        else:
            self.cx.execute("""
                                SELECT 
                                FA.FUNDING_LINE_ID, 
                                FL.ORG_ID, 
                                FL.NAME, 
                                FA.FISCAL_YEAR, 
                                FA.STEP, 
                                FA.AMOUNT, 
                                FA.AMOUNT_TYPE, 
                                FA.SOURCE_URL, 
                                FA.NOTE 
                                FROM FUNDING_AMOUNT_UPLOAD AS FA 
                                JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID 
                                JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID 
                                WHERE {}
                            """.format(query_org + ' AND ' +
                                       query_name + ' AND ' +
                                       query_year + ' AND ' +
                                       query_step + ' AND ' +
                                       query_user))

        data = self.cx.fetchall()
        return data

    def exist_funding_amount_upload(self, userid, funding_line_id, fiscal_year, step, amount_type):
        self.cx.execute("""
                            SELECT * FROM FUNDING_AMOUNT_UPLOAD 
                            WHERE USER = '{}' 
                            AND FUNDING_LINE_ID = {} 
                            AND FISCAL_YEAR = {}
                            AND STEP = '{}'
                            AND AMOUNT_TYPE = '{}'
                        """.format(userid, funding_line_id, fiscal_year, step, amount_type))
        data = self.cx.fetchall()
        return data

    def delete_funding_amount_upload(self, df_org=None, df_name=None, df_year=None, df_step=None,
                                     df_user=None):
        query_org = ''
        query_name = ''
        query_year = ''
        query_step = ''
        query_user = ''

        if df_org:
            for index in df_org:
                if query_org == '':
                    query_org = "FL.ORG_ID = '{}' ".format(index)
                else:
                    query_org += "OR FL.ORG_ID = '{}' ".format(index)
            query_org = '(' + query_org + ')'
        else:
            query_org = '(1 = 1)'

        if df_name:
            for index in df_name:
                if query_name == '':
                    query_name = "FL.NAME = '{}' ".format(index)
                else:
                    query_name += "OR FL.NAME = '{}' ".format(index)
            query_name = '(' + query_name + ')'
        else:
            query_name = '(2 = 2)'

        if df_year:
            for index in df_year:
                if query_year == '':
                    query_year = "FA.FISCAL_YEAR = {} ".format(index)
                else:
                    query_year += "OR FA.FISCAL_YEAR = {} ".format(index)
            query_year = '(' + query_year + ')'
        else:
            query_year = '(3 = 3)'

        if df_step:
            for index in df_step:
                if query_step == '':
                    query_step = "FA.STEP = '{}' ".format(index)
                else:
                    query_step += "OR FA.STEP = '{}' ".format(index)
            query_step = '(' + query_step + ')'
        else:
            query_step = '(4 = 4)'

        if df_user:
            for index in df_user:
                if query_user == '':
                    query_user = "FA.USER = '{}' ".format(index)
                else:
                    query_user += "OR FA.USER = '{}' ".format(index)
            query_user = '(' + query_user + ')'
        else:
            query_user = '(5 = 5)'

        self.cx.execute("""
                            DELETE FROM FUNDING_AMOUNT_UPLOAD AS FA
                            USING FUNDING_LINE AS FL WHERE FA.FUNDING_LINE_ID = FL.ID                                  
                            AND {}                         
                        """.format(query_org + ' AND ' +
                                   query_name + ' AND ' +
                                   query_year + ' AND ' +
                                   query_step + ' AND ' +
                                   query_user))
        self.connect.commit()

    def insert_funding_amount_upload(self, userid, funding_line_id,
                                     fiscal_year, step, amount, amount_type, source_url, note):
        self.cx.execute(
            """
                INSERT INTO FUNDING_AMOUNT_UPLOAD 
                (USER, FUNDING_LINE_ID, FISCAL_YEAR, STEP, AMOUNT, AMOUNT_TYPE, SOURCE_URL, NOTE) 
                VALUES ('{}', {}, {}, '{}', {}, '{}', '{}', '{}')
            """.format(userid, funding_line_id, fiscal_year, step, amount, amount_type, source_url, note))
        self.connect.commit()

    def update_funding_amount_upload(self, userid, funding_line_id, fiscal_year, step, amount_type,
                                     new_fiscal_year, new_step, new_amount, new_amount_type, new_source_url, new_note):
        self.cx.execute(
            """
                UPDATE FUNDING_AMOUNT_UPLOAD SET 
                FISCAL_YEAR = {}, 
                STEP = '{}', 
                AMOUNT = {}, 
                AMOUNT_TYPE = '{}',
                SOURCE_URL = '{}',
                NOTE = '{}' 
                WHERE USER = '{}' 
                AND FUNDING_LINE_ID = {} 
                AND FISCAL_YEAR = {} 
                AND STEP = '{}' 
                AND AMOUNT_TYPE = '{}'
            """.format(new_fiscal_year, new_step, new_amount, new_amount_type, new_source_url, new_note,
                       userid, funding_line_id, fiscal_year, step, amount_type))

        self.connect.commit()
        data = self.cx.fetchall()
        return data
