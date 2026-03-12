"""
Graph generator - orchestrates data processing and visualization.
"""
import pandas as pd
from typing import Dict, Any, Optional, Union, List

from visualizations.data_processor import DataProcessor
from visualizations.plotly_engine import PlotlyEngine
from visualizations.graph_types import GraphType, GraphConfig, GraphStyle, get_default_config


class GraphGenerator:
    """Main graph generation orchestrator."""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.plotly_engine = PlotlyEngine()
    
    def generate_graph(
        self,
        data: Union[List[Dict], Dict, pd.DataFrame, str],
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        graph_type: Optional[str] = None,
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        color_by: Optional[str] = None,
        aggregation: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate graph with intelligent defaults.
        
        Args:
            data: Input data (various formats supported)
            x_column: X-axis column name
            y_column: Y-axis column name
            graph_type: Explicit graph type or None for auto-detection
            title: Graph title
            x_label: X-axis label
            y_label: Y-axis label
            color_by: Column to color by
            aggregation: Aggregation method (mean, sum, count, etc.)
            **kwargs: Additional styling options
        
        Returns:
            Dict with 'html', 'figure', 'type', and 'metadata'
        """
        try:
            # Step 1: Normalize data
            df = self.data_processor.normalize_input(data)
            
            # Step 2: Clean data
            df = self.data_processor.clean_data(df)
            
            # Step 3: Determine columns if not specified
            if not x_column:
                x_column = df.columns[0]
            
            if not y_column and len(df.columns) > 1:
                # Find first numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    y_column = numeric_cols[0]
            
            # Step 4: Auto-detect graph type if not specified
            if not graph_type:
                graph_type = self.data_processor.auto_detect_graph_type(df, x_column, y_column)
            
            graph_type_enum = GraphType(graph_type.lower())
            
            # Step 5: Apply aggregation if specified
            if aggregation and y_column:
                df = self.data_processor.aggregate_for_visualization(
                    df, x_column, y_column, aggregation
                )
            
            # Step 6: Build configuration
            style = GraphStyle(
                title=title or f"{y_column or x_column} by {x_column}",
                x_label=x_label or x_column,
                y_label=y_label or y_column,
                **kwargs
            )
            
            config = GraphConfig(
                graph_type=graph_type_enum,
                x_column=x_column,
                y_column=y_column,
                color_by=color_by,
                aggregation=aggregation,
                style=style
            )
            
            # Step 7: Generate visualization
            result = self.plotly_engine.generate(df, config)
            
            # Step 8: Add metadata
            result['metadata'] = {
                'rows': len(df),
                'columns': list(df.columns),
                'x_column': x_column,
                'y_column': y_column,
                'data_shape': df.shape
            }
            
            # Add statistics if numeric
            if y_column and pd.api.types.is_numeric_dtype(df[y_column]):
                result['statistics'] = self.data_processor.calculate_statistics(df, y_column)
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'type': 'error'
            }
    
    def generate_comparison_chart(
        self,
        data: Union[List[Dict], Dict, pd.DataFrame],
        category_column: str,
        value_columns: List[str],
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate multi-series comparison chart.
        
        Args:
            data: Input data
            category_column: Column for X-axis (e.g., 'University')
            value_columns: List of columns to compare (e.g., ['Bachelor', 'Master'])
            title: Chart title
        
        Returns:
            Graph result dict
        """
        df = self.data_processor.normalize_input(data)
        df = self.data_processor.clean_data(df)
        
        # Reshape data for grouped bar chart
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        for col in value_columns:
            fig.add_trace(go.Bar(
                name=col,
                x=df[category_column],
                y=df[col],
                text=df[col],
                textposition='auto'
            ))
        
        fig.update_layout(
            title=title or f"Comparison of {', '.join(value_columns)}",
            xaxis_title=category_column,
            yaxis_title="Value",
            barmode='group',
            template='plotly_white'
        )
        
        return {
            'html': fig.to_html(include_plotlyjs=True, full_html=True),
            'figure': fig.to_json(),
            'type': 'comparison',
            'metadata': {
                'categories': list(df[category_column]),
                'value_columns': value_columns
            }
        }
    
    def generate_time_series(
        self,
        data: Union[List[Dict], pd.DataFrame],
        time_column: str,
        value_column: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate time-series line graph.
        
        Args:
            data: Input data with time information
            time_column: Column containing time/date data
            value_column: Column with values to plot
            title: Chart title
        
        Returns:
            Graph result dict
        """
        df = self.data_processor.normalize_input(data)
        df = self.data_processor.prepare_time_series(df, time_column, value_column)
        
        return self.generate_graph(
            data=df,
            x_column=time_column,
            y_column=value_column,
            graph_type='line',
            title=title or f"{value_column} Over Time"
        )
    
    def generate_correlation_plot(
        self,
        data: Union[List[Dict], pd.DataFrame],
        variable_x: str,
        variable_y: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate scatter plot for correlation analysis.
        
        Args:
            data: Input data
            variable_x: X variable
            variable_y: Y variable
            title: Chart title
        
        Returns:
            Graph result dict with correlation coefficient
        """
        df = self.data_processor.normalize_input(data)
        df = self.data_processor.clean_data(df)
        
        # Calculate correlation
        correlation = df[[variable_x, variable_y]].corr().iloc[0, 1]
        
        result = self.generate_graph(
            data=df,
            x_column=variable_x,
            y_column=variable_y,
            graph_type='scatter',
            title=title or f"{variable_x} vs {variable_y} (r={correlation:.3f})"
        )
        
        result['correlation'] = float(correlation)
        
        return result
