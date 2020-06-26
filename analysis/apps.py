from .laps import create_layout, get_selectors,get_uploader,App, get_selectors,plot_track,create_trajectory ,create_scales, create_axes

from bqplot import Tooltip ,Figure,Scatter,LinearScale,ColorAxis,ColorScale,Axis
import ipywidgets
import numpy

def create_new_reward_app(get_files_paths, logs_base_path, get_df, track, get_episode, aggregate_episode_reward, NewReward, df_to_params):
    
    file_selector, file_uploader = get_uploader(get_files_paths, logs_base_path)

    appModel = App(get_df) 
    appModel.file = file_selector.value
    ipywidgets.link((appModel, 'file'), (file_selector, 'value'))
    buttonsLayout, buttons = get_buttons()

    ep = aggregate_episode_reward(get_episode(appModel.df, 0), NewReward, df_to_params, track, 'new_reward')
    track_plot, rw_plot = create_figures(ep, track, buttons)
    fig = ipywidgets.HBox([track_plot, rw_plot])
    
    episodes = numpy.unique(appModel.df.episode.values)
    columns = ep.select_dtypes('number').columns.values
    
    col, dd, sl = get_selectors(columns, episodes)
    update_selectors(sl, appModel, track, fig,  get_episode, create_figures, buttons, aggregate_episode_reward, NewReward, df_to_params)
    
    appModel.dd, appModel.sl = dd, sl
    
    app = create_layout([file_selector, file_uploader], [dd, sl, buttonsLayout], fig )
    return app


def get_buttons():
    rw_btn = ipywidgets.ToggleButton(description='reward',value=True)
    nrw_btn = ipywidgets.ToggleButton(description='new_reward',value=False)
    buttonsLayout = ipywidgets.VBox([
        ipywidgets.HTML('Show on track'),
        ipywidgets.HBox([rw_btn,nrw_btn])
    ])
    return buttonsLayout, [rw_btn,nrw_btn]


def create_scatter_plot(df, color_scale):
    fig_scales = create_scales()
    fig_scales['color'] = color_scale
    tooltip = Tooltip(fields=['x', 'y' ], formats=['.2f', '.2f','s'], labels=['step','reward'] )
    newrw_tooltip = Tooltip(fields=['x', 'y' ], formats=['.2f', '.2f','s'], labels=['step','new_reward'] )
    rw = Scatter(x=df.step,
                 y=df.reward,
                 color=df.reward,
                 scales=fig_scales, 
                 default_size=20, 
                 tooltip=tooltip, labels=['reward'],
                 display_legend=True)
    nrw = Scatter(x=df.step,
                  y=df.new_reward,
                  color=df.new_reward,
                  scales=fig_scales, default_size=20, 
                  tooltip=newrw_tooltip,
                  labels=['new_reward'],
                  display_legend=True,
                  marker='cross')
    ax,ay,ac = create_axes(fig_scales)
    ax.label, ay.label = 'step','reward'
    return Figure(marks = [rw,nrw],axes = [ax,ay,ac])

def update_tray(df,tray, rw_col_name,btn):
    ln, sc = tray
    sc.color = df[rw_col_name]
    sc.tooltip.labels = ['x', 'y', rw_col_name]
    ipywidgets.link((ln,'visible'),(sc,'visible'))
    ipywidgets.link((ln,'visible'),(btn,'value'))

def create_track_plot(df, track, scales,buttons):
    rw_tray = create_trajectory(df.x, df.y, scales)
    nrw_tray = create_trajectory(df.x, df.y, scales)
    rw_btn, nrw_btn = buttons
    
    update_tray(df, rw_tray,'reward',rw_btn)
    update_tray(df, nrw_tray,'new_reward',nrw_btn)
    rw_btn.value, nrw_btn.value = True, False
    track_plot = plot_track(track, scales)
    track_plot.marks = track_plot.marks + rw_tray + nrw_tray
    return track_plot

def create_figures(df,track,buttons):
    scales = create_scales()
    track_plot = create_track_plot(df, track, scales, buttons)
    rw_plot = create_scatter_plot(df, scales['color'])
    return track_plot, rw_plot

def update_selectors(sl,appModel, track, fig,get_episode, create_figures,buttons, aggregate_episode_reward, NewReward, df_to_params):
    def select_episode(change):
        df = appModel.df
        episode = change['new']
        ep = aggregate_episode_reward(get_episode(df, episode), NewReward, df_to_params, track, 'new_reward')
        fig.children = create_figures(ep, track,buttons) 
        
    sl.observe(select_episode,names='value')