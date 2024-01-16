class DbRepo:
    def __init__(self, db_url, password):
        self.connection = None
        self.db_url = db_url
        self.password = password

    def _set_connection(self):
        try:
            connection = psycopg2.connect(dbname='postgres',
                                          user='postgres',
                                          password='postgres',
                                          host="localhost")

            connection.autocommit = True
            self.connection = connection
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
            connection.close()
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")

    def create_user(self):
        pass

    def update_user_by_id(self, user_id, **kwargs):
        pass

    def get_user_by_id(self):
        pass


# 2 tables
# users -> (tg_id, id, name), users_info -> (id, sleep_info, data)