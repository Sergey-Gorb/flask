import sqlite3


class FlDB:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Error getting DB data: " + str(e))
        return []

    def add_user(self, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() AS 'count' FROM users WHERE email Like '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print(f'User with e-mail {email} exist!')
                return False
            self.__cur.execute("INSERT INTO users(NULL, ?, ?)", (email, hpsw))
            self.__db.commit()

        except sqlite3.Error as e:
            print(f'Error {e} add user to database')
            return False

        return True

    def get_user(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False

            return res
        except sqlite3.Error as e:
            print("Error getting DB data: " + str(e))

        return False

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email LIKE '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("User not found")
                return False

            return res
        except sqlite3.Error as e:
            print("Error getting DB data: " + str(e))

        return False
