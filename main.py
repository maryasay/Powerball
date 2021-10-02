# Import required packages
import pandas as pd
import plotly.express as px
import dash
from dash import html
from dash import dcc
import numpy as np
from dash.dependencies import Input, Output

# Read the data into pandas dataframe
df_PB = pd.read_csv('https://www.texaslottery.com/export/sites/lottery/Games/Powerball/Winning_Numbers/powerball.csv',
                    header=None, skiprows=range(592))

# tidy up the column names
df_PB.drop([0], axis=1, inplace=True)
df_PB.rename(columns={1: 'Month', 2: 'Day', 3: 'Year', 4: 'ball1', 5: 'ball2',
                      6: 'ball3', 7: 'ball4', 8: 'ball5', 9: 'Pball', 10: 'Multiplier'}, inplace=True)

# Create drawDate: concatenate date columns into drawDate
df_PB['drawDate'] = pd.to_datetime({'year': df_PB['Year'],
                                    'month': df_PB['Month'],
                                    'day': df_PB['Day']}, format='%m%d%Y')

# Drop Month Day and Year Columns
df_PB.drop(['Month', 'Day', 'Year'], axis=1, inplace=True)
df_PB = df_PB.sort_values(['drawDate'], ascending=False)

def ComputeDraw():
    global df
    df = df.apply(pd.value_counts)
    df['Total'] = df.sum(axis=1)
    df = df.reset_index()
    df = df.sort_values(['Total'], ascending=False)
    df.rename(columns={'index': 'Number'}, inplace=True)
    df = df.astype({'Number': str})
    return df


def PCompute():
    global P_df
    P_df = P_df.reset_index()
    P_df.drop('index', axis=1, inplace=True)
    P_df = P_df.apply(pd.value_counts)
    P_df = P_df.reset_index()
    P_df.rename(columns={'index': 'Powerball', 'Pball': 'Frequency'}, inplace=True)
    return P_df


# Create Items to plot
# find the total frequency of each number in all draws
All_Ball = df_PB[['ball1', 'ball2', 'ball3', 'ball4', 'ball5']]
All_Ball = All_Ball.apply(pd.value_counts)
All_Ball['Total'] = All_Ball.sum(axis=1)
All_Ball['Number'] = np.arange(len(All_Ball)) + 1
All_Ball = All_Ball.astype({'Number': str})
All_Ball = All_Ball.sort_values(['Total'], ascending=False)

# Compute All Powerball
df_PB = df_PB.astype({'Pball': str})
Pball = df_PB['Pball'].value_counts()
Pball = Pball.reset_index()
Pball.rename(columns={'index': 'Powerball', 'Pball': 'Frequency'}, inplace=True)

# Compute Data for last 20 draws
df = df_PB.iloc[0:20, 0:5]
ComputeDraw()
Twenty_Draw = df

# frequency of each powerball in last 20 draws
P_df = df_PB.iloc[0:20, 5]
PCompute()
P_Twenty = P_df

df = df_PB.iloc[0:50, 0:5]
ComputeDraw()
Ball_Fifty = df

# Compute last 50 Powerballs
P_df = df_PB.iloc[0:50, 5]
PCompute()
P_Fifty = P_df


def unclutter(figure):
    figure.update_traces(texttemplate='%{text:2s}', textposition='outside')
    figure.update_xaxes(title_text="", showgrid=False, showticklabels=False)
    figure.update_yaxes(title_text="", showgrid=False, )
    figure.update_layout(showlegend=False)
    figure.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return figure


