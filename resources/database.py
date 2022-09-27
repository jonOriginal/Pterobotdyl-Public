import mysql.connector


class Database:
    def __init__(self, config):
        self.config = config

        self.connection = mysql.connector.connect(**config)
        self.cursor = self.connection.cursor(dictionary=True, buffered=True)
        self.init_connection()

    def init_connection(self):
        try:
            self.cursor.execute(
                "CREATE TABLE server (guild_id VARCHAR(255), channel_id VARCHAR(255), server_id VARCHAR(255), "
                "api_key VARCHAR(255))")
        except mysql.connector.Error:
            pass
        finally:
            self.connection.commit()

    def __contains__(self, guild_id):
        try:
            self.cursor.execute(f"SELECT * FROM server WHERE guild_id = '{guild_id}'")
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False

        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")

    def __getitem__(self, guild_id):
        try:
            self.cursor.execute(f"SELECT * FROM server WHERE guild_id = '{guild_id}'")
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")

    def __setitem__(self, guild_id, value):
        try:
            command = f"INSERT INTO server (guild_id,channel_id,server_id,api_key)" \
                      f" VALUES ('{guild_id}','{value['channel']}','{value['server_id']}','{value['api_key']}')"
            self.cursor.execute(command)
            self.connection.commit()

        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")

    def __delitem__(self, guild_id):
        try:
            self.cursor.execute(f"DELETE FROM server WHERE guild_id = '{guild_id}'")
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Something went wrong: {err}")
