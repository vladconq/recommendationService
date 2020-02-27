import psycopg2
import dash
import dash_html_components as html
import dash_table
import pandas as pd
import dash_auth

from waitress import serve
from flask import Flask, jsonify, request, abort
from functools import wraps
from dash.dependencies import Input, Output, State

from dashboard import custom_layout

TOKEN = '******'

server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,
                server=server,
                routes_pathname_prefix='/dashboard/',
                external_stylesheets=external_stylesheets)
app.layout = custom_layout

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin1'
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


def require_token(fun):
    @wraps(fun)
    def decorated_function(**kwargs):
        if request.headers.get('token') == TOKEN:
            return fun(**kwargs)
        else:
            abort(401)

    return decorated_function


def get_connection_and_cursor():
    conn = psycopg2.connect(
        host="******",
        user="******",
        dbname="******",
        password="******",
        sslmode="require"
    )
    cur = conn.cursor()

    return conn, cur


@server.route('/client/<uuid:client_id>')
@require_token
def get_recommendations_for_user(client_id):
    recommendations, recommended_items = dict(), list()
    conn, cur = get_connection_and_cursor()

    try:
        cur.execute("SELECT rating, item_id FROM recommendations WHERE client_id='{}'".format(client_id))

        records = cur.fetchall()
        records_sorted = sorted(records, reverse=True)

        [recommended_items.append(item[1]) for item in records_sorted]

        recommendations[str(client_id)] = recommended_items

        return jsonify(recommendations), 200
    finally:
        conn.commit()
        cur.close()
        conn.close()


@server.route('/top/<int:n>')
@require_token
def get_top_n_items(n):
    conn, cur = get_connection_and_cursor()

    try:
        cur.execute("SELECT item_id, client_id FROM top_n LIMIT {}".format(n))

        items_top = cur.fetchall()

        return jsonify(items_top), 200

    finally:
        conn.commit()
        cur.close()
        conn.close()


@app.callback(Output('client-info', 'children'),
              [Input('input1', 'value')])
def get_client_info(client_id):
    conn, cur = get_connection_and_cursor()

    try:
        sql_query = """
        SELECT client_name FROM client
        WHERE client_id = '{}'
        """.format(client_id)

        client_name = pd.read_sql(sql_query, conn)
        client_name = client_name.values[0][0]

        return html.H6('client — "{}"'.format(client_name))
    except Exception:
        return html.H6('client — Unknown')
    finally:
        conn.commit()
        cur.close()
        conn.close()


@app.callback(Output('output1', 'children'),
              [Input('button1', 'n_clicks')],
              [State('input1', 'value')])
def get_client_id(n_clicks, client_id):
    conn, cur = get_connection_and_cursor()

    try:
        sql_query = """
        SELECT product.item_id, item_name, rating FROM recommendations
        LEFT JOIN product ON recommendations.item_id = product.item_id
        WHERE recommendations.client_id = '{}'
        """.format(client_id)

        recommendations = pd.read_sql(sql_query, conn)
        recommendations.sort_values('rating', inplace=True, ascending=False)

        recommendations = recommendations.rename(columns={'item_id': 'Product ID',
                                                          'item_name': 'Product Name',
                                                          'rating': 'Rating'})

        return dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in recommendations.columns],
            data=recommendations.to_dict("rows"),
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(222 230 237)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(222 230 237)',
                'fontWeight': 'bold',
                'border': '0px solid blue'
            },
            style_cell={'font_family': 'sans-serif',
                        'font_size': '14px',
                        'overflow': 'hidden',
                        'height': 'auto',
                        'minWidth': '0px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                        },
            style_data={'border': '0px solid white', 'height': 'auto'},
            style_table={'overflowY': 'auto'},
            style_as_list_view=True,
        )
    except Exception:
        return 'There is no client with client_id: {}'.format(client_id)
    finally:
        conn.commit()
        conn.close()


@app.callback(Output('output2', 'children'),
              [Input('button2', 'n_clicks')],
              [State('input2', 'value')])
def get_client_id(n_clicks, top_n):
    conn, cur = get_connection_and_cursor()

    try:
        sql_query = """
        SELECT product.item_id, item_name, count FROM top_n
        LEFT JOIN product ON top_n.item_id = product.item_id
        """

        top_items = pd.read_sql(sql_query, conn)
        top_items = top_items.sort_values('count', ascending=False)
        top_items = top_items[:int(top_n)]

        top_items = top_items.rename(columns={'item_id': 'Product ID',
                                              'item_name': 'Product Name',
                                              'count': 'Count'})

        return dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in top_items.columns],
            data=top_items.to_dict("rows"),
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(222 230 237)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(222 230 237)',
                'fontWeight': 'bold',
                'border': '0px solid blue'
            },
            style_cell={'font_family': 'sans-serif',
                        'font_size': '14px',
                        'overflow': 'hidden',
                        'height': 'auto',
                        'minWidth': '0px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                        },
            style_data={'border': '0px solid white'},
            style_table={'overflowY': 'auto'},
            style_as_list_view=True,
        )
    finally:
        conn.commit()
        conn.close()


if __name__ == '__main__':
    serve(server, host='0.0.0.0', port=5000)
