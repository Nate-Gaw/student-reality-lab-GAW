"""
Data processing utilities for graph generation.
Handles data cleaning, validation, and transformation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class DataProcessor:
    """Process and prepare data for visualization."""
    
    @staticmethod
    def normalize_input(data: Union[List[Dict], Dict, pd.DataFrame, str]) -> pd.DataFrame:
        """
        Convert various input formats to pandas DataFrame.
        
        Args:
            data: Input data (list of dicts, dict, DataFrame, or CSV string)
        
        Returns:
            Normalized pandas DataFrame
        """
        if isinstance(data, pd.DataFrame):
            return data
        
        elif isinstance(data, list):
            # List of dictionaries
            return pd.DataFrame(data)
        
        elif isinstance(data, dict):
            # Single dict or dict with lists as values
            if all(isinstance(v, list) for v in data.values()):
                # Dict of lists: {'col1': [1,2,3], 'col2': [4,5,6]}
                return pd.DataFrame(data)
            else:
                # Single record: {'col1': 1, 'col2': 2}
                return pd.DataFrame([data])
        
        elif isinstance(data, str):
            # Assume CSV string
            from io import StringIO
            return pd.read_csv(StringIO(data))
        
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    @staticmethod
    def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer semantic types of DataFrame columns.
        
        Returns:
            Dict mapping column name to type: 'categorical', 'numeric', 'datetime', 'text'
        """
        column_types = {}
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                column_types[col] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                column_types[col] = 'datetime'
            elif df[col].nunique() < len(df) * 0.5 and df[col].nunique() < 20:
                # Low cardinality suggests categorical
                column_types[col] = 'categorical'
            else:
                column_types[col] = 'text'
        
        return column_types
    
    @staticmethod
    def auto_detect_graph_type(
        df: pd.DataFrame,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> str:
        """
        Automatically determine the best graph type for the data.
        
        Returns:
            Graph type: 'bar', 'line', 'scatter', 'pie', 'histogram'
        """
        column_types = DataProcessor.infer_column_types(df)
        
        # Single numeric column -> histogram
        if y_column is None and x_column and column_types.get(x_column) == 'numeric':
            return 'histogram'
        
        # No columns specified but only 2 columns total
        if not x_column and not y_column and len(df.columns) == 2:
            x_column, y_column = df.columns[0], df.columns[1]
        
        if x_column and y_column:
            x_type = column_types.get(x_column, 'text')
            y_type = column_types.get(y_column, 'numeric')
            
            # Categorical X + Numeric Y -> Bar chart
            if x_type == 'categorical' and y_type == 'numeric':
                # If requesting proportions/percentages -> Pie
                if df[x_column].nunique() <= 8 and 'percent' in y_column.lower():
                    return 'pie'
                return 'bar'
            
            # Datetime/ordered X + Numeric Y -> Line graph
            if (x_type == 'datetime' or 'time' in x_column.lower() or 'date' in x_column.lower()) and y_type == 'numeric':
                return 'line'
            
            # Numeric X + Numeric Y -> Scatter plot
            if x_type == 'numeric' and y_type == 'numeric':
                return 'scatter'
        
        # Default to bar chart for safety
        return 'bar'
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame: handle missing values, remove duplicates.
        """
        # Remove completely empty rows/columns
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Fill numeric NaN with 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Fill categorical NaN with 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna('Unknown')
        
        return df
    
    @staticmethod
    def aggregate_for_visualization(
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        aggregation: str = 'mean'
    ) -> pd.DataFrame:
        """
        Aggregate data for cleaner visualization.
        
        Args:
            aggregation: 'mean', 'sum', 'count', 'median'
        """
        agg_func = {
            'mean': 'mean',
            'sum': 'sum',
            'count': 'count',
            'median': 'median',
            'min': 'min',
            'max': 'max'
        }.get(aggregation, 'mean')
        
        # Group by x_column and aggregate y_column
        result = df.groupby(x_column)[y_column].agg(agg_func).reset_index()
        return result
    
    @staticmethod
    def prepare_time_series(
        df: pd.DataFrame,
        time_column: str,
        value_column: str
    ) -> pd.DataFrame:
        """
        Prepare time-series data for line graphs.
        """
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
            df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
        
        # Sort by time
        df = df.sort_values(time_column)
        
        # Remove rows with invalid dates
        df = df.dropna(subset=[time_column])
        
        return df
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame, column: str) -> Dict[str, float]:
        """
        Calculate descriptive statistics for a numeric column.
        """
        if column not in df.columns:
            return {}
        
        series = df[column].dropna()
        
        return {
            'mean': float(series.mean()),
            'median': float(series.median()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'count': int(series.count()),
            'q25': float(series.quantile(0.25)),
            'q75': float(series.quantile(0.75))
        }
