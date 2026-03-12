"""
Plotly visualization engine - generates interactive charts.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional, List
from visualizations.graph_types import GraphType, GraphConfig, GraphStyle


class PlotlyEngine:
    """Generate interactive Plotly visualizations."""
    
    def __init__(self):
        self.color_schemes = {
            'plotly': px.colors.qualitative.Plotly,
            'viridis': px.colors.sequential.Viridis,
            'blues': px.colors.sequential.Blues,
            'categorical': px.colors.qualitative.Safe
        }
    
    def generate(
        self,
        df: pd.DataFrame,
        config: GraphConfig
    ) -> Dict[str, Any]:
        """
        Generate graph based on configuration.
        
        Returns:
            Dict with 'html' (interactive HTML) and 'figure' (Plotly figure JSON)
        """
        if config.graph_type == GraphType.BAR:
            fig = self._create_bar_chart(df, config)
        elif config.graph_type == GraphType.LINE:
            fig = self._create_line_graph(df, config)
        elif config.graph_type == GraphType.SCATTER:
            fig = self._create_scatter_plot(df, config)
        elif config.graph_type == GraphType.PIE:
            fig = self._create_pie_chart(df, config)
        elif config.graph_type == GraphType.HISTOGRAM:
            fig = self._create_histogram(df, config)
        elif config.graph_type == GraphType.BOX:
            fig = self._create_box_plot(df, config)
        elif config.graph_type == GraphType.HEATMAP:
            fig = self._create_heatmap(df, config)
        else:
            raise ValueError(f"Unsupported graph type: {config.graph_type}")
        
        # Apply common styling
        fig = self._apply_styling(fig, config.style)
        
        return {
            'html': fig.to_html(include_plotlyjs=True, full_html=True),
            'figure': fig.to_json(),
            'type': config.graph_type.value
        }
    
    def _create_bar_chart(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create bar chart."""
        if config.color_by:
            fig = px.bar(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_by,
                orientation=config.orientation,
                title=config.style.title
            )
        else:
            fig = go.Figure(data=[
                go.Bar(
                    x=df[config.x_column],
                    y=df[config.y_column] if config.y_column else None,
                    orientation=config.orientation,
                    text=df[config.y_column] if config.show_values and config.y_column else None,
                    textposition='auto'
                )
            ])
        
        return fig
    
    def _create_line_graph(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create line graph."""
        if config.color_by:
            # Multiple lines grouped by color_by column
            fig = px.line(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_by,
                title=config.style.title,
                markers=True
            )
        else:
            fig = go.Figure(data=[
                go.Scatter(
                    x=df[config.x_column],
                    y=df[config.y_column],
                    mode='lines+markers',
                    name=config.y_column
                )
            ])
        
        return fig
    
    def _create_scatter_plot(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create scatter plot."""
        scatter_args = {
            'x': df[config.x_column],
            'y': df[config.y_column],
            'title': config.style.title
        }
        
        if config.color_by:
            scatter_args['color'] = df[config.color_by]
        
        if config.size_by:
            scatter_args['size'] = df[config.size_by]
        
        fig = px.scatter(df, **scatter_args)
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create pie chart."""
        fig = go.Figure(data=[
            go.Pie(
                labels=df[config.x_column],
                values=df[config.y_column] if config.y_column else None,
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )
        ])
        
        return fig
    
    def _create_histogram(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create histogram."""
        fig = px.histogram(
            df,
            x=config.x_column,
            nbins=30,
            title=config.style.title
        )
        
        return fig
    
    def _create_box_plot(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create box plot."""
        if config.color_by:
            fig = px.box(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_by,
                title=config.style.title
            )
        else:
            fig = go.Figure(data=[
                go.Box(
                    y=df[config.y_column] if config.y_column else df[config.x_column],
                    name=config.y_column or config.x_column
                )
            ])
        
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, config: GraphConfig) -> go.Figure:
        """Create heatmap (correlation matrix or pivot table)."""
        # If data is numeric, create correlation heatmap
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=[
                go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale=config.style.color_scheme
                )
            ])
        else:
            # Pivot table heatmap
            fig = px.density_heatmap(
                df,
                x=config.x_column,
                y=config.y_column,
                title=config.style.title
            )
        
        return fig
    
    def _apply_styling(self, fig: go.Figure, style: GraphStyle) -> go.Figure:
        """Apply styling configuration to figure."""
        layout_updates = {
            'template': style.template,
            'showlegend': style.show_legend,
            'hovermode': 'closest' if style.show_hover else False
        }
        
        if style.title:
            layout_updates['title'] = {
                'text': style.title,
                'font': {'size': style.title_font_size}
            }
        
        if style.x_label:
            layout_updates['xaxis_title'] = style.x_label
        
        if style.y_label:
            layout_updates['yaxis_title'] = style.y_label
        
        if style.width:
            layout_updates['width'] = style.width
        
        if style.height:
            layout_updates['height'] = style.height
        
        # Grid configuration
        if style.show_grid:
            layout_updates['xaxis'] = {'showgrid': True, 'gridcolor': 'lightgray'}
            layout_updates['yaxis'] = {'showgrid': True, 'gridcolor': 'lightgray'}
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    def export_static_image(
        self,
        fig: go.Figure,
        filename: str,
        format: str = 'png',
        width: int = 1200,
        height: int = 800
    ):
        """
        Export figure as static image.
        Requires kaleido package.
        """
        fig.write_image(
            filename,
            format=format,
            width=width,
            height=height
        )
