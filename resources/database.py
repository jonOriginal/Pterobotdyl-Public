import sqlite3


class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.init_connection()

    def init_connection(self):
        try:
            self.connection.execute(
                "CREATE TABLE server (guild_id VARCHAR(255), channel_id VARCHAR(255), server_id VARCHAR(255), "
                "api_key VARCHAR(255))")
        except sqlite3.DatabaseError:
            pass
        finally:
            self.connection.commit()

    def __contains__(self, guild_id):
        try:
            with self.connection:
                cursor = self.connection.execute("SELECT * FROM server WHERE guild_id = '%s'; --" % (guild_id, ))
                result = cursor.fetchone()
                if result:
                    return True
                else:
                    return False

        except sqlite3.Error as err:
            print(f"Something went wrong: {err}")

    def __getitem__(self, guild_id):
        try:
            cursor = self.connection.execute("SELECT * FROM server WHERE guild_id = '%s'; --" % (guild_id, ))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as err:
            print(f"Something went wrong: {err}")

    def __setitem__(self, guild_id, value):
        try:
            command = "INSERT INTO server (guild_id, channel_id, server_id, api_key)" \
                      " VALUES ('%s','%s','%s','%s')" % (guild_id, value['channel'], value['server_id'], value['api_key'])
            self.connection.execute(command)
            self.connection.commit()

        except sqlite3.Error as err:
            print(f"Something went wrong: {err}")

    def __delitem__(self, guild_id):
        try:
            self.connection.execute("DELETE FROM server WHERE guild_id = '%s';" % (guild_id, ))
            self.connection.commit()
        except sqlite3.Error as err:
            print(f"Something went wrong: {err}")