# Create a dash application
app = dash.Dash(__name__)

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add description about the graph using HTML P (paragraph) component
# Finally, add graph component.
app.layout = html.Div(children=[html.H1('US Powerball Winning Numbers',
                                        style={'textAlign': 'center', 'color': '#FFFFFF', 'font-size': 40}),
                                html.P('Frequency of Winning Numbers in Past draws',
                                       style={'textAlign': 'center', 'color': '	#0000FF'}),
                                html.Div([
                                    html.H1("Number of Draws: ", style={'margin-right': '2em', 'margin-left': '2em',
                                                                        'font-size': 30, 'textAlign': 'center',
                                                                        'color': '#FFFFFF'})
                                ]),

                                dcc.Dropdown(id='input-choice',
                                             options=[
                                                 {'label': 'Last 20 Draws', 'value': 'OPT1'},
                                                 {'label': 'Last 50 Draws', 'value': 'OPT2'},
                                                 {'label': 'All Past Draws', 'value': 'OPTA'}
                                             ],
                                             style={'margin': 'auto', 'width': '50%', 'padding': '10px',
                                                    'font-size': '20px',
                                                    'text-align-last': 'center', 'color': '	#0000FF'}, value='OPT1'),
                                html.Div([
                                    html.Div([], id='plot-1'),
                                    html.Div([], id='plot-2'),
                                ], style={'display': 'flex'})
                      ])


# add callback decorator
@app.callback([Output(component_id='plot-1', component_property='children'),
               Output(component_id='plot-2', component_property='children')],
              [Input(component_id='input-choice', component_property='value')]
              )
# Function to return graphs
def get_graph(chart):
    if chart == 'OPT1':
        # Number Chart of Winning Numbers in Past 20 Draws
        Twenty_fig = px.bar(Twenty_Draw, x='Total', y='Number', title='Frequency of Numbers', orientation='h',
                            hover_data=['Number', 'Total'], color='Number',
                            labels={'Total': 'Frequency'}, height=2000, text='Total', template="plotly_dark"
                            )
        unclutter(Twenty_fig)

        # Chart of Past 20 PowerBalls
        PTwenty_fig = px.bar(P_Twenty, x='Frequency', y='Powerball', title='Frequency of Powerball Numbers',
                             orientation='h', hover_data=['Powerball', 'Frequency'], color='Powerball', height=600,
                             text='Frequency', template="plotly_dark")
        unclutter(PTwenty_fig)

        # Return dcc.Graph component to the empty division
        return [dcc.Graph(figure=Twenty_fig),
                dcc.Graph(figure=PTwenty_fig)
                ]

    elif chart == 'OPT2':
        # Create graph for past 50 Draws
        Fifty_fig = px.bar(Ball_Fifty, x='Total', y='Number', title='Frequency of Numbers', orientation='h',
                           hover_data=['Number', 'Total'], color='Number', labels={'Total': 'Frequency'}, height=2000,
                           text='Total', template="plotly_dark")
        unclutter(Fifty_fig)

        PFifty_fig = px.bar(P_Fifty, x='Frequency', y='Powerball', title='Frequency of Powerball Numbers',
                            hover_data=['Powerball', 'Frequency'],
                            orientation='h', color='Powerball', height=800, text='Frequency', template="plotly_dark")
        unclutter(PFifty_fig)

        return [dcc.Graph(figure=Fifty_fig),
                dcc.Graph(figure=PFifty_fig)
                ]

    else:
        # Number Chart of all Winning Numbers
        All_fig = px.bar(All_Ball, x='Total', y='Number', title='Frequency of Numbers', orientation='h',
                         hover_data=['Number', 'Total'], color='Number',
                         labels={'Total': 'Frequency'}, height=2000, text='Total', template="plotly_dark")

        unclutter(All_fig)

        # Chart of All Past PowerBalls
        AllP_fig = px.bar(Pball, x='Frequency', y='Powerball', title='Frequency of Powerball Numbers', orientation='h',
                          hover_data=['Powerball', 'Frequency'], color='Powerball', height=800, text='Frequency',
                          template="plotly_dark")
        unclutter(AllP_fig)

        # Return dcc.Graph component to the empty division
        return [dcc.Graph(figure=All_fig),
                dcc.Graph(figure=AllP_fig)
                ]


# Run the application
if __name__ == '__main__':
    app.run_server()
