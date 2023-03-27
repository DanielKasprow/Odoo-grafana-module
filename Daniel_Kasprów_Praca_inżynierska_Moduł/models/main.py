import requests
import psycopg2
import datetime

from odoo import models, api
from odoo.http import request


def database_connection():
    """
    Funcja zwracająca dane do polączenia się z bazą danych

    Parameters:
    -----
    connection: object
        Objekt, który umożliwia połączenie z bazą danych

    Return
    ------
    connection: object
        Objekt, który umożliwia połączenie z bazą danych
    """
    connection = psycopg2.connect(user="daniel",
                                  password="3D4g0wwrL43UMPp7",
                                  host="172.17.0.2",
                                  port="5432",
                                  database="statistics_to_grafana")
    return connection


def generate_snapshot_key(dashboard):
    """
    Funcja sprawdzająca czy logi dla Grafana zostały dzisiaj zaaktualizowane

    Parameters:
    -----
    url: Str
        Tekst zawierający link do strony Grafana

    headers: list of str
        Lista zawierająca dane potrzebne do połączenia z Grafana

    data: object
        Object zawierające wszystkie dane do utworzenia wykresu

    resp: object
=           Object wygenerowanego wykresu

    data_resp: list
        Dane wykresu

    snapshot_key: str
        Tekst zawierający klucz snapshot do Grafana
    Return
    ------
    snapshot_key: str
        Tekst zawierający klucz snapshot do Grafana
    """
    url = "http://172.17.0.3:3000/api/snapshots"

    headers = {
        "Authorization": "Bearer eyJrIjoiRkZFVzhHMDhMSnV4b1ZjMEwyZHVzUUFPZ0xadHU3OGYiLCJuIjoia2V5IiwiaWQiOjF9",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {"dashboard": dashboard, "expires": 600}

    resp = requests.post(url, verify=False, headers=headers, json=data)

    data_resp = resp.json()
    snapshot_key = data_resp["key"]

    resp.close()
    return snapshot_key


# definiowanie modelu Odoo
class GrafanaModel(models.Model):
    _name = "grafana.snapshots"

    @api.model
    def checking_last_update_log_for_grafana(self):
        """
        Funcja sprawdzająca czy logi dla Grafana zostały dzisiaj zaaktualizowane

        Parameters:
        -----
        not_current: str
            Zmienna logiczna w postaci tekstowej zwracająca czy logi były aktualizowane tego dnia

        connection: object
            Objekt, który umożliwia połączenie z bazą danych

        curson: object
            Connection.cursor() wykonuje zapytanie do bazy danych bez jej aktualizowania

        last_update: list of tuple
            lista dwuwymiarowa zamierająca jedną zmienną z datą ostatniej aktualizacji
        Return
        ------
        not_current: str
            Zmienna logiczna w postaci tekstowej zwracająca czy logi były aktualizowane tego dnia

        """
        not_current = "true"

        connection = database_connection()
        cursor = connection.cursor()

        try:
            select = "SELECT * from  last_date_updated_statistics_to_grafana"
            cursor.execute(select)
            last_update = cursor.fetchall()
            last_update = last_update[0][1]
        except:
            last_update = "dont exists"

        if last_update == datetime.date.today():
            not_current = "false"

        cursor.close()

        return not_current

    @api.model
    def preparing_logs_for_grafana(self):
        """
        Funcja przygotowująca logi do Grafany do bazy danych

        Parameters:
        ------
        connection: object
            Objekt, który umożliwia połączenie z bazą danych

        curson: object
            Connection.cursor() wykonuje zapytanie do bazy danych bez jej aktualizowania

        select: str
            Tekst zawierający zapytanie do bazy danych

        lists_of_logs: list of tuple
            lista logów do przygotowania dla Grafana

        ip_connect:tuple
            Krotka logu
        """
        connection = database_connection()
        cursor = connection.cursor()

        # aktualizacja daty ostatniej aktualizacji logów do wykresów
        select = "CREATE TABLE IF NOT EXISTS last_date_updated_statistics_to_grafana(id SERIAL PRIMARY KEY, last_update DATE)"
        cursor.execute(select)
        connection.commit()

        select = " DELETE FROM last_date_updated_statistics_to_grafana"
        cursor.execute(select)
        connection.commit()

        select = " INSERT INTO last_date_updated_statistics_to_grafana(last_update) VALUES(\'" + str(
            datetime.date.today()) + "\')"
        cursor.execute(select)
        connection.commit()

        # Tworzenie tabeli jeśli nie istnieje
        select = "CREATE TABLE IF NOT EXISTS prepared_statistics(id SERIAL PRIMARY KEY, start_date DATE, " \
                 "start_time TIME, counted_statistics bigint, counted_statistics_unique bigint, server_name varchar, stream_name varchar, sgroup_name varchar)"
        cursor.execute(select)
        connection.commit()

        # Czyszczenie tabeli z poprzednich wyników
        select = " DELETE FROM prepared_statistics"
        cursor.execute(select)
        connection.commit()

        # Wczytywanie logów
        select = "SELECT start_date, extract(hour from start_time) as hour_time, count(client_ip), count(distinct client_ip), server_name, stream_name, sgroup_name " \
                 "from session " \
                 "inner join channel on channel.channel_id = session.channel_id " \
                 "LEFT OUTER join streaming_group_channel on channel.channel_id = streaming_group_channel.channel_id " \
                 "LEFT OUTER join streaming_group on streaming_group_channel.sgroup_id = streaming_group.sgroup_id " \
                 "where listening_time_id = 8 " \
                 "GROUP BY start_date, hour_time, stream_name, server_name, sgroup_name"

        cursor.execute(select)
        lists_of_logs = cursor.fetchall()

        # Przerobienie logów do Grafana
        for ip_connect in lists_of_logs:
            # Jeśli sgroup_name nie jest Null
            if ip_connect[6] != None:
                select = "INSERT INTO prepared_statistics (start_date, start_time, counted_statistics, counted_statistics_unique, server_name, stream_name, sgroup_name) " \
                         "VALUES ('" + str(ip_connect[0]) + "', time '" + str(int(ip_connect[1])) + ":00' , " + str(
                    ip_connect[2]) + "," + str(ip_connect[3]) + ",'" + str(ip_connect[4]) + "','" + str(
                    ip_connect[5]) + "','" + str(ip_connect[6]) + "')"
            else:
                select = "INSERT INTO prepared_statistics (start_date, start_time, counted_statistics, counted_statistics_unique, server_name, stream_name) " \
                         "VALUES ('" + str(ip_connect[0]) + "', time '" + str(int(ip_connect[1])) + ":00' , " + str(
                    ip_connect[2]) + "," + str(ip_connect[3]) + ",'" + str(ip_connect[4]) + "','" + str(
                    ip_connect[5]) + "')"

            cursor.execute(select)
            connection.commit()
        cursor.close()

    @api.model
    def get_snapshot_iframe(self, from_date, to_date, type_of_report, sql_where):
        """
        Funcja sprawdzająca czy logi dla Grafana zostały dzisiaj zaaktualizowane

        Parameters:
        -----
        fromData: Str
            Tekst zawierający Datę początkoœą okres wykresu

        toData: Str
            Tekst zawierający Datę kończącą okres wykresu

        type_of_report : str
            Tekst zawierający typ wykresu

        sql_where : str
            Tekst zawierający ograniczenia zapytania do bazy danych

        dashboard:
            Zmienna zawierająca zmienne tworzenia wykresów do Grafana


        sql_query : str
            Tekst zawierający zapytanie do bazy danych

        Return
        ------
        snapshot_key: str
            Tekst zawierający klucz snapshot do Grafana
        """

        # Jeśli typ raportu ustawiony na dzienny
        if type_of_report == "Daily":
            sql_query = "SELECT start_date," \
                        "sum(case when " + sql_where + " then counted_statistics end) as all_Connections," \
                                                       "sum(case when " + sql_where + " then counted_statistics_unique end) as Unique_Connections " \
                                                                                      "from prepared_statistics " \
                                                                                      "where start_date BETWEEN \'" + from_date + "\' and \'" + to_date + "\'\nGROUP BY start_date;"

        # Jeśli typ raportu ustawiony na godzinny
        else:
            sql_query = "SELECT start_date + start_time," \
                        "sum(case when " + sql_where + " then counted_statistics end) as all_Connections," \
                                                       "sum(case when " + sql_where + " then counted_statistics_unique end) as Unique_Connections " \
                                                                                      "from prepared_statistics " \
                                                                                      "where start_date BETWEEN \'" + from_date + "\' and \'" + to_date + "\'\nGROUP BY start_date + start_time;"

        dashboard = {
            "id": 5,
            "uid": None,
            "title": "Wykres",
            "tags": ["templated"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "25s",
            "editable": False,
            "panels": [
                {
                    "datasource": {
                        "type": "postgres",
                        "uid": "BCe5rXp4k"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "custom": {
                                "axisCenteredZero": False,
                                "axisColorMode": "text",
                                "axisLabel": "",
                                "axisPlacement": "auto",
                                "fillOpacity": 80,
                                "gradientMode": "none",
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "viz": False
                                },
                                "lineWidth": 1,
                                "scaleDistribution": {
                                    "type": "linear"
                                },
                                "thresholdsStyle": {
                                    "mode": "off"
                                }
                            },
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "color": "green",
                                        "value": None
                                    },
                                    {
                                        "color": "red",
                                        "value": 80
                                    }
                                ]
                            }
                        },
                        "overrides": []
                    },
                    "gridPos": {
                        "h": 9,
                        "w": 12,
                        "x": 0,
                        "y": 0
                    },
                    "id": 2,
                    "options": {
                        "barRadius": 0,
                        "barWidth": 0.91,
                        "groupWidth": 0.8,
                        "legend": {
                            "calcs": [],
                            "displayMode": "list",
                            "placement": "bottom",
                            "showLegend": True
                        },
                        "orientation": "auto",
                        "showValue": "auto",
                        "stacking": "none",
                        "tooltip": {
                            "mode": "single",
                            "sort": "none"
                        },
                        "xTickLabelRotation": 0,
                        "xTickLabelSpacing": 100
                    },
                    "targets": [
                        {
                            "datasource": {
                                "type": "postgres",
                                "uid": "BCe5rXp4k"
                            },
                            "editorMode": "code",
                            "format": "table",
                            "rawQuery": True,
                            "rawSql": sql_query,
                            "refId": "A",
                            "sql": {
                                "columns": [
                                    {
                                        "name": "COUNT",
                                        "parameters": [
                                            {
                                                "name": "server_name",
                                                "type": "functionParameter"
                                            }
                                        ],
                                        "type": "function"
                                    },
                                    {
                                        "parameters": [
                                            {
                                                "name": "event_date",
                                                "type": "functionParameter"
                                            }
                                        ],
                                        "type": "function"
                                    }
                                ],
                                "groupBy": [
                                    {
                                        "property": {
                                            "name": "event_date",
                                            "type": "string"
                                        },
                                        "type": "groupBy"
                                    }
                                ],
                                "limit": 50
                            },
                            "table": "raw_event"
                        }
                    ],
                    "title": "",
                    "type": "barchart"
                }
            ],
        }
        snapshot_key = generate_snapshot_key(dashboard)

        return snapshot_key

    @api.model
    def get_sql_query(self, sql_query):
        """
        Funcja zwracająca wynik zapytania do bazy danych

        Parameters:
        -----
        connection: object
            Objekt, który umożliwia połączenie z bazą danych

        curson: object
            Connection.cursor() wykonuje zapytanie do bazy danych bez jej aktualizowania

        sql_query: str
            Tekst zawierający zapytanie do bazy danych

        lists: list of tuple
            Wynik zapytania do bazy danych

        Return
        ------
        lists: list of tuple
            Wynik zapytania do bazy danych
        """
        connection = database_connection()
        cursor = connection.cursor()

        cursor.execute(sql_query)
        lists = cursor.fetchall()
        cursor.close()

        return lists
