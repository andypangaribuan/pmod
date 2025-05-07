'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''

import psycopg2


class DBX:
    __conn: dict = {}
    __conn_tz: str | None = None

    def __init__(self, name: str, host: str, port: str, usr: str, pwd: str, tz: str):
        self.__conn_tz = tz
        self.__conn = {
            'database': name,
            'host': host,
            'port': port,
            'user': usr,
            'password': pwd,
        }

    def fetches(self, query, vars: list = []) -> tuple[list | None, Exception | None]:
        try:
            with psycopg2.connect(**self.__conn) as conn:
                with conn.cursor() as cur:
                    return self.__fetches(cur, query, vars), None
        except Exception as err:
            return None, err

    def exec(self, query, vars: list = []) -> Exception | None:
        try:
            with psycopg2.connect(**self.__conn) as conn:
                with conn.cursor() as cur:
                    if len(vars) > 0:
                        cur.execute(query, vars)
                    else:
                        cur.execute(query)
        except Exception as err:
            return err

    def __fetches(self, cur: any, query, vars=[]) -> list:
        if self.__conn_tz is not None:
            cur.execute(f"SET TIME ZONE '{self.__conn_tz}';")

        if len(vars) > 0:
            cur.execute(query, vars)
        else:
            cur.execute(query)

        columns = list(cur.description)
        rows = cur.fetchall()
        results = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col.name] = row[i]
            results.append(row_dict)

        return results
