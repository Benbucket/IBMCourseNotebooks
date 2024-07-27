# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = [{'label': 'All Sites', 'value': 'All Sites'}]
all_launch_sites = spacex_df['Launch Site'].unique().tolist()
for launch_site in all_launch_sites:
    launch_sites.append({'label': launch_site, 'value': launch_site})

booster_versions = [{'label': 'All Boosters', 'value': 'All Boosters'}]
booster_versions.extend(
    [{'label': version, 'value': version} for version in spacex_df['Booster Version Category'].unique()]
)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=launch_sites,
            placeholder='Select a Launch Site here',
            searchable=True,
            clearable=False,
            value='All Sites'
        ),
    ]),
    html.Br(),

    html.Div([
        dcc.Dropdown(
            id='booster-dropdown',
            options=booster_versions,
            placeholder='Select a Booster Version Category',
            searchable=True,
            clearable=False,
            value='All Boosters'
        ),
    ]),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    html.Div([
        dcc.RangeSlider(
            id='payload_slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: {'label': f'{i} Kg'} for i in range(0, 10001, 1000)},
            value=[min_payload, max_payload]
        ),
    ]),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='booster-dropdown', component_property='value')]
)
def update_piegraph(site_dropdown, booster_dropdown):
    if booster_dropdown != 'All Boosters':
        data = spacex_df[spacex_df['Booster Version Category'] == booster_dropdown]
    else:
        data = spacex_df

    if site_dropdown == 'All Sites':
        data = data[data['class'] == 1]
        fig = px.pie(
            data,
            names='Launch Site',
            title='Total Success Launches by All Sites',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
    else:
        data = data[data['Launch Site'] == site_dropdown]
        fig = px.pie(
            data,
            names='class',
            title=f'Total Success Launches for Site &#8608; {site_dropdown}',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload_slider', component_property='value'),
     Input(component_id='booster-dropdown', component_property='value')]
)
def update_scattergraph(site_dropdown, payload_slider, booster_dropdown):
    low, high = payload_slider
    if booster_dropdown != 'All Boosters':
        data = spacex_df[spacex_df['Booster Version Category'] == booster_dropdown]
    else:
        data = spacex_df

    if site_dropdown != 'All Sites':
        data = data[data['Launch Site'] == site_dropdown]
    
    inrange = (data['Payload Mass (kg)'] > low) & (data['Payload Mass (kg)'] < high)
    fig = px.scatter(
        data[inrange],
        x="Payload Mass (kg)",
        y="class",
        title=f'Correlation Between Payload and Success for Site &#8608; {site_dropdown}',
        color="Booster Version Category",
        size='Payload Mass (kg)',
        hover_data=['Payload Mass (kg)']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
