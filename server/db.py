import os
import sqlite3


def db_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, 'users_dev.db')


def save_activity(timestamp, user_sid, user_name, user_display_name, sys_version, user_ip, sys_name):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(f"INSERT INTO activities "
                  f"(timestamp,user_sid,user_name,user_display_name,user_ip,sys_name,sys_version)"
                  f" VALUES "
                  f"('{timestamp}','{user_sid}','{user_name}','{user_display_name}','{user_ip}','{sys_name}','{sys_version}')")
        conn.commit()
        conn.close()
        return True
    except sqlite3.OperationalError as err:
        print(f"Not Save! Error: {err}")
        return False


def get_activity_user_sid(user_sid, limit=50):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(f"SELECT * FROM activities WHERE user_sid = '{user_sid}' LIMIT {limit}")
        data = c.fetchall()
        conn.commit()
        conn.close()
        return data
    except sqlite3.OperationalError as err:
        print(f"Error: {err}")
        return False


def get_activity_user_ip(user_ip, limit=50):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(f"SELECT * FROM activities WHERE user_ip = '{user_ip}' LIMIT {limit}")
        data = c.fetchall()
        conn.commit()
        conn.close()
        return data
    except sqlite3.OperationalError as err:
        print(f"Error: {err}")
        return False


def get_activity_sys_name(sys_name, limit=50):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(f"SELECT * FROM activities WHERE sys_name = '{sys_name}' LIMIT {limit}")
        data = c.fetchall()
        conn.commit()
        conn.close()
        return data
    except sqlite3.OperationalError as err:
        print(f"Error: {err}")
        return False


if __name__ == '__main__':
    pass
