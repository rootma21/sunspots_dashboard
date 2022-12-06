from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from copy import deepcopy

# https address of realtime sun img
SUN_IMG_PATH = 'https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg'


def load_ss_data(fname, **kwargs):
    """ loads sunspot csv data into df """
    # read data
    col_names = kwargs.get('col_names', ['Year', 'Month', 'FracDate',
                                         'MM Sunspot Number', 'MM_SD',
                                         'NumObservations', 'indicator'])
    sep = kwargs.get('sep', ',')
    df = pd.read_csv(fname, sep=sep, names=col_names, header=None)
    return df


def get_yr_range(df, yr_col='Year'):
    """ get list of all years in data """
    yr_range = df[yr_col].unique()

    return yr_range


def rolling(df):
    pass


def main():
    # create app
    app = Dash(__name__)

    # read data
    col_names = ['Year', 'Month', 'FracDate',
                 'MM Sunspot Number', 'MM_SD',
                 'NumObservations', 'indicator']
    df_mm = pd.read_csv('SN_m_tot_V2.0.csv', sep=';',
                        names=col_names, header=None)

    # get list of years
    yr_range = df_mm.Year.unique()

    # LAYOUT
    app.layout = html.Div([

        html.H1('Historical Sunspot Activity'),
        # graph 1 - Historical Sunspot Activity over yr range
        dcc.Graph(id='hist_ss_graph', style={
                  'width': '100vw', 'height': '90vh'}),

        # year range sliders for historical graph
        html.P('Select Year Range: '),
        dcc.RangeSlider(id='yr_range', min=min(yr_range),
                        max=max(yr_range), step=5,
                        marks={1750: '1750',
                               1800: '1800',
                               1850: '1850',
                               1900: '1900',
                               1950: '1950',
                               2000: '2000',
                               },
                        value=[1900, 2000]),
        # smoothed data line (avg over observ period)
        html.P('Smoothed Data Observation Period: '),
        dcc.Slider(id='smooth_period', min=0, max=24, step=1, value=5),

        # graph 2 - Variability of Sunspot Cycle
        html.H2('Variability of Sunspot Cycle'),
        html.P('Select Length of Cycle (in Years)'),
        dcc.Slider(id='cycle_len', min=1, max=15, step=1, value=11),
        dcc.Graph(id='ss_var_graph'),

        # Image of the Sun
        html.H4('The Sun'),
        html.Img(src=SUN_IMG_PATH),
    ], style={'textAlign': 'center', 'marginBottom': 25, 'marginTop': 25, 'marginLeft': 50, 'marginRight': 50})

    # callback for historical data of monthly mean sunspots
    @app.callback(
        Output('hist_ss_graph', 'figure'),
        Input('yr_range', 'value'),
        Input('smooth_period', 'value'),
    )
    def update_hist_ss_graph(yr_range, smooth_period):
        """ updates historical ss graph as year range changes """

        # make plot ss_df
        hist_ss_df = deepcopy(df_mm.loc[(df_mm.Year >= yr_range[0])
                                        & (df_mm.Year <= yr_range[1])])

        # smooth df here
        hist_ss_df['rolling_mm_ss_num'] = deepcopy(hist_ss_df['MM Sunspot Number'].rolling(window=smooth_period, min_periods=1,
                                                                                           method='single').mean())

        fig_hist = px.scatter(
            hist_ss_df, x='Year', y='MM Sunspot Number', title='Monthly Mean Sunspot Number')
        fig_hist.update_traces(line=dict(color='rgba(245,40,145, 0.8)'))

        fig_smoothed = px.line(
            hist_ss_df, x='Year', y='rolling_mm_ss_num', title='Monthly Mean Sunspot Number')
        fig_ss = go.Figure(data=fig_hist.data + fig_smoothed.data)

        return fig_ss

    @app.callback(
        Output('ss_var_graph', 'figure'),
        Input('cycle_len', 'value')
    )
    def update_ss_var_graph(cycle_len):
        """ updates variability of the sunspot cycle graph """

        # make ss_var_df
        df_mm['cycle_mod'] = df_mm['FracDate'] % cycle_len

        # plot
        ss_var_fig = px.scatter(df_mm, x='cycle_mod', y='MM Sunspot Number')
        return ss_var_fig

    app.run_server(debug=False)


if __name__ == '__main__':
    main()
