"""
Graph type definitions and configurations.
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class GraphType(str, Enum):
    """Supported graph types."""
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    AREA = "area"


class GraphStyle(BaseModel):
    """Graph styling configuration."""
    title: Optional[str] = None
    title_font_size: int = 20
    
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    axis_font_size: int = 12
    
    show_legend: bool = True
    legend_position: str = "right"  # top, bottom, left, right
    
    color_scheme: str = "plotly"  # plotly, viridis, blues, etc.
    template: str = "plotly_white"  # plotly, plotly_white, plotly_dark, etc.
    
    width: Optional[int] = None
    height: Optional[int] = None
    
    show_grid: bool = True
    show_hover: bool = True


class GraphConfig(BaseModel):
    """Complete graph configuration."""
    graph_type: GraphType
    x_column: str
    y_column: Optional[str] = None
    
    aggregation: Optional[str] = None  # mean, sum, count, etc.
    sort_by: Optional[str] = None
    sort_descending: bool = False
    
    style: GraphStyle = GraphStyle()
    
    # Additional columns for grouping/coloring
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    
    # Specific configurations
    orientation: str = "v"  # h for horizontal bars
    show_values: bool = True  # Show values on bars/points


# Default configurations for each graph type
DEFAULT_CONFIGS = {
    GraphType.BAR: {
        "style": {
            "template": "plotly_white",
            "show_grid": True
        },
        "orientation": "v",
        "show_values": True
    },
    GraphType.LINE: {
        "style": {
            "template": "plotly_white",
            "show_grid": True
        },
        "show_values": False
    },
    GraphType.SCATTER: {
        "style": {
            "template": "plotly_white",
            "show_grid": True
        }
    },
    GraphType.PIE: {
        "style": {
            "template": "plotly_white",
            "show_legend": True,
            "legend_position": "right"
        }
    },
    GraphType.HISTOGRAM: {
        "style": {
            "template": "plotly_white",
            "show_grid": True
        }
    },
    GraphType.BOX: {
        "style": {
            "template": "plotly_white",
            "show_grid": True
        }
    },
    GraphType.HEATMAP: {
        "style": {
            "template": "plotly_white",
            "color_scheme": "viridis"
        }
    }
}


def get_default_config(graph_type: GraphType) -> Dict[str, Any]:
    """Get default configuration for a graph type."""
    return DEFAULT_CONFIGS.get(graph_type, {})
