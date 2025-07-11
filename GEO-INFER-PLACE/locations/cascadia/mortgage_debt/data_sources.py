"""
Cascadian Mortgage Data Sources

This module is responsible for fetching and processing mortgage data from the
Home Mortgage Disclosure Act (HMDA) database.
"""
import logging
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import io
import json

logger = logging.getLogger(__name__)

class CascadianMortgageDataSources:
    """Handles fetching and processing of HMDA mortgage data."""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'mortgages')
        os.makedirs(self.data_dir, exist_ok=True)
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'data_urls.json')
        try:
            with open(config_path) as f:
                self.config = json.load(f).get('mortgage_debt', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse mortgage_debt config: {e}")
            self.config = {}

        self.hmda_bulk_url_template = self.config.get('hmda_bulk_url')

    def _fetch_hmda_data(self, year: int, states: list) -> pd.DataFrame:
        """
        Fetches HMDA LAR data for given states and year.
        """
        all_state_dfs = []
        for state in states:
            file_path = os.path.join(self.data_dir, f'hmda_{year}_{state}.csv')
            
            if os.path.exists(file_path):
                logger.info(f"Loading cached HMDA data for {state}, {year} from {file_path}")
                all_state_dfs.append(pd.read_csv(file_path))
                continue

            logger.info(f"Fetching HMDA data for {state}, {year}...")
            
            if not self.hmda_bulk_url_template:
                logger.error("HMDA bulk URL template not configured. Cannot download data.")
                continue
            
            download_success = False
            for year_to_try in range(year, year - 4, -1):
                try:
                    hmda_bulk_url = self.hmda_bulk_url_template.format(year=year_to_try, state=state.lower())
                    
                    logger.info(f"Attempting to download from bulk URL for year {year_to_try}: {hmda_bulk_url}")
                    
                    response = requests.get(hmda_bulk_url, timeout=300) # Increased timeout for large files
                    
                    if response.status_code == 404:
                        logger.warning(f"HMDA data not found for {state} for year {year_to_try}. Trying previous year.")
                        continue
                    
                    response.raise_for_status()
                    
                    # Use dtype={'census_tract': str} to avoid losing leading zeros
                    df = pd.read_csv(io.StringIO(response.text), dtype={'census_tract': str})
                    df.to_csv(file_path, index=False)
                    all_state_dfs.append(df)
                    logger.info(f"Successfully downloaded and cached HMDA data for {state}, {year_to_try}")
                    download_success = True
                    break # Exit the loop on success
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error downloading HMDA data for {state}, year {year_to_try}: {e}")
                    # Don't break here, allow it to try the next year
            
            if not download_success:
                 logger.warning(f"Falling back to empty dataframe for {state} after trying multiple years.")
        
        if not all_state_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_state_dfs, ignore_index=True)

    def fetch_all_mortgage_data(self, year: int = 2022) -> pd.DataFrame:
        """
        Loads all available HMDA mortgage data for CA and OR.
        
        Args:
            year: The year to fetch data for. Defaults to 2022 as it's a recent, complete year.

        Returns:
            A DataFrame containing all found mortgage data, or an empty one.
        """
        logger.info(f"Fetching mortgage data for CA and OR for year {year}.")
        
        states = ['CA', 'OR']
        hmda_df = self._fetch_hmda_data(year, states)
        
        if hmda_df.empty:
            logger.warning("No mortgage data could be fetched.")
            return pd.DataFrame()

        # Clean and process the data
        # Select only relevant columns
        cols_to_keep = ['census_tract', 'loan_amount', 'property_value', 'income']
        hmda_df = hmda_df[cols_to_keep].copy()

        # Convert to numeric, coercing errors
        for col in ['loan_amount', 'property_value', 'income']:
            hmda_df[col] = pd.to_numeric(hmda_df[col], errors='coerce')
        
        # Drop rows where key financial data is missing
        hmda_df.dropna(subset=['loan_amount', 'property_value', 'census_tract'], inplace=True)
        
        # Filter out nonsensical values
        hmda_df = hmda_df[hmda_df['loan_amount'] > 1000]
        hmda_df = hmda_df[hmda_df['property_value'] > 1000]
        
        logger.info(f"Aggregating HMDA data by census tract...")
        
        # Aggregate by census tract
        agg_df = hmda_df.groupby('census_tract').agg(
            total_loan_volume=('loan_amount', 'sum'),
            average_loan_amount=('loan_amount', 'mean'),
            average_property_value=('property_value', 'mean'),
            average_income=('income', 'mean'),
            number_of_loans=('loan_amount', 'count')
        ).reset_index()

        # Calculate Loan to Value Ratio
        agg_df['loan_to_value_ratio'] = agg_df['total_loan_volume'] / agg_df.groupby('census_tract')['average_property_value'].transform('sum')
        agg_df['loan_to_value_ratio'].replace([np.inf, -np.inf], np.nan, inplace=True)
        
        logger.info(f"Successfully processed and aggregated mortgage data for {len(agg_df)} census tracts.")
        return agg_df 