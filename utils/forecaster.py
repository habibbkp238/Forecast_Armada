import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class FleetForecaster:
    """Handles forecasting using TimeGPT and fallback methods"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.nixtla_client = None
        
        if api_key:
            try:
                from nixtla import NixtlaClient
                self.nixtla_client = NixtlaClient(api_key=api_key)
            except ImportError:
                st.error("nixtla package not installed. Please install: pip install nixtla")
            except Exception as e:
                st.error(f"Error initializing TimeGPT client: {str(e)}")
    
    def validate_api_key(self):
        """Validate if API key is working"""
        if not self.nixtla_client:
            return False, "API key not initialized"
        
        try:
            # Test with a small dummy dataset
            test_df = pd.DataFrame({
                'unique_id': ['test'] * 10,
                'ds': pd.date_range(start='2024-01-01', periods=10, freq='D'),
                'y': np.random.randint(1, 10, 10)
            })
            
            # Try to forecast 1 period
            _ = self.nixtla_client.forecast(
                df=test_df,
                h=1,
                time_col='ds',
                target_col='y',
                id_col='unique_id',
                freq='D'
            )
            
            return True, "API key validated successfully"
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'authentication' in error_msg or 'api key' in error_msg:
                return False, "Invalid API key"
            elif 'quota' in error_msg or 'limit' in error_msg:
                return False, "API quota exceeded"
            else:
                return False, f"API validation error: {str(e)}"
    
    def forecast_timegpt(self, df, horizon, freq='D', model='timegpt-1-long-horizon', 
                        exog_df=None, progress_callback=None):
        """Forecast using TimeGPT"""
        
        if not self.nixtla_client:
            return None, "TimeGPT client not initialized"
        
        try:
            if progress_callback:
                progress_callback(0.3, "Preparing data for TimeGPT...")
            
            # Ensure correct column names
            forecast_df = df.copy()
            if 'unique_id' not in forecast_df.columns:
                return None, "Missing 'unique_id' column"
            
            # Get number of unique series
            n_series = forecast_df['unique_id'].nunique()
            
            if progress_callback:
                progress_callback(0.5, f"Forecasting {n_series} series with TimeGPT...")
            
            # Call TimeGPT API
            result = self.nixtla_client.forecast(
                df=forecast_df,
                h=horizon,
                freq=freq,
                model=model
            )
            
            if progress_callback:
                progress_callback(0.9, "Processing forecast results...")
            
            # Rename forecast column to 'forecast'
            if 'TimeGPT' in result.columns:
                result = result.rename(columns={'TimeGPT': 'forecast'})
            
            # Round forecasts to integers (can't have fractional fleets)
            result['forecast'] = result['forecast'].round().astype(int)
            
            # Ensure no negative forecasts
            result['forecast'] = result['forecast'].clip(lower=0)
            
            if progress_callback:
                progress_callback(1.0, "Forecast completed!")
            
            return result, "Success"
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'quota' in error_msg or 'limit' in error_msg or 'rate' in error_msg:
                return None, f"API_LIMIT: {str(e)}"
            else:
                return None, f"TimeGPT error: {str(e)}"
    
    def forecast_moving_average(self, df, horizon, window=6, progress_callback=None):
        """Fallback: Simple Moving Average forecast"""
        
        try:
            if progress_callback:
                progress_callback(0.3, "Calculating moving averages...")
            
            forecast_results = []
            
            unique_ids = df['unique_id'].unique()
            total_series = len(unique_ids)
            
            for idx, unique_id in enumerate(unique_ids):
                series_data = df[df['unique_id'] == unique_id].copy()
                series_data = series_data.sort_values('ds')
                
                # Calculate MA-6
                ma_value = series_data['y'].tail(window).mean()
                
                # If not enough data, use overall mean
                if pd.isna(ma_value) or len(series_data) < window:
                    ma_value = series_data['y'].mean()
                
                # Create future dates
                last_date = series_data['ds'].max()
                freq = pd.infer_freq(series_data['ds'])
                if freq is None:
                    freq = 'D'
                
                future_dates = pd.date_range(
                    start=last_date + pd.Timedelta(days=1 if freq == 'D' else 30),
                    periods=horizon,
                    freq=freq
                )
                
                # Create forecast dataframe
                forecast_df = pd.DataFrame({
                    'unique_id': unique_id,
                    'ds': future_dates,
                    'forecast': int(round(ma_value))
                })
                
                forecast_results.append(forecast_df)
                
                # Update progress
                if progress_callback and (idx + 1) % 10 == 0:
                    progress = 0.3 + 0.6 * (idx + 1) / total_series
                    progress_callback(progress, f"Processing series {idx + 1}/{total_series}")
            
            result = pd.concat(forecast_results, ignore_index=True)
            
            if progress_callback:
                progress_callback(1.0, "Moving Average forecast completed!")
            
            return result, "Success"
            
        except Exception as e:
            return None, f"Moving Average error: {str(e)}"
    
    def prepare_exogenous_features(self, historical_df, forecast_horizon, freq='D'):
        """Prepare exogenous features (holidays) for both historical and forecast period"""
        
        try:
            import holidays
            
            # Get the historical dates
            min_date = historical_df['ds'].min()
            last_date = historical_df['ds'].max()
            
            # Create future dates for forecast
            if freq == 'D':
                future_dates = pd.date_range(
                    start=last_date + pd.Timedelta(days=1),
                    periods=forecast_horizon,
                    freq='D'
                )
            elif freq == 'MS' or freq == 'M':
                # For monthly, use month start
                future_dates = pd.date_range(
                    start=last_date + pd.DateOffset(months=1),
                    periods=forecast_horizon,
                    freq='MS'
                )
            
            # Get all historical dates
            historical_dates = historical_df['ds'].sort_values().unique()
            
            # Combine historical and future dates
            all_dates = list(historical_dates) + list(future_dates)
            
            # Get Indonesian holidays (2022-2026)
            years = list(range(2022, 2027))
            id_holidays = holidays.Indonesia(years=years)
            
            # Get all unique_ids
            unique_ids = historical_df['unique_id'].unique()
            
            # Create exogenous dataframe
            exog_data = []
            for uid in unique_ids:
                for date in all_dates:
                    exog_data.append({
                        'unique_id': uid,
                        'ds': pd.Timestamp(date),
                        'is_holiday': 1 if pd.Timestamp(date) in id_holidays else 0,
                        'is_weekend': 1 if pd.Timestamp(date).dayofweek >= 5 else 0,
                        'month': pd.Timestamp(date).month
                    })
            
            exog_df = pd.DataFrame(exog_data)
            
            return exog_df
            
        except Exception as e:
            st.warning(f"Could not prepare holiday features: {str(e)}")
            return None
    
    def run_forecast(self, df, horizon, freq='D', model='timegpt-1-long-horizon',
                     use_timegpt=True, include_holidays=True, progress_callback=None):
        """Main forecast method with fallback logic"""
        
        if progress_callback:
            progress_callback(0.1, "Starting forecast...")
        
        # Prepare exogenous features if requested
        exog_df = None
        if include_holidays and use_timegpt:
            exog_df = self.prepare_exogenous_features(df, horizon, freq)
            
            # Need to add holiday features to historical data too
            if exog_df is not None:
                import holidays
                years = df['ds'].dt.year.unique().tolist()
                id_holidays = holidays.Indonesia(years=years)
                
                df = df.copy()
                df['is_holiday'] = df['ds'].apply(lambda x: 1 if x in id_holidays else 0)
                df['day_of_week'] = df['ds'].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
                
                if freq == 'MS':
                    df['month'] = df['ds'].dt.month
        
        # Try TimeGPT first if requested
        if use_timegpt and self.nixtla_client:
            result, message = self.forecast_timegpt(
                df, horizon, freq, model, exog_df, progress_callback
            )
            
            if result is not None:
                # Increment API call counter
                st.session_state.api_calls_count += 1
                return result, "TimeGPT", message
            else:
                # Check if it's an API limit error
                if "API_LIMIT" in message:
                    st.warning(f"⚠️ {message}")
                    st.info("Switching to Moving Average (MA-6) fallback method...")
                    # Fall through to MA forecast
                else:
                    return None, "TimeGPT", message
        
        # Fallback to Moving Average
        if progress_callback:
            progress_callback(0.2, "Using Moving Average fallback...")
        
        result, message = self.forecast_moving_average(df, horizon, window=6, progress_callback=progress_callback)
        
        if result is not None:
            return result, "Moving Average (MA-6)", message
        else:
            return None, "Failed", message
    
    def merge_forecast_with_metadata(self, forecast_df, original_df, aggregation_cols):
        """Merge forecast results with original metadata"""
        
        # Extract metadata from original data
        metadata = original_df[aggregation_cols + ['province', 'region']].drop_duplicates()
        
        # Create unique_id in metadata
        metadata['unique_id'] = metadata[aggregation_cols].astype(str).agg('_'.join, axis=1)
        
        # Merge
        result = forecast_df.merge(metadata, on='unique_id', how='left')
        
        # Fill missing metadata with 'All'
        for col in ['company', 'origin', 'destination', 'province', 'region', 'fleet_type']:
            if col in result.columns:
                result[col] = result[col].fillna('All')
        
        # Rename columns
        result = result.rename(columns={'ds': 'date', 'forecast': 'forecast_qty'})
        
        # Format date as dd/mm/yyyy
        result['date'] = pd.to_datetime(result['date']).dt.strftime('%d/%m/%Y')
        
        return result
