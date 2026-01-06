import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays

class DataProcessor:
    """Handles all data preprocessing and validation"""
    
    def __init__(self):
        self.indonesian_holidays = holidays.Indonesia()
    
    def parse_uploaded_data(self, df):
        """Parse and validate uploaded data"""
        try:
            # Required columns
            required_cols = ['date', 'company', 'origin', 'destination', 
                           'province', 'region', 'fleet_type', 'qty']
            
            # Check if all required columns exist
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return None, f"Missing columns: {', '.join(missing_cols)}"
            
            # Parse dates with dd/mm/yyyy format
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
            
            # Check for invalid dates
            invalid_dates = df['date'].isna().sum()
            if invalid_dates > 0:
                return None, f"Found {invalid_dates} invalid dates. Please use dd/mm/yyyy format (e.g., 31/12/2024)"
            
            # Convert qty to numeric
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
            
            # Remove rows with missing qty
            df = df.dropna(subset=['qty'])
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df, "Success"
            
        except Exception as e:
            return None, f"Error parsing data: {str(e)}"
    
    def detect_frequency(self, df):
        """Auto-detect if data is daily or monthly"""
        try:
            dates = pd.to_datetime(df['date']).sort_values().unique()
            
            # Check if all dates are 1st of the month
            if all(pd.to_datetime(d).day == 1 for d in dates):
                return 'MS', 'Monthly'
            
            # Calculate median difference between consecutive dates
            if len(dates) > 1:
                date_series = pd.Series(dates).sort_values()
                date_diffs = date_series.diff().dropna()
                median_diff = date_diffs.dt.days.median()
                
                # If median difference is around 28-31 days, it's monthly
                if 25 <= median_diff <= 35:
                    return 'MS', 'Monthly'
                # If median difference is 1-2 days, it's daily
                elif median_diff <= 2:
                    return 'D', 'Daily'
            
            # Fallback: check unique dates count vs date range
            date_range_days = (dates.max() - dates.min()).days
            n_unique_dates = len(dates)
            
            # If we have roughly one date per month, it's monthly
            if date_range_days > 300 and n_unique_dates < 50:
                return 'MS', 'Monthly'
            
            return 'D', 'Daily (default)'
                
        except Exception as e:
            return 'D', 'Daily (default)'
    
    def validate_data_quality(self, df, freq='D'):
        """Check data quality and return report"""
        report = {}
        
        # Basic stats
        report['total_rows'] = len(df)
        report['date_range'] = f"{df['date'].min().strftime('%d/%m/%Y')} to {df['date'].max().strftime('%d/%m/%Y')}"
        report['total_days'] = (df['date'].max() - df['date'].min()).days + 1
        
        # Check minimum data points
        min_points = 30 if freq == 'D' else 12
        report['has_minimum_data'] = len(df['date'].unique()) >= min_points
        report['min_points_required'] = min_points
        report['actual_points'] = len(df['date'].unique())
        
        # Unique combinations
        report['unique_companies'] = df['company'].nunique()
        report['unique_origins'] = df['origin'].nunique()
        report['unique_destinations'] = df['destination'].nunique()
        report['unique_fleet_types'] = df['fleet_type'].nunique()
        report['unique_routes'] = df.groupby(['origin', 'destination']).ngroups
        
        # Missing dates
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq=freq)
        actual_dates = df['date'].unique()
        missing_dates_count = len(set(date_range) - set(actual_dates))
        report['missing_dates'] = missing_dates_count
        
        # Zero values
        report['zero_qty_count'] = (df['qty'] == 0).sum()
        report['zero_qty_percent'] = round((df['qty'] == 0).sum() / len(df) * 100, 2)
        
        return report
    
    def fill_missing_dates(self, df, freq='D', aggregation_cols=None):
        """Fill missing dates for each unique series"""
        if aggregation_cols is None:
            aggregation_cols = ['company', 'origin', 'destination', 'fleet_type']
        
        # Create unique_id
        df['unique_id'] = df[aggregation_cols].astype(str).agg('_'.join, axis=1)
        
        # Get full date range
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq=freq)
        
        # Fill missing dates for each series
        filled_dfs = []
        for unique_id in df['unique_id'].unique():
            series_df = df[df['unique_id'] == unique_id].copy()
            
            # Create complete date range for this series
            complete_dates = pd.DataFrame({'date': date_range})
            
            # Merge with existing data
            series_df = complete_dates.merge(series_df, on='date', how='left')
            
            # Fill unique_id
            series_df['unique_id'] = unique_id
            
            # Fill other columns with forward fill, then backward fill, then 0
            for col in aggregation_cols:
                series_df[col] = series_df[col].fillna(method='ffill').fillna(method='bfill')
            
            # Fill province and region
            series_df['province'] = series_df['province'].fillna(method='ffill').fillna(method='bfill')
            series_df['region'] = series_df['region'].fillna(method='ffill').fillna(method='bfill')
            
            # Fill qty with 0 for missing dates
            series_df['qty'] = series_df['qty'].fillna(0)
            
            filled_dfs.append(series_df)
        
        result_df = pd.concat(filled_dfs, ignore_index=True)
        return result_df.sort_values(['unique_id', 'date']).reset_index(drop=True)
    
    def aggregate_data(self, df, aggregation_level):
        """Aggregate data based on selected level"""
        
        # Define aggregation mappings
        agg_mappings = {
            'Most Granular': ['company', 'origin', 'destination', 'fleet_type'],
            'By Company': ['company'],
            'By Route': ['origin', 'destination'],
            'By Fleet Type': ['fleet_type'],
            'By Region': ['region'],
            'By Province': ['province'],
            'By Company & Route': ['company', 'origin', 'destination'],
            'By Company & Fleet Type': ['company', 'fleet_type'],
            'By Route & Fleet Type': ['origin', 'destination', 'fleet_type']
        }
        
        if aggregation_level not in agg_mappings:
            return df, ['company', 'origin', 'destination', 'fleet_type']
        
        agg_cols = agg_mappings[aggregation_level]
        
        # Aggregate
        agg_df = df.groupby(agg_cols + ['date']).agg({'qty': 'sum'}).reset_index()
        
        # Fill missing columns with 'All'
        all_cols = ['company', 'origin', 'destination', 'province', 'region', 'fleet_type']
        for col in all_cols:
            if col not in agg_df.columns:
                agg_df[col] = 'All'
        
        return agg_df, agg_cols
    
    def prepare_for_timegpt(self, df, aggregation_cols):
        """Prepare data in TimeGPT format"""
        # Create unique_id
        df['unique_id'] = df[aggregation_cols].astype(str).agg('_'.join, axis=1)
        
        # Prepare TimeGPT format: unique_id, ds, y
        timegpt_df = df[['unique_id', 'date', 'qty']].copy()
        timegpt_df.columns = ['unique_id', 'ds', 'y']
        
        # DO NOT set as index - keep as regular columns
        return timegpt_df
    
    def add_holiday_features(self, df, freq='D'):
        """Add Indonesian holiday features"""
        df = df.copy()
        
        # Get years from data
        years = df['date'].dt.year.unique()
        
        # Create holiday calendar
        id_holidays = holidays.Indonesia(years=years.tolist())
        
        # Add is_holiday column
        df['is_holiday'] = df['date'].apply(lambda x: 1 if x in id_holidays else 0)
        
        # Add day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Add is_weekend
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        # For monthly data, add month number
        if freq == 'MS':
            df['month'] = df['date'].dt.month
        
        return df
    
    def handle_outliers(self, df, method='cap', threshold=99):
        """Handle outliers in qty column"""
        if method == 'cap':
            # Cap at percentile
            upper_limit = df['qty'].quantile(threshold / 100)
            df['qty'] = df['qty'].clip(upper=upper_limit)
        elif method == 'remove':
            # Remove outliers
            upper_limit = df['qty'].quantile(threshold / 100)
            df = df[df['qty'] <= upper_limit]
        
        return df
    
    def get_series_summary(self, df, aggregation_cols):
        """Get summary of series to be forecasted"""
        df['unique_id'] = df[aggregation_cols].astype(str).agg('_'.join, axis=1)
        
        summary = {
            'total_series': df['unique_id'].nunique(),
            'series_list': df['unique_id'].unique().tolist()[:10],  # First 10
            'avg_data_points': df.groupby('unique_id').size().mean(),
            'total_qty': df['qty'].sum(),
            'avg_qty': df['qty'].mean()
        }
        
        return summary
