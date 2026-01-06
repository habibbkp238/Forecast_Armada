import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class Visualizer:
    """Handles all visualizations for the app"""
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#2E7D32',
            'secondary': '#66BB6A',
            'accent': '#1B5E20',
            'light': '#E8F5E9',
            'historical': '#2196F3',
            'forecast': '#FF6B6B'
        }
    
    def plot_time_series(self, df, date_col='date', value_col='qty', 
                        title='Time Series', height=400):
        """Plot basic time series"""
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df[value_col],
            mode='lines+markers',
            name='Historical',
            line=dict(color=self.color_scheme['historical'], width=2),
            marker=dict(size=6),
            hovertemplate='<b>Date:</b> %{x|%d/%m/%Y}<br><b>Qty:</b> %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Quantity',
            hovermode='x unified',
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        return fig
    
    def plot_historical_vs_forecast(self, historical_df, forecast_df, 
                                    aggregation='total', height=500):
        """Plot historical data with forecast"""
        
        fig = go.Figure()
        
        # Prepare historical data
        if aggregation == 'total':
            hist_agg = historical_df.groupby('date')['qty'].sum().reset_index()
            hist_agg['date'] = pd.to_datetime(hist_agg['date'], format='%d/%m/%Y', errors='coerce')
            
            # Filter out zeros (auto-filled missing dates)
            hist_agg = hist_agg[hist_agg['qty'] > 0]
            
            # Sort by date
            hist_agg = hist_agg.sort_values('date')
            
            # Historical line
            fig.add_trace(go.Scatter(
                x=hist_agg['date'],
                y=hist_agg['qty'],
                mode='lines+markers',
                name='Historical',
                line=dict(color=self.color_scheme['historical'], width=2),
                marker=dict(size=6),
                hovertemplate='<b>Date:</b> %{x|%d/%m/%Y}<br><b>Qty:</b> %{y}<extra></extra>'
            ))
            
            # Prepare forecast data
            forecast_agg = forecast_df.groupby('date')['forecast_qty'].sum().reset_index()
            forecast_agg['date'] = pd.to_datetime(forecast_agg['date'], format='%d/%m/%Y', errors='coerce')
            
            # Sort by date
            forecast_agg = forecast_agg.sort_values('date')
            
            # Forecast line
            fig.add_trace(go.Scatter(
                x=forecast_agg['date'],
                y=forecast_agg['forecast_qty'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color=self.color_scheme['forecast'], width=2, dash='dash'),
                marker=dict(size=8),
                hovertemplate='<b>Date:</b> %{x|%d/%m/%Y}<br><b>Forecast:</b> %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Historical Data vs Forecast',
            xaxis_title='Date',
            yaxis_title='Total Fleet Quantity',
            hovermode='x unified',
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        return fig
    
    def plot_by_dimension(self, forecast_df, dimension='fleet_type', top_n=10, height=500):
        """Plot forecast by a specific dimension"""
        
        # Check if dimension exists
        if dimension not in forecast_df.columns:
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Dimension '{dimension}' not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(height=height)
            return fig
        
        # Aggregate by dimension
        agg_df = forecast_df.groupby(dimension)['forecast_qty'].sum().reset_index()
        agg_df = agg_df.sort_values('forecast_qty', ascending=False).head(top_n)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=agg_df[dimension],
            y=agg_df['forecast_qty'],
            marker=dict(
                color=agg_df['forecast_qty'],
                colorscale='Greens',
                showscale=False
            ),
            text=agg_df['forecast_qty'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Forecast: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Forecast by {dimension.replace("_", " ").title()} (Top {top_n})',
            xaxis_title=dimension.replace("_", " ").title(),
            yaxis_title='Total Forecast Quantity',
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12),
            showlegend=False
        )
        
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        return fig
    
    def plot_forecast_distribution(self, forecast_df, height=400):
        """Plot distribution of forecasts"""
        
        # Aggregate by date
        daily_forecast = forecast_df.groupby('date')['forecast_qty'].sum().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=daily_forecast['forecast_qty'],
            name='Forecast Distribution',
            marker=dict(color=self.color_scheme['primary']),
            boxmean='sd'
        ))
        
        fig.update_layout(
            title='Forecast Distribution',
            yaxis_title='Forecast Quantity',
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12),
            showlegend=False
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        return fig
    
    def plot_top_routes(self, forecast_df, top_n=10, height=500):
        """Plot top routes by forecast volume"""
        
        # Check if origin and destination exist
        if 'origin' not in forecast_df.columns or 'destination' not in forecast_df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Route data not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(height=height)
            return fig
        
        # Create route column
        forecast_df_copy = forecast_df.copy()
        forecast_df_copy['route'] = forecast_df_copy['origin'] + ' → ' + forecast_df_copy['destination']
        
        # Aggregate by route
        route_agg = forecast_df_copy.groupby('route')['forecast_qty'].sum().reset_index()
        route_agg = route_agg.sort_values('forecast_qty', ascending=True).tail(top_n)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=route_agg['forecast_qty'],
            y=route_agg['route'],
            orientation='h',
            marker=dict(
                color=route_agg['forecast_qty'],
                colorscale='Greens',
                showscale=False
            ),
            text=route_agg['forecast_qty'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Forecast: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Top {top_n} Routes by Forecast Volume',
            xaxis_title='Total Forecast Quantity',
            yaxis_title='Route',
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12),
            showlegend=False
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E0E0E0',
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        fig.update_yaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='#E0E0E0'
        )
        
        return fig
    
    def plot_heatmap(self, df, x_col, y_col, value_col, title='Heatmap', height=500):
        """Create a heatmap"""
        
        # Check if columns exist
        if x_col not in df.columns or y_col not in df.columns or value_col not in df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Required columns not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(height=height)
            return fig
        
        # Pivot data
        pivot_df = df.pivot_table(
            index=y_col,
            columns=x_col,
            values=value_col,
            aggfunc='sum'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Greens',
            hovertemplate='<b>%{x}</b><br><b>%{y}</b><br>Value: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            height=height,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12)
        )
        
        return fig