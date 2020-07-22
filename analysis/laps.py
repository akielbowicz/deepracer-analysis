import ipywidgets
import pathlib
from traitlets import HasTraits,Instance,link
from traittypes import DataFrame
import numpy
from bqplot import Figure, LinearScale, Scatter, Lines, Axis, Tooltip,ColorScale,ColorAxis


def get_uploader(get_files_paths,logs_base_path):
    file_selector = ipywidgets.Dropdown(options=get_files_paths(logs_base_path),
                                        value=get_files_paths(logs_base_path)[-1][1],
                                        description='file')
    file_uploader = ipywidgets.FileUpload( accept='.log',multiple=True)

    def save_file(change):
        for filename, data in change['new'].items():
            filepath = pathlib.Path(logs_base_path,filename)
            filepath.touch()
            print('Saving new file: ', filepath)
            with open(filepath,'rb+') as f:
                f.write(data['content'])
            print('Saved succesfully')

    def update_filepaths(change):
        old = set(file_selector.options)
        file_selector.options = get_files_paths(logs_base_path)
        new = set(file_selector.options)

    file_uploader.observe(save_file,names='value')
    file_uploader.observe(update_filepaths,names='value')
    return file_selector, file_uploader

def get_selectors(columns,episodes):    
    col = ipywidgets.Dropdown(options=columns,description='column')
    dd = ipywidgets.Dropdown(options=episodes,default_value=0,description='episode')
    sl = ipywidgets.IntSlider(min=min(episodes,default=0), max=max(episodes,default=0), default_value=0)
    
    ipywidgets.link((dd,'value'),(sl,'value'))
    return col,dd,sl

def update_selectors(col,dd,sl,appModel, track_plot, get_episode, create_trajectory, scales):
    def select_episode(change):
        df = appModel.df
        episode = change['new']
        ep = get_episode(df, episode)
        color = ep[col.value]
        trajectory = create_trajectory(ep.x,ep.y,scales)
        trajectory[-1].color = color
        track_plot.marks = track_plot.marks[:-2] + trajectory

    def select_column(change):
        new_column = change['new']
        df = appModel.df
        ep = get_episode(df,sl.value)
        if len(track_plot.marks)>3:
            scatter = track_plot.marks[-1]
            update_scatter(scatter,ep,new_column)

    def update_scatter(scatter,ep,new_column):
        scatter.color = ep[new_column]
        color_scale = scatter.scales['color']

        color_scale.min = float(scatter.color.min(initial=0.0))
        color_scale.max = float(scatter.color.max(initial=1.0)) 
        scatter.tooltip.labels = ['x','y', new_column]  

    col.observe(select_column,names='value')
    sl.observe(select_episode,names='value')


class App(HasTraits):
    df = DataFrame(default_value=None,allow_none=True).tag(sync=True)
    file = Instance(pathlib.Path,allow_none=True,default_value=None)
    
    def __init__(self,df_loader):
        self.observe(self._update_file,names='file')
        self.df_loader = df_loader
        self.dd = ipywidgets.Dropdown()
        self.sl = ipywidgets.IntSlider()
        
    def _update_file(self,change):
        new_file = change['new']
        self.df = self.df_loader(new_file)
        self._update_episodes()
        
    def _update_episodes(self):
        episodes = numpy.unique(self.df.episode.values)
        self.dd.options = episodes
        self.sl.min=min(episodes)
        self.sl.max=max(episodes)

def create_scales():
    return {'x': LinearScale(), 'y': LinearScale(),'color': ColorScale(scheme='YlGnBu'),'size':LinearScale(min=0,max=1)}

def create_trajectory(x,y,scales):
    tooltip = Tooltip(fields=['x', 'y', 'color' ], formats=['.2f', '.2f','s'])
    return [ Lines(x=x, y=y, scales=scales,opacities=[0.1] ), Scatter(x=x, y=y, default_size=10, scales=scales, tooltip=tooltip ) ]

def plot_track(track, scales):
    
    def plot_line(points, scales):
        x,y = points.T
        return Lines(x=x, y=y, scales=scales,colors=['gray'])

    def create_line(track,name,scales):
        points = getattr(track, name)
        return plot_line(points, scales)

    def create_track(track, scales):    
        return [ create_line(track,name,scales)
             for name in ['inner_border', 'outer_border','center_line']]


    marks = create_track(track,scales)  
    axes = create_axes(scales)
    fig = Figure(marks=marks, axes=axes)
    fig.min_aspect_ratio = 1
    fig.max_aspect_ratio = 1
    return fig

def create_axes(scales):
    return [ Axis(scale=scales['x'], label='x'), 
             Axis(scale=scales['y'], orientation='vertical', label='y'),
             ColorAxis(scale=scales['color'], label='', side='right', orientation='vertical') ]

def create_app(get_files_paths, logs_base_path, get_df, track, get_episode):
    
    file_selector, file_uploader = get_uploader(get_files_paths, logs_base_path)

    appModel = App(get_df) 
    appModel.file = file_selector.value
    ipywidgets.link((appModel, 'file'), (file_selector, 'value'))

    scales = create_scales()
    track_plot = plot_track(track, scales)

    columns_and_episodes = initial_info(appModel, track_plot, get_episode, scales)   
        
    col,dd,sl = get_selectors(*columns_and_episodes)
    update_selectors(col, dd, sl, appModel, track_plot, get_episode, create_trajectory, scales)
    
    appModel.dd, appModel.sl = dd, sl
    app = create_layout([file_selector, file_uploader], [dd, sl, col], track_plot)
    return app

def create_layout(file_widgets,selectors,*args):
    return ipywidgets.VBox([ipywidgets.HBox(file_widgets),
                            ipywidgets.HBox(selectors), 
                            *args]) 

def initial_info(appModel,track_plot, get_episode, scales):
    episodes = numpy.unique(appModel.df.episode.values)
    ep = get_episode(appModel.df,0)
    columns = ep.select_dtypes('number').columns.values
    track_plot.marks = track_plot.marks + create_trajectory(ep.x, ep.y, scales)
    return columns,episodes