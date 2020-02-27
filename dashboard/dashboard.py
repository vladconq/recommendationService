import dash_html_components as html
import dash_core_components as dcc

custom_layout = html.Div([
    html.Div([
        html.H2('COMPANY NAME'),
    ], className='header1'),

    html.Div([
        html.Div('recommendation system'),
    ], className='header2'),

    html.Div([
        html.Div([
            html.H5('Find recommended products for the client:'),
            html.Div([
                dcc.Input(id='input1', type='text', value='00348f8f-cc3c-11e6-8932-3cd92b037e6c',
                          className='seven columns'),
                html.Button('Submit', id='button1', className='five columns button'),
            ], className='inputBlock'),
            html.Div(id='client-info')
        ], className='leftBlock'),

        html.Div([
            html.H5('Find out the TOP products to promote:'),
            html.Div([
                dcc.Input(id='input2', type='number', value='20',
                          className='two columns'),
                html.Button('Submit', id='button2', className='ten columns button'),
            ], className='inputBlock'),
        ], className='rightBlock')
    ], className='mainBlock'),

    html.Div([
        html.Div([
            html.Div(id='output1')
        ], className='leftBlock2'),
        html.Div([
            html.Div(id='output2')
        ], className='rightBlock2')
    ], className='mainBlock2'),

    html.Div(id='alert', style={'display': 'none'}),
])



