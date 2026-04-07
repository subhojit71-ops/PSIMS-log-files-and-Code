""""
PSIms Complete Unified System v3.8 - PDF REPORTS + ENHANCED ANALYTICS
Pharma Stakeholder Interaction Monitoring System

Author: Subhoit Talukdar
Version: 3.8 - Production Ready (PART 1 of 3)

NEW FEATURES:
- Enhanced cluster_profiles CSV with percentage calculations
- Multi-page PDF reports with 9 comprehensive pie charts
- Per-cluster composition analysis (5 charts)
- Per-bucket dominance analysis (4 charts)
- Professional formatting with legends and labels
"""

# Check if running in Jupyter and handle kernel restart
#try:
#    from IPython import get_ipython
#    ipython = get_ipython()
#    if ipython is not None and 'IPKernelApp' in ipython.config:
#        IS_JUPYTER = True
#        import atexit
#        def cleanup_on_exit():
#           try:
#                import gc
#                gc.collect()
#            except:
#                pass
#        atexit.register(cleanup_on_exit)
#    else:
#       IS_JUPYTER = False
#except:
#    IS_JUPYTER = False

import pandas as pd
import numpy as np
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import openpyxl
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from difflib import SequenceMatcher
import threading


# UI Library Check
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledText
    THEME_AVAILABLE = True
except ImportError:
    import tkinter.ttk as ttk
    from tkinter.scrolledtext import ScrolledText
    THEME_AVAILABLE = False
    print("NOTE: ttkbootstrap not found. UI will look standard.")

# Visualization libraries (REQUIRED for PDF reports)
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.backends.backend_pdf import PdfPages
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("ERROR: matplotlib/seaborn REQUIRED for PDF reports. Install with: pip install matplotlib seaborn")

import warnings
warnings.filterwarnings('ignore')
import hashlib  
import copy     


# =====================================================
# CONFIGURATION MANAGER (SAFE MODE)
# =====================================================

class PSImsConfig:
    """Manages system configuration with persistent storage and crash protection"""
    
    def __init__(self):
        self.config_file = 'psims_config.json.backup'
        self.config = self.load_or_create()
    
    def load_or_create(self):
        """Load config or create with default structure"""
        default_config = {
            'folders': {
                'input_folder': '',
                'csv_output': '',
                'results_output': ''
            },
            'settings': {
                'eligibility_mode': 'relaxed',
                'num_clusters': 6,
                'require_engagement': True,
                'zero_data_position': 'first',
                'naming_method': 'combined',
                'high_threshold': 30,
                'low_threshold': 15,
                'show_quality_metrics': True,
                'generate_visualizations': False
            },
            'last_run': None
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    content = f.read()
                    if not content.strip(): 
                        raise ValueError("Empty config file")
                    
                    loaded_config = json.loads(content)
                    
                    # Ensure all required keys exist
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                        elif isinstance(default_config[key], dict):
                            for subkey in default_config[key]:
                                if subkey not in loaded_config[key]:
                                    loaded_config[key][subkey] = default_config[key][subkey]
                    
                    return loaded_config
            except Exception as e:
                print(f"Warning: Config file corrupted ({e}). Resetting to defaults.")
                try:
                    os.remove(self.config_file)
                except:
                    pass
                return default_config
        
        return default_config
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def update_folder(self, key, path):
        """Update folder path in config"""
        if 'folders' not in self.config:
            self.config['folders'] = {}
        self.config['folders'][key] = path
        self.save()
    
    def get_folder(self, key):
        """Get folder path from config"""
        if 'folders' not in self.config:
            self.config['folders'] = {}
        return self.config['folders'].get(key, '')
    
    def update_setting(self, key, value):
        """Update a setting"""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        self.config['settings'][key] = value
        self.save()
    
    def get_setting(self, key, default=None):
        """Get a setting"""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        return self.config['settings'].get(key, default)
    

# =====================================================
# ADMIN SETTINGS MANAGER (ADD AFTER PSImsConfig CLASS)
# =====================================================

class AdminSettingsManager:
    """Manages admin authentication and scoring configuration"""
    
    def __init__(self, config_manager):
        self.config = config_manager 
        self.default_password_hash = self._hash_password("Lupin@123")  #Default password
        
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verify admin password"""
        stored_hash = self.config.get_setting('admin_password_hash', self.default_password_hash)
        return self._hash_password(password) == stored_hash
    
    def change_password(self, old_password, new_password):
        """Change admin password"""
        if not self.verify_password(old_password):
            return False, "Incorrect current password"
        
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        
        new_hash = self._hash_password(new_password)
        self.config.update_setting('admin_password_hash', new_hash)
        return True, "Password changed successfully"
    
    def get_scoring_config(self):
        """Load scoring config from settings or return defaults"""
        saved_config = self.config.get_setting('scoring_config', None)
        if saved_config:
            return saved_config
        else:
            return copy.deepcopy(DEFAULT_SCORING_CONFIG)
    
    def save_scoring_config(self, scoring_config):
        """Save scoring configuration"""
        self.config.update_setting('scoring_config', scoring_config)
        global SCORING_CONFIG
        SCORING_CONFIG = copy.deepcopy(scoring_config)
        return True
    
    def reset_to_defaults(self):
        """Reset scoring config to factory defaults"""
        self.config.update_setting('scoring_config', None)
        global SCORING_CONFIG
        SCORING_CONFIG = copy.deepcopy(DEFAULT_SCORING_CONFIG)
        return True


# =====================================================
# SCORING CONFIGURATION 
# =====================================================

# =====================================================
# SCORING CONFIGURATION (UPDATED WITH THRESHOLDS)
# =====================================================

DEFAULT_SCORING_CONFIG = {
    'engagement': {
        'email_open_weight': 0.50, 
        'email_click_weight': 0.50,
        'whatsapp_read_weight': 0.50, 
        'whatsapp_click_weight': 0.50,
        'call_productive_weight': 0.70, 
        'call_duration_weight': 0.30,
        'final_email_weight': 0.33, 
        'final_whatsapp_weight': 0.33, 
        'final_call_weight': 0.34,
        'max_score': 100,
        'high_threshold': 30, 
        'low_threshold': 15  # NEW
    },
    'academic': {
        'publication_points_per_item': 10, 
        'publication_max_score': 50,
        'trial_points_per_item': 20, 
        'trial_max_score': 30,
        'association_points_per_item': 10, 
        'association_max_score': 20,
        'max_score': 100, 
        'baseline_threshold': 10,
        'high_threshold': 30, 
        'low_threshold': 15  # NEW
    },
    'social_media': {
        'follower_log_multiplier': 10, 
        'follower_max_score': 50,
        'follower_min_threshold': 100,
        'platform_points_per_item': 10, 
        'platform_max_score': 30,
        'healthcare_platform_points_per_item': 10, 
        'healthcare_platform_max_score': 20,
        'max_score': 100,
        'high_threshold': 30, 
        'low_threshold': 15  # NEW
    },
    'recognition': {
        'award_points_per_item': 15, 
        'award_max_score': 30,
        'press_points_per_item': 10, 
        'press_max_score': 25,
        'event_points_per_item': 8, 
        'event_max_score': 25,
        'association_points_per_item': 5, 
        'association_max_score': 20,
        'max_score': 100,
        'high_threshold': 30, 
        'low_threshold': 15  # NEW
    }
}
SCORING_CONFIG = copy.deepcopy(DEFAULT_SCORING_CONFIG)


# =====================================================
# SMART EXCEL CONVERTER
# =====================================================

class SmartConverter:
    """Intelligently combines and converts Excel files"""
    
    def __init__(self, output_folder, log_callback=None):
        self.output_folder = output_folder
        self.log = log_callback or print
        self.warnings = []
    
    def standardize_name(self, name):
        """Standardize names (lowercase, no spaces)"""
        return name.strip().lower().replace(' ', '_').replace("'", "")
    
    def fuzzy_match(self, str1, str2, threshold=0.8):
        """Fuzzy string matching"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() >= threshold
    
    def combine_pi_batches(self, pi_files):
        """Combine multiple PI batch files"""
        self.log("\n📊 Combining Personal Info Batches...")
        
        all_sheets_per_file = {}
        for file in pi_files:
            try:
                wb = openpyxl.load_workbook(file, read_only=True)
                all_sheets_per_file[file] = wb.sheetnames
                wb.close()
                self.log(f"   {os.path.basename(file)}: {len(all_sheets_per_file[file])} sheets")
            except Exception as e:
                self.log(f"   ❌ Error loading {os.path.basename(file)}: {e}")
                continue
        
        if not all_sheets_per_file:
            self.log("   ❌ No valid PI files to process")
            return
        
        master_sheets = all_sheets_per_file[list(all_sheets_per_file.keys())[0]]
        sheet_mapping = {sheet: [] for sheet in master_sheets}
        
        for file in all_sheets_per_file.keys():
            file_sheets = all_sheets_per_file[file]
            for master_sheet in master_sheets:
                if master_sheet in file_sheets:
                    sheet_mapping[master_sheet].append((file, master_sheet))
                else:
                    for file_sheet in file_sheets:
                        if self.fuzzy_match(master_sheet, file_sheet):
                            warning = f"Fuzzy match: '{master_sheet}' → '{file_sheet}' in {os.path.basename(file)}"
                            self.warnings.append(warning)
                            self.log(f"   ⚠️  {warning}")
                            sheet_mapping[master_sheet].append((file, file_sheet))
                            break
        
        COUNT_BASED_SHEETS = ['publication', 'trials', 'academic_association', 
                             'awards', 'press', 'events', 'association']
        
        self.log("\n   📝 Combining sheets...")
        for sheet_name, file_sheet_pairs in sheet_mapping.items():
            if not file_sheet_pairs:
                self.log(f"   ⚠️  No data found for sheet: {sheet_name}")
                continue
            
            dfs = []
            for file, actual_sheet_name in file_sheet_pairs:
                try:
                    df = pd.read_excel(file, sheet_name=actual_sheet_name)
                    df.columns = [self.standardize_name(col) for col in df.columns]
                    dfs.append(df)
                    self.log(f"      ✓ {os.path.basename(file)} → {actual_sheet_name}: {len(df)} rows")
                except Exception as e:
                    self.log(f"      ❌ Error reading {actual_sheet_name} from {os.path.basename(file)}: {e}")
            
            if dfs:
                combined = pd.concat(dfs, ignore_index=True)
                standardized_sheet = self.standardize_name(sheet_name)
                
                if 'uin' in combined.columns:
                    is_count_based = any(cb_sheet in standardized_sheet for cb_sheet in COUNT_BASED_SHEETS)
                    
                    if not is_count_based and standardized_sheet in ['pi', 'clinics', 'digital', 'healthcare_platforms']:
                        before = len(combined)
                        combined = combined.drop_duplicates(subset=['uin'], keep='last')
                        after = len(combined)
                        if before != after:
                            self.log(f"          Removed {before - after} duplicate UINs (reference sheet)")
                    else:
                        self.log(f"          Kept all {len(combined)} rows (count-based sheet)")
                
                output_name = standardized_sheet + '.csv'
                output_path = os.path.join(self.output_folder, output_name)
                combined.to_csv(output_path, index=False, encoding='utf-8')
                self.log(f"      ✓ Saved {output_name}: {len(combined)} rows, {len(combined.columns)} cols")
    
    def convert_engagement_files(self, engagement_files):
        """Convert engagement files"""
        self.log("\n📅 Converting Engagement Files...")
        
        for file in engagement_files:
            try:
                df = pd.read_excel(file)
                df.columns = [self.standardize_name(col) for col in df.columns]
                
                original_name = os.path.basename(file).replace('.xlsx', '').replace('.xls', '')
                standardized_name = self.standardize_name(original_name) + '.csv'
                
                output_path = os.path.join(self.output_folder, standardized_name)
                df.to_csv(output_path, index=False, encoding='utf-8')
                
                self.log(f"   ✓ {original_name} → {standardized_name}: {len(df)} rows")
            except Exception as e:
                self.log(f"   ❌ Failed to convert {os.path.basename(file)}: {e}")
    
    def get_warnings(self):
        return self.warnings
    
    """"
PSIms v3.8 - PART 2 of 3: Analysis Engine with Data Loading & Scoring

This file contains the PSImsEngine class initialization, data loading,
aggregation, and scoring logic. Clustering and PDF generation in Part 3.
"""

class PSImsEngine:
    """Core analytics engine with PDF report generation"""
    
    def __init__(self, csv_folder, output_folder, log_callback, 
                 eligibility_mode, require_engagement,
                 naming_method, high_threshold, low_threshold,
                 show_quality_metrics, generate_visualizations,
                 zero_data_position, selected_csv_files, 
                 selected_specialty='All Specialties'):
        
        self.csv_folder = csv_folder
        self.output_folder = output_folder
        self.log = log_callback or print
        self.data = {}
        
        self.eligibility_mode = eligibility_mode
        self.require_engagement = require_engagement
        self.naming_method = naming_method
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.show_quality_metrics = show_quality_metrics
        self.enable_visualizations = generate_visualizations
        self.zero_data_position = zero_data_position
        self.selected_csv_files = selected_csv_files or []
        self.selected_specialty = selected_specialty
        
        self.eligibility_rules = {
            'strict': {'min_buckets': 4},
            'moderate': {'min_buckets': 3},
            'relaxed': {'min_buckets': 2},
            'basic': {'min_buckets': 1},
            'custom': {'min_buckets': 2}
        }
        
        self.log(f"🔧 Engine initialized:")
        self.log(f"   Mode: {self.eligibility_mode}")
        self.log(f"   Specialty Filter: {self.selected_specialty}")
        self.log(f"   Thresholds: High={self.high_threshold}, Low={self.low_threshold}")

    def load_csv(self, filename):
        """Safely load CSV with encoding fallback"""
        filepath = os.path.join(self.csv_folder, filename)
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
                return df
            return pd.DataFrame()
        except:
            try:
                return pd.read_csv(filepath, encoding='latin-1', low_memory=False)
            except:
                return pd.DataFrame()
    
    def should_load_file(self, filename):
        """Check if file should be loaded based on selection"""
        if not self.selected_csv_files or len(self.selected_csv_files) == 0:
            return True
        return filename in self.selected_csv_files
    
    def standardize_uin_column(self, df, is_engagement=False):
        """Standardize UIN column name to lowercase 'uin'"""
        if df.empty:
            return df
        
        for col in df.columns:
            if col.lower() == 'uin':
                if col != 'uin':
                    df = df.rename(columns={col: 'uin'})
                return df
        
        uin_variations = [
            'Client doctor code', 'client doctor code', 'CLIENT DOCTOR CODE',
            'Client_doctor_code', 'client_doctor_code', 'Client_Doctor_Code',
            'Doctor Code', 'doctor code', 'DoctorCode', 'doctorcode',
            'doctor_id', 'DoctorID', 'Doctor_ID',
            'Client Code', 'client code', 'ClientCode'
        ]
        
        for col in df.columns:
            if col in uin_variations:
                df = df.rename(columns={col: 'uin'})
                return df
        
        for col in df.columns:
            col_lower = col.lower().replace('_', '').replace(' ', '')
            if any(term in col_lower for term in ['doctorcode', 'clientcode', 'doctorid']):
                df = df.rename(columns={col: 'uin'})
                return df
        
        return df
    
    def standardize_engagement_columns(self, df):
        """Standardize engagement metric column names"""
        column_mappings = {
            'HCP Email Open Rate': 'hcp_email_open_rate',
            'HCP Email Click Rate': 'hcp_email_click_rate',
            'HCP Whatsapp Read Rate': 'hcp_whatsapp_read_rate',
            'HCP Whatsapp Click Rate': 'hcp_whatsapp_click_rate',
            'HCP Call Productive Rate': 'hcp_call_productive_rate',
            'Average Duration Connected Calls': 'average_duration_connected_calls'
        }
        
        rename_dict = {}
        for col in df.columns:
            for original, standardized in column_mappings.items():
                if col.lower() == original.lower():
                    rename_dict[col] = standardized
                    break
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
        
        return df
    
    def load_all_data(self):
        """Load all CSV files"""
        self.log("\n📂 Loading Data Files...")
        
        files = {
            'pi': 'pi.csv',
            'clinics': 'clinics.csv',
            'publications': 'publication.csv',
            'trials': 'trials.csv',
            'academic_associations': 'academic_association.csv',
            'digital': 'digital.csv',
            'healthcare_platforms': 'healthcare_platforms.csv',
            'awards': 'awards.csv',
            'press': 'press.csv',
            'events': 'events.csv',
            'associations': 'association.csv'
        }
        
        for key, filename in files.items():
            if self.should_load_file(filename):
                self.data[key] = self.load_csv(filename)
                if not self.data[key].empty:
                    self.data[key] = self.standardize_uin_column(self.data[key])
                    if 'uin' in self.data[key].columns:
                        self.log(f"   ✓ {key}: {len(self.data[key])} rows")
                    else:
                        self.log(f"   ⚠️ {key}: No UIN column")
                        self.data[key] = pd.DataFrame()
                else:
                    self.data[key] = pd.DataFrame()
            else:
                self.data[key] = pd.DataFrame()
                self.log(f"   ⊘ {key}: Skipped (not selected)")
        
        engagement_files = [f for f in os.listdir(self.csv_folder) 
                          if f.endswith('.csv') and self.should_load_file(f) and
                          any(month in f.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                                               'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])]
        
        engagement_dfs = []
        for eng_file in engagement_files:
            df = self.load_csv(eng_file)
            if not df.empty:
                self.log(f"   📋 {eng_file}: {len(df)} rows")
                df = self.standardize_uin_column(df, is_engagement=True)
                df = self.standardize_engagement_columns(df)
                
                if 'uin' in df.columns:
                    engagement_dfs.append(df)
                    self.log(f"      ✓ {df['uin'].nunique()} unique UINs found")
        
        if engagement_dfs:
            combined = pd.concat(engagement_dfs, ignore_index=True)
            
            expected_cols = {
                'hcp_email_open_rate': 0,
                'hcp_email_click_rate': 0,
                'hcp_whatsapp_read_rate': 0,
                'hcp_whatsapp_click_rate': 0,
                'hcp_call_productive_rate': 0,
                'average_duration_connected_calls': 0
            }
            
            for col, default in expected_cols.items():
                if col not in combined.columns:
                    combined[col] = default
                else:
                    combined[col] = pd.to_numeric(combined[col], errors='coerce').fillna(default)
            
            agg_dict = {col: 'mean' for col in expected_cols.keys()}
            self.data['engagement'] = combined.groupby('uin', as_index=False).agg(agg_dict)
            self.log(f"   ✓ Engagement (averaged): {len(self.data['engagement'])} UINs")
        else:
            self.data['engagement'] = pd.DataFrame()

    def aggregate_by_uin(self):
        self.log("\n🔗 Aggregating by UIN...")
        if self.data['pi'].empty:
            self.log("   ❌ No PI data")
            return pd.DataFrame()
        
        pi_df = self.data['pi'].copy()
        if 'uin_specialty' not in pi_df.columns:
            if 'specialty' in pi_df.columns:
                pi_df.rename(columns={'specialty': 'uin_specialty'}, inplace=True)
            else:
                pi_df['uin_specialty'] = 'Unknown'

        # --- MULTI-SELECT LOGIC START ---
        if self.selected_specialty and self.selected_specialty != "All Specialties":
            original_count = len(pi_df)
            
            # Handle list (Multi-select) vs String (Single/Legacy)
            if isinstance(self.selected_specialty, list):
                # Clean up list and filter
                clean_specs = [str(s).strip().lower() for s in self.selected_specialty]
                pi_df = pi_df[pi_df['uin_specialty'].astype(str).str.strip().str.lower().isin(clean_specs)]
                spec_display = f"{len(clean_specs)} selected specialties"
            else:
                # Legacy string support
                pi_df = pi_df[pi_df['uin_specialty'].astype(str).str.lower() == self.selected_specialty.lower()]
                spec_display = self.selected_specialty

            filtered_count = len(pi_df)
            self.log(f"   🔎 Filtered by {spec_display}: {original_count} → {filtered_count} doctors")
            
            if pi_df.empty:
                self.log("   ❌ No doctors found for selection.")
                return pd.DataFrame()
        # --- MULTI-SELECT LOGIC END ---
        
        master = pi_df[['uin']].drop_duplicates().copy()
        self.log(f"   Master: {len(master)} UINs")
        
        # ... (Rest of the method remains exactly the same as before from 'for metric in...')
        for metric in ['publication_count', 'trial_count', 'academic_association_count',
                       'award_count', 'platform_count', 'total_followers',
                       'healthcare_platform_count', 'press_count', 'event_count', 
                       'association_count']:
            master[metric] = 0
            
        # Helper for counting
        def merge_count(df_key, col_to_check, count_col_name, master_df):
            if not self.data[df_key].empty and 'uin' in self.data[df_key].columns:
                temp_df = self.data[df_key].copy()
                if col_to_check in temp_df.columns:
                    temp_df = temp_df[temp_df[col_to_check].notna() & (temp_df[col_to_check] != '')]
                
                if len(temp_df) > 0:
                    counts = temp_df.groupby('uin').size().reset_index(name=count_col_name)
                    master_df = master_df.merge(counts, on='uin', how='left', suffixes=('', '_new'))
                    master_df[count_col_name] = master_df[f'{count_col_name}_new'].fillna(0)
                    master_df.drop([f'{count_col_name}_new'], axis=1, errors='ignore', inplace=True)
                    self.log(f"   ✓ {df_key.capitalize()}: {(master_df[count_col_name] > 0).sum()} doctors")
            return master_df

        master = merge_count('publications', 'publication_type', 'publication_count', master)
        
        trials_df = self.data['trials']
        t_col = next((c for c in ['trial_type', 'trial_id', 'trial_title'] if c in trials_df.columns), None)
        if t_col:
            t_df = trials_df[trials_df[t_col].notna() & (trials_df[t_col] != '')]
            if len(t_df) > 0:
                cnt = t_df.groupby('uin').size().reset_index(name='trial_count')
                master = master.merge(cnt, on='uin', how='left', suffixes=('', '_new'))
                master['trial_count'] = master['trial_count_new'].fillna(0)
                master.drop(['trial_count_new'], axis=1, inplace=True, errors='ignore')
                self.log(f"   ✓ Trials: {(master['trial_count'] > 0).sum()} doctors")

        master = merge_count('academic_associations', 'association_type', 'academic_association_count', master)
        master = merge_count('awards', 'award_level', 'award_count', master)
        master = merge_count('press', 'press_type', 'press_count', master)
        master = merge_count('events', 'event_type', 'event_count', master)
        master = merge_count('associations', 'association_type', 'association_count', master)
        master = merge_count('healthcare_platforms', 'platform_name', 'healthcare_platform_count', master)

        if not self.data['digital'].empty and 'uin' in self.data['digital'].columns:
            dig = self.data['digital'][(self.data['digital']['uin'].notna()) & (self.data['digital']['uin'] != '')].copy()
            if len(dig) > 0:
                if 'sm_channel' in dig.columns:
                    dig = dig[dig['sm_channel'].notna() & (dig['sm_channel'] != '')]
                    agg = {'platform_count': ('sm_channel', 'nunique')}
                    if 'sm_followers' in dig.columns:
                        dig['sm_followers'] = pd.to_numeric(dig['sm_followers'], errors='coerce').fillna(0)
                        agg['total_followers'] = ('sm_followers', 'sum')
                    d_grp = dig.groupby('uin').agg(**agg).reset_index()
                else:
                    d_grp = dig.groupby('uin').size().reset_index(name='platform_count')
                    d_grp['total_followers'] = 0
                
                master = master.merge(d_grp, on='uin', how='left', suffixes=('_old', ''))
                master.drop([c for c in master.columns if c.endswith('_old')], axis=1, errors='ignore', inplace=True)
                master['platform_count'] = master.get('platform_count', 0).fillna(0)
                master['total_followers'] = master.get('total_followers', 0).fillna(0)
                self.log(f"   ✓ Social Media: {(master['platform_count'] > 0).sum()} doctors")

        if not self.data['healthcare_platforms'].empty and 'uin' in self.data['healthcare_platforms'].columns:
            hc = self.data['healthcare_platforms'].groupby('uin').size().reset_index(name='healthcare_platform_count')
            master = master.merge(hc, on='uin', how='left', suffixes=('', '_new'))
            master['healthcare_platform_count'] = master['healthcare_platform_count_new'].fillna(0)
            master.drop(['healthcare_platform_count_new'], axis=1, errors='ignore', inplace=True)

        if not self.data['engagement'].empty:
            merged = master.merge(self.data['engagement'], on='uin', how='left')
            for col in ['hcp_email_open_rate', 'hcp_email_click_rate', 'hcp_whatsapp_read_rate',
                        'hcp_whatsapp_click_rate', 'hcp_call_productive_rate', 
                        'average_duration_connected_calls']:
                if col in merged.columns:
                    merged[col] = merged[col].fillna(0)
        else:
            merged = master.copy()
            for col in ['hcp_email_open_rate', 'hcp_email_click_rate', 'hcp_whatsapp_read_rate',
                        'hcp_whatsapp_click_rate', 'hcp_call_productive_rate', 
                        'average_duration_connected_calls']:
                merged[col] = 0
        
        pi_cols = ['uin'] + [c for c in ['full_name', 'mobile', 'whatsapp_phone', 
                                     'email_id_1', 'uin_specialty'] if c in pi_df.columns]
        merged = merged.merge(pi_df[pi_cols].drop_duplicates('uin'), on='uin', how='left')
        
        if 'uin_specialty' in merged.columns:
            merged.rename(columns={'uin_specialty': 'specialty'}, inplace=True)

        if not self.data['clinics'].empty and 'uin' in self.data['clinics'].columns:
            clinic_cols = ['uin'] + [c for c in ['clinic_address', 'clinic_city', 'clinic_state'] 
                                   if c in self.data['clinics'].columns]
            if len(clinic_cols) > 1:
                merged = merged.merge(self.data['clinics'][clinic_cols].drop_duplicates('uin'), on='uin', how='left')
                self.log(f"   ✓ Merged clinic data")
        
        merged.fillna(0, inplace=True)
        return merged
    
    def calculate_scores(self, df):
        """Calculate 4 bucket scores"""
        self.log("\n🎯 Calculating Scores...")
        
        def calc_engagement(row):
            config = SCORING_CONFIG['engagement']
            
            email_open = row.get('hcp_email_open_rate', 0) or 0
            email_click = row.get('hcp_email_click_rate', 0) or 0
            wa_read = row.get('hcp_whatsapp_read_rate', 0) or 0
            wa_click = row.get('hcp_whatsapp_click_rate', 0) or 0
            call_prod = row.get('hcp_call_productive_rate', 0) or 0
            call_dur = row.get('average_duration_connected_calls', 0) or 0
            
            if 0 < email_open <= 1:
                email_open = email_open * 100
            if 0 < email_click <= 1:
                email_click = email_click * 100
            if 0 < wa_read <= 1:
                wa_read = wa_read * 100
            if 0 < wa_click <= 1:
                wa_click = wa_click * 100
            if 0 < call_prod <= 1:
                call_prod = call_prod * 100
            
            email_score = (email_open * config['email_open_weight'] + 
                          email_click * config['email_click_weight'])
            wa_score = (wa_read * config['whatsapp_read_weight'] + 
                        wa_click * config['whatsapp_click_weight'])
            
            call_dur_norm = min((call_dur / 60) * 100, 100) if call_dur > 0 else 0
            call_score = (call_prod * config['call_productive_weight'] + 
                          call_dur_norm * config['call_duration_weight'])
            
            final = (email_score * config['final_email_weight'] +
                    wa_score * config['final_whatsapp_weight'] +
                    call_score * config['final_call_weight'])
            
            return round(final, 2)
        
        def calc_academic(row):
            config = SCORING_CONFIG['academic']
            pubs = row.get('publication_count', 0) or 0
            trials = row.get('trial_count', 0) or 0
            acad_assoc = row.get('academic_association_count', 0) or 0
            
            pub_score = min(pubs * config['publication_points_per_item'], 
                           config['publication_max_score'])
            trial_score = min(trials * config['trial_points_per_item'], 
                             config['trial_max_score'])
            assoc_score = min(acad_assoc * config['association_points_per_item'], 
                             config['association_max_score'])
            
            total = pub_score + trial_score + assoc_score
            return round(min(total, config['max_score']), 2)
        
        def calc_social(row):
            config = SCORING_CONFIG['social_media']
            platforms = row.get('platform_count', 0) or 0
            followers = row.get('total_followers', 0) or 0
            hc_platforms = row.get('healthcare_platform_count', 0) or 0
            
            if followers >= config['follower_min_threshold']:
                follower_score = min(np.log10(followers) * config['follower_log_multiplier'],
                                   config['follower_max_score'])
            else:
                follower_score = 0
            
            platform_score = min(platforms * config['platform_points_per_item'],
                               config['platform_max_score'])
            hc_score = min(hc_platforms * config['healthcare_platform_points_per_item'],
                          config['healthcare_platform_max_score'])
            
            total = follower_score + platform_score + hc_score
            return round(min(total, config['max_score']), 2)
        
        def calc_recognition(row):
            config = SCORING_CONFIG['recognition']
            awards = row.get('award_count', 0) or 0
            press = row.get('press_count', 0) or 0
            events = row.get('event_count', 0) or 0
            assoc = row.get('association_count', 0) or 0
            
            award_score = min(awards * config['award_points_per_item'],
                            config['award_max_score'])
            press_score = min(press * config['press_points_per_item'],
                            config['press_max_score'])
            event_score = min(events * config['event_points_per_item'],
                            config['event_max_score'])
            assoc_score = min(assoc * config['association_points_per_item'],
                            config['association_max_score'])
            
            total = award_score + press_score + event_score + assoc_score
            return round(min(total, config['max_score']), 2)
        
        df['engagement_score'] = df.apply(calc_engagement, axis=1)
        df['academic_score'] = df.apply(calc_academic, axis=1)
        df['social_media_score'] = df.apply(calc_social, axis=1)
        df['recognition_score'] = df.apply(calc_recognition, axis=1)
        
        df['engagement_percentile'] = df['engagement_score'].rank(pct=True)
        df['academic_percentile'] = df['academic_score'].rank(pct=True)
        df['social_media_percentile'] = df['social_media_score'].rank(pct=True)
        df['recognition_percentile'] = df['recognition_score'].rank(pct=True)
        
        df['engagement_data_available'] = df['engagement_score'] > 0
        df['academic_data_available'] = (df['publication_count'] + df['trial_count'] + df['academic_association_count']) > 0
        df['social_media_data_available'] = (df['platform_count'] + df['healthcare_platform_count'] + df['total_followers']) > 0
        df['recognition_data_available'] = (df['award_count'] + df['press_count'] + df['event_count'] + df['association_count']) > 0
        
        df['buckets_with_data'] = (df['engagement_data_available'].astype(int) +
                                   df['academic_data_available'].astype(int) +
                                   df['social_media_data_available'].astype(int) +
                                   df['recognition_data_available'].astype(int))
        
        rules = self.eligibility_rules.get(self.eligibility_mode, self.eligibility_rules['relaxed'])
        df['eligible_for_clustering'] = (
            (df['buckets_with_data'] >= rules['min_buckets']) &
            (df['engagement_data_available'] if self.require_engagement else True)
        )
        
        def get_reason(row):
            if row['eligible_for_clustering']:
                return ''
            reasons = []
            if self.require_engagement and not row['engagement_data_available']:
                reasons.append('No engagement data')
            if row['buckets_with_data'] < rules['min_buckets']:
                reasons.append(f"Only {int(row['buckets_with_data'])}/{rules['min_buckets']} buckets")
            return '; '.join(reasons)
        
        df['insufficient_data_reason'] = df.apply(get_reason, axis=1)
        
        self.log(f"   ✓ Scored {len(df)} doctors")
        self.log(f"   Avg Engagement: {df['engagement_score'].mean():.2f}")
        self.log(f"   Avg Academic: {df['academic_score'].mean():.2f}")
        self.log(f"   Avg Social Media: {df['social_media_score'].mean():.2f}")
        self.log(f"   Avg Recognition: {df['recognition_score'].mean():.2f}")
        
        return df
    
    def run_analysis(self, n_clusters=6):
        """Execute complete analysis pipeline"""
        self.log("\n" + "="*60)
        self.log("🚀 STARTING PSIMS ANALYSIS")
        self.log("="*60)
        
        self.load_all_data()
        aggregated = self.aggregate_by_uin()
        
        if aggregated.empty:
            self.log("\n❌ No data to analyze")
            return None, None, None, None  # MUST RETURN 4 VALUES
        
        scored = self.calculate_scores(aggregated)
        clustered, profiles, silhouette = self.perform_clustering(scored, n_clusters)
        
        # This generates the 4 return values
        output_file, profiles_file, summary_file, pdf_file = self.generate_output(clustered, profiles, silhouette)
        
        self.log("\n" + "="*60)
        self.log("✅ ANALYSIS COMPLETE!")
        self.log("="*60)
        
        return output_file, profiles_file, summary_file, pdf_file # MUST RETURN 4 VALUES
    
    """"
PSIms v3.8 - PART 3 of 3: Clustering, PDF Generation & GUI

This file completes the PSImsEngine class with clustering, enhanced profiles,
PDF report generation with 9 pie charts, and the complete GUI.

IMPORTANT: This continues from Part 2. Add these methods to the PSImsEngine class.
"""

# =====================================================
# CONTINUATION OF PSImsEngine CLASS - ADD THESE METHODS
# =====================================================

    def get_smart_cluster_name(self, cluster_data):
        """Generate smart cluster name using ACTUAL scores and PER-BUCKET thresholds"""
        
        avg_scores = {
            'Engagement': cluster_data['engagement_score'].mean(),
            'Academic': cluster_data['academic_score'].mean(),
            'Social Media': cluster_data['social_media_score'].mean(),
            'Recognition': cluster_data['recognition_score'].mean()
        }
        
        # Identify dominant bucket
        max_score_bucket = max(avg_scores, key=avg_scores.get)
        max_score = avg_scores[max_score_bucket]
        
        # --- NEW THRESHOLD LOGIC START ---
        # Map bucket name to config key
        bucket_key_map = {
            'Engagement': 'engagement',
            'Academic': 'academic',
            'Social Media': 'social_media',
            'Recognition': 'recognition'
        }
        
        # Get specific thresholds for the DOMINANT bucket
        config_key = bucket_key_map.get(max_score_bucket, 'engagement')
        high_thresh = SCORING_CONFIG[config_key].get('high_threshold', 30)
        low_thresh = SCORING_CONFIG[config_key].get('low_threshold', 15)
        # --- NEW THRESHOLD LOGIC END ---

        all_scores = list(avg_scores.values())
        
        # Use the specific low threshold of the dominant bucket (or check all?)
        # For "Low Activity", we generally check if EVERYTHING is low. 
        # We'll use a conservative general low (15) or the min of all lows.
        if all(score < 15 for score in all_scores): # Keeping strict 15 for global low
            return "Low Activity Profile"
        
        buckets_with_data = sum(1 for score in all_scores if score > 5)
        if buckets_with_data == 1:
            return f"Single-Bucket: {max_score_bucket}"
        
        score_range = max(all_scores) - min(all_scores)
        if score_range < 10 and max_score < 25:
            return "Balanced Low Profile"
        elif score_range < 10:
            return "Balanced Profile"
        
        # Use Specific Thresholds
        if max_score > high_thresh:
            return f"{max_score_bucket}-Focused"
        elif max_score > low_thresh:
            return f"{max_score_bucket}-Leaning"
        else:
            return f"Low {max_score_bucket}"
    
    def perform_clustering(self, df, n_clusters=6):
        """Cluster with proper naming"""
        self.log(f"\n🔍 Clustering (k={n_clusters}, mode={self.eligibility_mode})...")
        
        zero_data = df[df['buckets_with_data'] == 0].copy()
        has_data = df[df['buckets_with_data'] > 0].copy()
        
        self.log(f"   Zero-data doctors: {len(zero_data)}")
        self.log(f"   Doctors with data: {len(has_data)}")
        
        cluster_profiles = []
        silhouette_scores = {}
        
        if len(zero_data) > 0:
            if self.zero_data_position == 'exclude':
                self.log("   ⊘ Zero-data doctors excluded from output")
            else:
                if self.zero_data_position == 'first':
                    zero_data['cluster_id'] = 1
                    zero_data['cluster_name'] = 'Cluster 1: No Data'
                elif self.zero_data_position == 'last':
                    zero_data['cluster_id'] = n_clusters
                    zero_data['cluster_name'] = f'Cluster {n_clusters}: No Data'
                else:
                    zero_data['cluster_id'] = 0
                    zero_data['cluster_name'] = 'Cluster 0: No Data'
                
                cluster_profiles.append({
                    'cluster_id': zero_data['cluster_id'].iloc[0],
                    'count': len(zero_data),
                    'avg_engagement': 0,
                    'avg_academic': 0,
                    'avg_social_media': 0,
                    'avg_recognition': 0,
                    'cluster_name': zero_data['cluster_name'].iloc[0]
                })
        
        if len(has_data) >= (n_clusters - 1):
            score_cols = ['engagement_score', 'academic_score', 'social_media_score', 'recognition_score']
            for col in score_cols:
                has_data[col] = has_data[col].fillna(0)
            
            features = has_data[score_cols].values
            features = np.nan_to_num(features, nan=0.0)
            
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            if self.zero_data_position == 'exclude' or len(zero_data) == 0:
                kmeans_clusters = n_clusters
                cluster_id_offset = 1
            else:
                kmeans_clusters = n_clusters - 1
                cluster_id_offset = 2 if self.zero_data_position == 'first' else 1
            
            kmeans = KMeans(n_clusters=kmeans_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)
            has_data['cluster_id'] = clusters + cluster_id_offset
            
            if self.show_quality_metrics and len(has_data) > kmeans_clusters:
                try:
                    silhouette_avg = silhouette_score(features_scaled, clusters)
                    silhouette_scores['overall'] = silhouette_avg
                    self.log(f"   📊 Silhouette Score: {silhouette_avg:.3f}")
                except:
                    pass
            
            for i in range(kmeans_clusters):
                cluster_data = has_data[has_data['cluster_id'] == i + cluster_id_offset]
                
                cluster_name = self.get_smart_cluster_name(cluster_data)
                full_cluster_name = f"Cluster {i + cluster_id_offset}: {cluster_name}"
                
                has_data.loc[has_data['cluster_id'] == i + cluster_id_offset, 'cluster_name'] = full_cluster_name
                
                profile = {
                    'cluster_id': i + cluster_id_offset,
                    'count': len(cluster_data),
                    'avg_engagement': cluster_data['engagement_score'].mean(),
                    'avg_academic': cluster_data['academic_score'].mean(),
                    'avg_social_media': cluster_data['social_media_score'].mean(),
                    'avg_recognition': cluster_data['recognition_score'].mean(),
                    'cluster_name': full_cluster_name
                }
                cluster_profiles.append(profile)
                self.log(f"   {full_cluster_name}: {len(cluster_data)} doctors")
        else:
            has_data['cluster_id'] = 1 if self.zero_data_position != 'first' else 2
            has_data['cluster_name'] = f"Cluster {has_data['cluster_id'].iloc[0]}: Mixed Profile"
            cluster_profiles.append({
                'cluster_id': has_data['cluster_id'].iloc[0],
                'count': len(has_data),
                'avg_engagement': has_data['engagement_score'].mean(),
                'avg_academic': has_data['academic_score'].mean(),
                'avg_social_media': has_data['social_media_score'].mean(),
                'avg_recognition': has_data['recognition_score'].mean(),
                'cluster_name': has_data['cluster_name'].iloc[0]
            })
        
        if self.zero_data_position == 'exclude':
            result = has_data
        else:
            result = pd.concat([zero_data, has_data], ignore_index=True) if len(zero_data) > 0 else has_data
        
        return result, cluster_profiles, silhouette_scores
    
    def enhance_cluster_profiles(self, cluster_profiles):
        """Add percentage calculations to cluster profiles DataFrame (YOUR EXCEL FORMULAS)"""
        self.log("\n📊 Enhancing Cluster Profiles with Percentage Calculations...")
        
        profiles_df = pd.DataFrame(cluster_profiles)
        
        # Column I: Sum of all average scores (=SUM(C2:F2))
        profiles_df['sum_of_avg_scores'] = (
            profiles_df['avg_engagement'] + 
            profiles_df['avg_academic'] + 
            profiles_df['avg_social_media'] + 
            profiles_df['avg_recognition']
        )
        
        # Columns J-M: Percentage contribution per cluster (=C2/I2)
        profiles_df['pct_engagement'] = (profiles_df['avg_engagement'] / profiles_df['sum_of_avg_scores'] * 100).round(0).astype(int)
        profiles_df['pct_academic'] = (profiles_df['avg_academic'] / profiles_df['sum_of_avg_scores'] * 100).round(0).astype(int)
        profiles_df['pct_social_media'] = (profiles_df['avg_social_media'] / profiles_df['sum_of_avg_scores'] * 100).round(0).astype(int)
        profiles_df['pct_recognition'] = (profiles_df['avg_recognition'] / profiles_df['sum_of_avg_scores'] * 100).round(0).astype(int)
        
        # Row 7 totals: Sum across all clusters (=SUM(C2:C6))
        total_engagement = profiles_df['avg_engagement'].sum()
        total_academic = profiles_df['avg_academic'].sum()
        total_social_media = profiles_df['avg_social_media'].sum()
        total_recognition = profiles_df['avg_recognition'].sum()
        
        # Row 9: Per-bucket percentage contribution (=C2/C7)
        profiles_df['bucket_pct_engagement'] = (profiles_df['avg_engagement'] / total_engagement * 100).round(0).astype(int) if total_engagement > 0 else 0
        profiles_df['bucket_pct_academic'] = (profiles_df['avg_academic'] / total_academic * 100).round(0).astype(int) if total_academic > 0 else 0
        profiles_df['bucket_pct_social_media'] = (profiles_df['avg_social_media'] / total_social_media * 100).round(0).astype(int) if total_social_media > 0 else 0
        profiles_df['bucket_pct_recognition'] = (profiles_df['avg_recognition'] / total_recognition * 100).round(0).astype(int) if total_recognition > 0 else 0
        
        self.log(f"   ✓ Added all percentage calculations matching Excel formulas")
        
        return profiles_df
    
    def generate_pdf_report(self, profiles_df, timestamp):
        """Generate standardized PDF report (Fixed Size, Top Text, Cluster ID Labels)"""
        
        if not VISUALIZATION_AVAILABLE:
            self.log("\n⚠️ PDF generation skipped - matplotlib not available")
            return None
        
        self.log("\n📄 Generating Multi-Page PDF Report (Standardized Layout)...")
        pdf_file = os.path.join(self.output_folder, f'cluster_analysis_report_{timestamp}.pdf')
        
        try:
            with PdfPages(pdf_file) as pdf:
                plt.style.use('seaborn-v0_8-whitegrid')
                
                # --- PAGE TYPE 1: CLUSTER COMPOSITION ---
                for idx, row in profiles_df.iterrows():
                    # Fixed figure size for every page
                    fig = plt.figure(figsize=(14, 8.5)) 
                    
                    cluster_name = row['cluster_name']
                    
                    labels = ['Engagement', 'Academic', 'Social Media', 'Recognition']
                    sizes = [
                        row['pct_engagement'], row['pct_academic'],
                        row['pct_social_media'], row['pct_recognition']
                    ]
                    
                    # Filter zeros
                    filtered_data = [(l, s) for l, s in zip(labels, sizes) if s > 0]
                    if filtered_data:
                        labels, sizes = zip(*filtered_data)
                        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'][:len(labels)]
                    else:
                        labels, sizes = ['No Data'], [100]
                        colors = ['#CCCCCC']
                    
                    # Title at very top
                    plt.suptitle(f'{cluster_name}\nScore Composition Breakdown', 
                               fontsize=16, fontweight='bold', y=0.95)
                    
                    # *** MOVE DESCRIPTION TO TOP ***
                    summary_text = (
                        f'Physician Count: {row["count"]:,} | Total Influence Score: {row["sum_of_avg_scores"]:.1f}\n'
                        f'Business Insight: This cluster shows how stakeholder value is distributed across the four dimensions.\n'
                        f'Use this to tailor communication and resource allocation.'
                    )
                    
                    props = dict(boxstyle='round', facecolor='wheat', alpha=0.4, pad=0.8)
                    # Coordinates: x=0.5 (center), y=0.87 (near top, below title)
                    fig.text(0.5, 0.87, summary_text, ha='center', va='top', 
                            fontsize=10, style='italic', bbox=props)
                    
                    # *** PUSH CHART DOWN ***
                    # [left, bottom, width, height] -> Start chart lower to leave room at top
                    ax = fig.add_axes([0.1, 0.05, 0.8, 0.75]) 
                    
                    wedges, texts, autotexts = ax.pie(
                        sizes, labels=labels, autopct='%1.0f%%', startangle=90,
                        colors=colors, textprops={'fontsize': 12, 'weight': 'bold'},
                        explode=[0.05] * len(sizes)
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                    
                    # Legend with scores
                    legend_labels = []
                    for i, label in enumerate(labels):
                        avg_score = row[f"avg_{label.lower().replace(' ', '_')}"]
                        legend_labels.append(f'{label}: {sizes[i]}% (Avg Score: {avg_score:.1f})')
                    
                    # anchor (1.05, 0.0) means bottom-left corner of legend is at bottom-right of chart
                    ax.legend(legend_labels, loc='lower left', bbox_to_anchor=(1.05, 0.0), 
                            fontsize=11, title="Score Details")
                    
                    # Save WITHOUT 'tight' to enforce strict 11x8.5 size
                    pdf.savefig(fig) 
                    plt.close()
                
                # --- PAGE TYPE 2: BUCKET DOMINANCE ---
                bucket_names = ['Engagement', 'Academic', 'Social Media', 'Recognition']
                bucket_cols = ['bucket_pct_engagement', 'bucket_pct_academic', 
                              'bucket_pct_social_media', 'bucket_pct_recognition']
                bucket_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
                
                for bucket_name, bucket_col, main_color in zip(bucket_names, bucket_cols, bucket_colors):
                    fig = plt.figure(figsize=(14, 8.5))
                    
                    # *** FIX LABELS: USE FULL NAME (Cluster ID + Name) ***
                    cluster_labels = profiles_df['cluster_name'].tolist() # No more .split(':')
                    sizes = profiles_df[bucket_col].tolist()
                    
                    filtered_data = [(l, s) for l, s in zip(cluster_labels, sizes) if s > 0]
                    if filtered_data:
                        cluster_labels, sizes = zip(*filtered_data)
                        colors = plt.cm.Pastel1(np.linspace(0.2, 0.9, len(cluster_labels)))
                    else:
                        cluster_labels, sizes = ['No Data'], [100]
                        colors = ['#CCCCCC']
                    
                    plt.suptitle(f'{bucket_name} Bucket Distribution Across Clusters\n'
                               f'Which Physician Segments Dominate {bucket_name}?',
                               fontsize=16, fontweight='bold', color=main_color, y=0.95)
                    
                    # Description at TOP
                    total_score = profiles_df[f'avg_{bucket_name.lower().replace(" ", "_")}'].sum()
                    top_cluster_idx = profiles_df[bucket_col].idxmax()
                    top_cluster_name = profiles_df.loc[top_cluster_idx, 'cluster_name']
                    
                    summary_text = (
                        f'Total {bucket_name} Score: {total_score:.1f} | Dominant: {top_cluster_name}\n'
                        f'Larger slices indicate physician groups with higher cumulative {bucket_name.lower()} scores.\n'
                        f'Focus engagement resources on dominant segments.'
                    )
                    
                    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.3, pad=0.8)
                    fig.text(0.5, 0.87, summary_text, ha='center', va='top', 
                            fontsize=10, style='italic', bbox=props)
                    
                    ax = fig.add_axes([0.1, 0.05, 0.8, 0.75])
                    
                    wedges, texts, autotexts = ax.pie(
                        sizes, labels=cluster_labels, autopct='%1.0f%%', startangle=90,
                        colors=colors, textprops={'fontsize': 10}, pctdistance=0.85
                    )
                    
                    for autotext in autotexts:
                        autotext.set_fontsize(9)
                        autotext.set_weight('bold')
                    
                    # Legend with IDs
                    legend_labels = [f'{l}: {s}%' for l, s in zip(cluster_labels, sizes)]
                    # Legend bottom-right
                    ax.legend(legend_labels, loc='lower left', bbox_to_anchor=(1.05, 0.0), 
                            title='Cluster Contribution', fontsize=10)
                    
                    pdf.savefig(fig)
                    plt.close()
                
                # --- PAGE TYPE 3: SUMMARY TABLE (No Changes needed, just standard save) ---
                fig = plt.figure(figsize=(14, 8.5))
                ax = fig.add_subplot(111)
                ax.axis('tight')
                ax.axis('off')
                
                table_data = [['Cluster Name', 'Count', 'Engagement', 'Academic', 'Social', 'Recognition', 'Total']]
                for _, row in profiles_df.iterrows():
                    table_data.append([
                        row['cluster_name'][:35], # Allow longer names
                        f"{row['count']:,}",
                        f"{row['avg_engagement']:.1f}", f"{row['avg_academic']:.1f}",
                        f"{row['avg_social_media']:.1f}", f"{row['avg_recognition']:.1f}",
                        f"{row['sum_of_avg_scores']:.1f}"
                    ])
                
                table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                               colWidths=[0.3, 0.1, 0.12, 0.12, 0.12, 0.12, 0.12])
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 2)
                
                for i in range(7): table[(0, i)].set_facecolor('#2E86AB'); table[(0, i)].set_text_props(color='white', weight='bold')
                
                ax.set_title('Summary Statistics', fontsize=16, fontweight='bold', pad=20)
                pdf.savefig(fig)
                plt.close()

            self.log(f"   ✅ PDF report complete: {pdf_file}")
            return pdf_file
            
        except Exception as e:
            self.log(f"   ❌ PDF generation failed: {e}")
            import traceback
            self.log(traceback.format_exc())
            return None
    
    def create_visualizations(self, df, cluster_profiles):
        """Generate standard cluster visualizations (legacy support)"""
        if not self.enable_visualizations:
            return None
        
        if not VISUALIZATION_AVAILABLE:
            self.log("\n⚠️  Visualization libraries not installed")
            return None
        
        self.log("\n📈 Generating Standard Visualizations...")
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('PSIMS Cluster Analysis - Standard Charts', fontsize=16, fontweight='bold')
            
            # Chart 1: Cluster sizes
            cluster_counts = df['cluster_name'].value_counts()
            axes[0, 0].barh(range(len(cluster_counts)), cluster_counts.values, color='steelblue')
            axes[0, 0].set_yticks(range(len(cluster_counts)))
            axes[0, 0].set_yticklabels([name.split(':')[1].strip() if ':' in name else name 
                                     for name in cluster_counts.index], fontsize=9)
            axes[0, 0].set_xlabel('Number of Physicians')
            axes[0, 0].set_title('Cluster Size Distribution')
            axes[0, 0].grid(axis='x', alpha=0.3)
            
            # Chart 2: Average scores
            profiles_df = pd.DataFrame(cluster_profiles)
            score_cols = ['avg_engagement', 'avg_academic', 'avg_social_media', 'avg_recognition']
            x = np.arange(len(profiles_df))
            width = 0.2
            
            colors_bar = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
            for idx, col in enumerate(score_cols):
                offset = (idx - 1.5) * width
                axes[0, 1].bar(x + offset, profiles_df[col], width, 
                              label=col.replace('avg_', '').replace('_', ' ').title(),
                              color=colors_bar[idx])
            
            axes[0, 1].set_xlabel('Cluster ID')
            axes[0, 1].set_ylabel('Average Score')
            axes[0, 1].set_title('Average Scores by Cluster')
            axes[0, 1].set_xticks(x)
            axes[0, 1].set_xticklabels(profiles_df['cluster_id'])
            axes[0, 1].legend()
            axes[0, 1].grid(axis='y', alpha=0.3)
            
            # Chart 3: Score distributions
            has_data = df[df['buckets_with_data'] > 0]
            score_data = [has_data['engagement_score'], has_data['academic_score'],
                         has_data['social_media_score'], has_data['recognition_score']]
            bp = axes[1, 0].boxplot(score_data, labels=['Engagement', 'Academic', 'Social Media', 'Recognition'],
                                    patch_artist=True)
            for patch, color in zip(bp['boxes'], colors_bar):
                patch.set_facecolor(color)
            axes[1, 0].set_ylabel('Score')
            axes[1, 0].set_title('Score Distribution Across All Physicians')
            axes[1, 0].grid(axis='y', alpha=0.3)
            
            # Chart 4: Data availability
            bucket_counts = df['buckets_with_data'].value_counts().sort_index()
            axes[1, 1].bar(bucket_counts.index, bucket_counts.values, color='teal', alpha=0.7)
            axes[1, 1].set_xlabel('Number of Buckets with Data')
            axes[1, 1].set_ylabel('Number of Physicians')
            axes[1, 1].set_title('Data Availability Distribution')
            axes[1, 1].grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            viz_file = os.path.join(self.output_folder, f'cluster_visualization_{timestamp}.png')
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.log(f"   ✓ Saved: {viz_file}")
            return viz_file
            
        except Exception as e:
            self.log(f"   ⚠️ Visualization generation failed: {e}")
            return None
    
    def generate_output(self, df, cluster_profiles, silhouette_scores):
        """Save comprehensive results with enhanced profiles and PDF"""
        self.log("\n💾 Generating Output Files...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_folder, f'psims_results_{timestamp}.csv')
        
        # Main results CSV
        output_cols = ['uin', 'full_name', 'specialty', 'mobile', 'clinic_city',
                       'engagement_score', 'engagement_percentile', 'engagement_data_available',
                       'academic_score', 'academic_percentile', 'academic_data_available',
                       'social_media_score', 'social_media_percentile', 'social_media_data_available',
                       'recognition_score', 'recognition_percentile', 'recognition_data_available',
                       'buckets_with_data', 'eligible_for_clustering',
                       'cluster_id', 'cluster_name', 'insufficient_data_reason']
        
        output_cols = [c for c in output_cols if c in df.columns]
        output_df = df[output_cols]
        
        output_df.to_csv(output_file, index=False, encoding='utf-8')
        self.log(f"   ✓ Main results: {output_file}")
        
        profiles_file = None
        pdf_file = None
        
        if cluster_profiles:
            # Enhance profiles with percentage calculations
            profiles_df = self.enhance_cluster_profiles(cluster_profiles)
            
            # Save enhanced CSV with all calculations
            profiles_file = os.path.join(self.output_folder, f'cluster_profiles_enhanced_{timestamp}.csv')
            profiles_df.to_csv(profiles_file, index=False, encoding='utf-8')
            self.log(f"   ✓ Enhanced profiles: {profiles_file}")
            
            # Generate PDF report with 9 pie charts
            pdf_file = self.generate_pdf_report(profiles_df, timestamp)
            
            # Console summary
            self.log("\n📊 Cluster Summary:")
            for _, profile in profiles_df.iterrows():
                pct = (profile['count'] / len(df)) * 100
                self.log(f"   • {profile['cluster_name']}: {profile['count']} ({pct:.1f}%)")
                self.log(f"     Composition: Eng={profile['pct_engagement']}% | Acad={profile['pct_academic']}% | "
                        f"Social={profile['pct_social_media']}% | Recog={profile['pct_recognition']}%")
        
        # Summary text file
        summary_file = os.path.join(self.output_folder, f'summary_stats_{timestamp}.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PSIMS ANALYSIS SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Eligibility Mode: {self.eligibility_mode.upper()}\n")
            f.write(f"Require Engagement: {self.require_engagement}\n")
            f.write(f"Naming Method: {self.naming_method}\n")
            f.write(f"Specialty Filter: {self.selected_specialty}\n")
            f.write(f"Thresholds: High={self.high_threshold}, Low={self.low_threshold}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Physicians: {len(df)}\n")
            f.write(f"Eligible for Clustering: {df['eligible_for_clustering'].sum()}\n")
            f.write(f"Insufficient Data: {(~df['eligible_for_clustering']).sum()}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("DATA AVAILABILITY\n")
            f.write("-" * 80 + "\n")
            for bucket in ['engagement', 'academic', 'social_media', 'recognition']:
                col = f'{bucket}_data_available'
                if col in df.columns:
                    count = df[col].sum()
                    pct = (count / len(df)) * 100
                    f.write(f"{bucket.replace('_', ' ').title()}: {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("-" * 80 + "\n")
            f.write("SCORE STATISTICS\n")
            f.write("-" * 80 + "\n")
            for bucket in ['engagement', 'academic', 'social_media', 'recognition']:
                score_col = f'{bucket}_score'
                if score_col in df.columns:
                    f.write(f"\n{bucket.replace('_', ' ').title()}:\n")
                    f.write(f"  Mean: {df[score_col].mean():.2f}\n")
                    f.write(f"  Median: {df[score_col].median():.2f}\n")
                    f.write(f"  Std Dev: {df[score_col].std():.2f}\n")
                    f.write(f"  Min: {df[score_col].min():.2f}\n")
                    f.write(f"  Max: {df[score_col].max():.2f}\n")
            
            if cluster_profiles:
                f.write("\n" + "-" * 80 + "\n")
                f.write("CLUSTER DETAILS\n")
                f.write("-" * 80 + "\n")
                profiles_df = pd.DataFrame(cluster_profiles)
                for _, profile in profiles_df.iterrows():
                    pct = (profile['count'] / len(df)) * 100
                    f.write(f"\n{profile['cluster_name']}\n")
                    f.write(f"  Size: {profile['count']} physicians ({pct:.1f}%)\n")
                    f.write(f"  Avg Engagement: {profile['avg_engagement']:.2f}\n")
                    f.write(f"  Avg Academic: {profile['avg_academic']:.2f}\n")
                    f.write(f"  Avg Social Media: {profile['avg_social_media']:.2f}\n")
                    f.write(f"  Avg Recognition: {profile['avg_recognition']:.2f}\n")
            
            if silhouette_scores and self.show_quality_metrics:
                f.write("\n" + "-" * 80 + "\n")
                f.write("CLUSTER QUALITY METRICS\n")
                f.write("-" * 80 + "\n")
                if 'overall' in silhouette_scores:
                    score = silhouette_scores['overall']
                    f.write(f"Silhouette Score: {score:.3f}\n")
                    if score > 0.7:
                        f.write("Quality: Excellent - Strong cluster separation\n")
                    elif score > 0.5:
                        f.write("Quality: Good - Reasonable cluster structure\n")
                    elif score > 0.3:
                        f.write("Quality: Fair - Weak cluster structure\n")
                    else:
                        f.write("Quality: Poor - Consider reducing cluster count\n")

            # --- NEW SECTION: SCORING PARAMETERS ---
            f.write("\n" + "-" * 80 + "\n")
            f.write("ACTIVE SCORING PARAMETERS (WEIGHTS & THRESHOLDS)\n")
            f.write("-" * 80 + "\n")
            
            # Helper to print dictionary nicely
            def print_config_section(name, config_dict):
                f.write(f"\n[{name.upper()}]\n")
                for key, val in config_dict.items():
                    # Format key for readability (replace underscores with spaces)
                    readable_key = key.replace('_', ' ').title()
                    f.write(f"  {readable_key}: {val}\n")

            if 'SCORING_CONFIG' in globals():
                active_config = SCORING_CONFIG
            else:
                # Fallback if global not found (shouldn't happen in normal flow)
                active_config = DEFAULT_SCORING_CONFIG

            print_config_section("Engagement", active_config['engagement'])
            print_config_section("Academic", active_config['academic'])
            print_config_section("Social Media", active_config['social_media'])
            print_config_section("Recognition", active_config['recognition'])
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        self.log(f"   ✓ Summary text: {summary_file}")
        
        # Generate standard visualizations if enabled
        viz_file = self.create_visualizations(df, cluster_profiles)
        
        return output_file, profiles_file, summary_file, pdf_file




# =====================================================
# GUI APPLICATION (COMPLETE)
# =====================================================

class PSImsGUI:
    """Modern GUI for PSIms v3.8"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PSIMS v3.8 - Production Ready with PDF Reports")
        self.root.geometry("1100x850")
        
        self.config = PSImsConfig()
        self.admin_manager = AdminSettingsManager(self.config)
        self.is_admin_authenticated = False
        
        # Initialize Variables
        self.input_folder_var = tk.StringVar(value=self.config.get_folder('input_folder'))
        self.csv_folder_var = tk.StringVar(value=self.config.get_folder('csv_output'))
        self.results_folder_var = tk.StringVar(value=self.config.get_folder('results_output'))
        
        self.eligibility_var = tk.StringVar(value=self.config.get_setting('eligibility_mode', 'relaxed'))
        self.clusters_var = tk.StringVar(value=str(self.config.get_setting('num_clusters', 6)))
        self.require_eng_var = tk.BooleanVar(value=self.config.get_setting('require_engagement', True))
        self.zero_pos_var = tk.StringVar(value=self.config.get_setting('zero_data_position', 'first'))
        self.naming_var = tk.StringVar(value=self.config.get_setting('naming_method', 'combined'))
        self.high_thresh_var = tk.StringVar(value=str(self.config.get_setting('high_threshold', 30)))
        self.low_thresh_var = tk.StringVar(value=str(self.config.get_setting('low_threshold', 15)))
        
        self.specialty_var = tk.StringVar(value='All Specialties')
        self.show_metrics_var = tk.BooleanVar(value=self.config.get_setting('show_quality_metrics', True))
        self.generate_viz_var = tk.BooleanVar(value=self.config.get_setting('generate_visualizations', False))
        
        self.selected_pi_files = []
        self.selected_eng_files = []
        self.selected_csv_files = []
        
        self.create_widgets()

    def create_widgets(self):
        # Header
        if THEME_AVAILABLE:
            header_frame = ttk.Frame(self.root, bootstyle="secondary")
            header_frame.pack(fill='x', ipady=10)
            ttk.Label(header_frame, text=" PSIMS v3.8 - PDF Reports & Enhanced Analytics ", 
                     font=('Helvetica', 16, 'bold'), bootstyle="inverse-secondary").pack(side=tk.LEFT, padx=10)
        else:
            header = tk.Label(self.root, text="PSIMS v3.8 - PDF Reports", font=('Arial', 16, 'bold'), bg='gray', fg='white')
            header.pack(fill='x', ipady=10)
        
        # Tabs Container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.tab_data = ttk.Frame(self.notebook, padding=10)
        self.tab_analysis = ttk.Frame(self.notebook, padding=10)
        self.tab_admin = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_data, text="  1. Data Preparation  ")
        self.notebook.add(self.tab_analysis, text="  2. Analysis & Configuration  ")
        self.notebook.add(self.tab_admin, text="  3. Admin Settings 🔒  ")
        
        self.build_data_tab()
        self.build_analysis_tab()
        self.build_admin_tab()  
        self.build_log_area()
    
    def build_data_tab(self):
        # Folders Section
        lf = ttk.Labelframe(self.tab_data, text="📁 Project Folders", padding=15)
        lf.pack(fill='x', pady=10)
        
        self.create_folder_row(lf, "Raw Input Files:", self.input_folder_var, 'input_folder')
        self.create_folder_row(lf, "CSV Output Folder:", self.csv_folder_var, 'csv_output')
        self.create_folder_row(lf, "Analysis Results:", self.results_folder_var, 'results_output')
        
        # Conversion Section
        lf2 = ttk.Labelframe(self.tab_data, text="🔄 File Conversion Engine", padding=15)
        lf2.pack(fill='x', pady=10)
        
        row1 = ttk.Frame(lf2)
        row1.pack(fill='x', pady=5)
        ttk.Label(row1, text="PI Batch Files:", width=18).pack(side=tk.LEFT)
        self.lbl_pi = ttk.Label(row1, text="None selected", foreground="gray")
        self.lbl_pi.pack(side=tk.LEFT, padx=10, fill='x', expand=True)
        ttk.Button(row1, text="Select Files", command=self.select_pi_files).pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(lf2)
        row2.pack(fill='x', pady=5)
        ttk.Label(row2, text="Engagement Files:", width=18).pack(side=tk.LEFT)
        self.lbl_eng = ttk.Label(row2, text="None selected", foreground="gray")
        self.lbl_eng.pack(side=tk.LEFT, padx=10, fill='x', expand=True)
        ttk.Button(row2, text="Select Files", command=self.select_engagement_files).pack(side=tk.RIGHT)
        
        if THEME_AVAILABLE:
            ttk.Button(lf2, text="▶ RUN CONVERSION PIPELINE", command=self.run_conversion, 
                      bootstyle="success").pack(pady=15, fill='x')
        else:
            tk.Button(lf2, text="RUN CONVERSION", command=self.run_conversion, 
                      bg='green', fg='white').pack(pady=15, fill='x')
            
        self.convert_progress = ttk.Progressbar(lf2, mode='indeterminate', length=300)

    def build_analysis_tab(self):
        lf = ttk.Labelframe(self.tab_analysis, text="⚙️ Analysis Configuration", padding=15)
        lf.pack(fill='x', pady=10)
        
        # Row 0: Specialty Filter (MULTI-SELECT UPDATE)
        ttk.Label(lf, text="Filter Specialty:", font=('Arial', 10, 'bold'), 
                 foreground='#d35400').grid(row=0, column=0, sticky='w', pady=10)
        
        self.selected_specialty_list = [] 
        
        def open_specialty_selector():
            p = os.path.join(self.csv_folder_var.get(), 'pi.csv')
            if not os.path.exists(p):
                messagebox.showerror("Error", "PI.csv not found!")
                return
            
            try:
                df = pd.read_csv(p, usecols=lambda c: c.lower() in ['specialty','uin_specialty'])
                col = df.columns[0]
                all_specs = sorted([str(x).strip() for x in df[col].dropna().unique() if str(x).strip()])
            except:
                all_specs = []

            # Pop-up window
            top = tk.Toplevel(self.root)
            top.title("Select Specialties")
            top.geometry("400x500")
            
            # --- FIX: PACK BUTTON FRAME FIRST ---
            btn_frame = ttk.Frame(top, padding=10)
            btn_frame.pack(side=tk.BOTTOM, fill='x')
            
            vars_dict = {}
            
            def on_done():
                self.selected_specialty_list = [s for s, v in vars_dict.items() if v.get()]
                count = len(self.selected_specialty_list)
                
                if count == 0:
                    self.specialty_var.set("All Specialties")
                    self.selected_specialty_list = [] 
                else:
                    self.specialty_var.set(f"{count} Selected")
                top.destroy()
            
            ttk.Button(btn_frame, text="Done", command=on_done, bootstyle="success").pack(fill='x')
            # ------------------------------------
            
            # Checkbox frame with scroll (Packed AFTER button)
            cv = tk.Canvas(top)
            sb = ttk.Scrollbar(top, orient="vertical", command=cv.yview)
            scroll_f = ttk.Frame(cv)
            
            scroll_f.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
            cv.create_window((0, 0), window=scroll_f, anchor="nw")
            cv.configure(yscrollcommand=sb.set)
            
            sb.pack(side="right", fill="y")
            cv.pack(side="left", fill="both", expand=True)
            
            # "Select All" option
            def toggle_all():
                state = all_var.get()
                for v in vars_dict.values(): v.set(state)

            all_var = tk.BooleanVar()
            ttk.Checkbutton(scroll_f, text="Select All", variable=all_var, command=toggle_all).pack(anchor='w', padx=5, pady=2)
            ttk.Separator(scroll_f).pack(fill='x', pady=5)

            for spec in all_specs:
                var = tk.BooleanVar(value=spec in self.selected_specialty_list)
                vars_dict[spec] = var
                ttk.Checkbutton(scroll_f, text=spec, variable=var).pack(anchor='w', padx=10)

        self.lbl_spec_display = ttk.Entry(lf, textvariable=self.specialty_var, state='readonly', width=30)
        self.lbl_spec_display.grid(row=0, column=1, padx=10, sticky='w')
        ttk.Button(lf, text="Select Specialties...", command=open_specialty_selector).grid(row=0, column=2, padx=5, sticky='w')
        
        # Row 1: CSV Selection
        ttk.Button(lf, text="Select Specific CSVs", command=self.select_csv_files).grid(row=1, column=0, pady=10, sticky='w')
        self.lbl_csv = ttk.Label(lf, text="(Default: All CSVs)", foreground="gray")
        self.lbl_csv.grid(row=1, column=1, padx=10, sticky='w')
        
        # Row 2: Modes
        ttk.Label(lf, text="Eligibility Mode:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Combobox(lf, textvariable=self.eligibility_var, 
                    values=['strict','moderate','relaxed','basic'], 
                    state='readonly', width=15).grid(row=2, column=1, sticky='w', padx=10)
        
        ttk.Checkbutton(lf, text="Require Engagement Data", 
                       variable=self.require_eng_var).grid(row=2, column=2, padx=20, sticky='w')
        
        # Row 3: Clusters
        ttk.Label(lf, text="Clusters:").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Spinbox(lf, from_=3, to=10, textvariable=self.clusters_var, width=5).grid(row=3, column=1, sticky='w', padx=10)
        
        ttk.Label(lf, text="Zero Data Pos:").grid(row=3, column=2, sticky='e', pady=5)
        ttk.Combobox(lf, textvariable=self.zero_pos_var, 
                    values=['first','last','separate','exclude'], 
                    state='readonly', width=10).grid(row=3, column=3, sticky='w', padx=5)
        
        # Row 5: Naming Method
        ttk.Label(lf, text="Naming Method:").grid(row=5, column=0, sticky='w', pady=5)
        ttk.Combobox(lf, textvariable=self.naming_var, 
                    values=['absolute','percentile','combined'], 
                    state='readonly', width=15).grid(row=5, column=1, sticky='w', padx=10)
        
        # Row 6: Toggles
        f_tog = ttk.Frame(lf)
        f_tog.grid(row=6, column=0, columnspan=4, pady=10, sticky='w')
        ttk.Checkbutton(f_tog, text="Show Quality Metrics", 
                       variable=self.show_metrics_var).pack(side=tk.LEFT, padx=5)
        viz_btn = ttk.Checkbutton(f_tog, text="Generate Standard Visualizations", 
                                 variable=self.generate_viz_var)
        viz_btn.pack(side=tk.LEFT, padx=20)
        if not VISUALIZATION_AVAILABLE:
            viz_btn.config(state='disabled')
        
        # PDF Info Box
        info_frame = ttk.Frame(self.tab_analysis)
        info_frame.pack(fill='x', pady=10, padx=10)
        
        if THEME_AVAILABLE:
            info_label = ttk.Label(info_frame, 
                                  text="📄 PDF Report Generation: Enabled (Standardized Layout)\n",
                                  bootstyle="info", font=('Arial', 9, 'italic'))
        else:
            info_label = tk.Label(info_frame, 
                                text="📄 PDF reports enabled", font=('Arial', 9, 'italic'), fg='blue')
        info_label.pack(pady=5)

        # Run Button
        if THEME_AVAILABLE:
            self.btn_run = ttk.Button(self.tab_analysis, text="▶ RUN COMPLETE ANALYSIS", 
                                     command=self.run_analysis, bootstyle="primary", width=30)
        else:
            self.btn_run = tk.Button(self.tab_analysis, text="RUN ANALYSIS", 
                                    command=self.run_analysis, bg='blue', fg='white', width=30)
        self.btn_run.pack(pady=15)
        
        self.analysis_progress = ttk.Progressbar(self.tab_analysis, mode='indeterminate', length=400)

    def build_log_area(self):
        lf = ttk.Labelframe(self.root, text="📋 System Log", padding=5)
        lf.pack(fill='both', expand=True, padx=10, pady=10)
        self.log_text = ScrolledText(lf, height=10, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)

    def create_folder_row(self, parent, label, var, key):
        f = ttk.Frame(parent)
        f.pack(fill='x', pady=2)
        ttk.Label(f, text=label, width=18).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=var).pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        ttk.Button(f, text="...", width=3, command=lambda: self.browse(var, key)).pack(side=tk.LEFT)

    def log(self, msg):
        # Use .after() to safely update the GUI from a background thread
        self.root.after(0, lambda: self._log_internal(msg))

    def _log_internal(self, msg):
        print(msg)
        self.log_text.insert(tk.END, str(msg) + "\n")
        self.log_text.see(tk.END)

    def browse(self, var, key):
        d = filedialog.askdirectory()
        if d:
            var.set(d)
            self.config.update_folder(key, d)

    def select_pi_files(self):
        f = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx *.xls")])
        if f:
            self.selected_pi_files = f
            self.lbl_pi.config(text=f"{len(f)} files selected", foreground='green')

    def select_engagement_files(self):
        f = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx *.xls")])
        if f:
            self.selected_eng_files = f
            self.lbl_eng.config(text=f"{len(f)} files selected", foreground='green')

    def select_csv_files(self):
        d = self.csv_folder_var.get()
        if not os.path.exists(d):
            return messagebox.showerror("Error", "Set CSV Folder first")
        f = filedialog.askopenfilenames(initialdir=d, filetypes=[("CSV", "*.csv")])
        if f:
            self.selected_csv_files = [os.path.basename(x) for x in f]
            self.lbl_csv.config(text=f"{len(f)} CSVs selected", foreground='green')

    def run_conversion(self):
        if not self.selected_pi_files and not self.selected_eng_files:
            return messagebox.showwarning("Warning", "No files selected")
        
        # Start the progress bar on the main thread
        self.convert_progress.pack(fill='x', pady=5)
        self.convert_progress.start(10)
        self.log_text.delete(1.0, tk.END)
        
        # Define the heavy task to run in the background
        def conversion_task():
            try:
                conv = SmartConverter(self.csv_folder_var.get(), self.log)
                if self.selected_pi_files:
                    conv.combine_pi_batches(self.selected_pi_files)
                if self.selected_eng_files:
                    conv.convert_engagement_files(self.selected_eng_files)
                
                # Update UI on success (must use root.after)
                self.root.after(0, lambda: self.populate_specialties())
                self.root.after(0, lambda: messagebox.showinfo("Success", "Conversion Complete! ✅"))
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                # Stop progress bar safely
                self.root.after(0, self.stop_conversion_progress)

        # Launch the thread
        threading.Thread(target=conversion_task, daemon=True).start()

    def stop_conversion_progress(self):
        self.convert_progress.stop()
        self.convert_progress.pack_forget()

    def populate_specialties(self):
        p = os.path.join(self.csv_folder_var.get(), 'pi.csv')
        s = ['All Specialties']
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, usecols=lambda c: c.lower() in ['specialty','uin_specialty'])
                col = df.columns[0]
                vals = df[col].dropna().unique()
                s += sorted([str(x).strip() for x in vals if str(x).strip()])
                self.log(f"✓ Loaded {len(s)-1} specialties from PI data.")
            except Exception as e:
                self.log(f"⚠️ Could not load specialties: {e}")
        self.cb_spec['values'] = s
        self.cb_spec.current(0)

    def run_analysis(self):
        # 1. Check for Matplotlib (Main Thread)
        if not VISUALIZATION_AVAILABLE:
            response = messagebox.askyesno(
                "Warning",
                "Matplotlib is not installed. PDF reports will NOT be generated.\n\n"
                "Install with: pip install matplotlib seaborn\n\n"
                "Continue without PDF reports?"
            )
            if not response:
                return
        
        # 2. CAPTURE SETTINGS (Main Thread)
        # We MUST read all UI variables HERE, before the thread starts.
        settings = {
            'csv_folder': self.csv_folder_var.get(),
            'results_folder': self.results_folder_var.get(),
            'eligibility': self.eligibility_var.get(),
            'clusters': int(self.clusters_var.get()),
            'req_engagement': self.require_eng_var.get(),
            'zero_pos': self.zero_pos_var.get(),
            'naming': self.naming_var.get(),
            'high_th': int(self.high_thresh_var.get()),
            'low_th': int(self.low_thresh_var.get()),
            'show_metrics': self.show_metrics_var.get(),
            'gen_viz': self.generate_viz_var.get(),
            'specialty': self.selected_specialty_list if self.selected_specialty_list else "All Specialties",
            'selected_csvs': list(self.selected_csv_files) if self.selected_csv_files else []
        }

        # 3. Save config (Fast enough to do on Main Thread)
        try:
            self.config.update_setting('eligibility_mode', settings['eligibility'])
            self.config.update_setting('num_clusters', settings['clusters'])
            self.config.update_setting('require_engagement', settings['req_engagement'])
            self.config.update_setting('zero_data_position', settings['zero_pos'])
            self.config.update_setting('naming_method', settings['naming'])
            self.config.update_setting('high_threshold', settings['high_th'])
            self.config.update_setting('low_threshold', settings['low_th'])
            self.config.update_setting('show_quality_metrics', settings['show_metrics'])
            self.config.update_setting('generate_visualizations', settings['gen_viz'])
        except Exception as e:
            print(f"Config save warning: {e}")

        # 4. Prepare UI
        self.analysis_progress.pack(fill='x', pady=5)
        self.analysis_progress.start(10)
        self.log_text.delete(1.0, tk.END)
        self.btn_run.config(state='disabled') # Disable button

        # 5. Define the Background Task
        def analysis_task():
            try:
                # Update global scoring config
                global SCORING_CONFIG
                SCORING_CONFIG = self.admin_manager.get_scoring_config()
                
                # Initialize Engine with CAPTURED settings
                engine = PSImsEngine(
                    settings['csv_folder'],
                    settings['results_folder'],
                    self.log,
                    settings['eligibility'],
                    settings['req_engagement'],
                    settings['naming'],
                    settings['high_th'],
                    settings['low_th'],
                    settings['show_metrics'],
                    settings['gen_viz'],
                    settings['zero_pos'],
                    settings['selected_csvs'],
                    settings['specialty']
                )
                
                # RUN THE HEAVY ANALYSIS
                out, prof, smry, pdf = engine.run_analysis(settings['clusters'])
                
                # Success Handler
                def on_success():
                    if out:
                        msg = "✅ Analysis Complete!\n\n"
                        msg += f"Results saved to:\n{settings['results_folder']}\n\n"
                        if pdf:
                            msg += "📄 PDF Report with 9 pie charts generated successfully!"
                        else:
                            msg += "⚠️ PDF report not generated (matplotlib not available)"
                        messagebox.showinfo("Success", msg)
                    else:
                        messagebox.showwarning("Warning", "No output generated. Check log for details.")

                self.root.after(0, on_success)

            except Exception as e:
                import traceback
                err_msg = traceback.format_exc()
                self.log(f"❌ Error: {e}\n{err_msg}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed:\n{str(e)}"))
            
            finally:
                self.root.after(0, self.stop_analysis_progress)

        # 6. Launch Thread
        threading.Thread(target=analysis_task, daemon=True).start()

    def stop_analysis_progress(self):
        self.analysis_progress.stop()
        self.analysis_progress.pack_forget()
        self.btn_run.config(state='normal')

    def on_tab_changed(self, event):
            """Handle tab change events - check admin authentication for admin tab"""
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            
            if "Admin Settings" in tab_text and not self.is_admin_authenticated:
                # Show login dialog
                if self.show_login_dialog():
                    self.is_admin_authenticated = True
                    self.log("✓ Admin authenticated successfully")
                else:
                    # Switch back to previous tab
                    self.notebook.select(self.tab_analysis)
                    messagebox.showwarning("Access Denied", "Invalid admin password")
    
    def show_login_dialog(self):
        """Show password dialog for admin access (Dynamic Sizing)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Admin Authentication")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Build UI first so we know the size
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="🔒 Admin Access Required", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        ttk.Label(main_frame, text="Enter admin password to continue:").pack(pady=5)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, show="●", width=30, font=('Arial', 12))
        password_entry.pack(pady=10)
        password_entry.focus()
        
        result = {'authenticated': False}
        
        def check_password():
            if self.admin_manager.verify_password(password_var.get()):
                result['authenticated'] = True
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password!", parent=dialog)
                password_entry.delete(0, tk.END)
        
        def on_cancel():
            dialog.destroy()
        
        password_entry.bind('<Return>', lambda e: check_password())
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        if THEME_AVAILABLE:
            ttk.Button(btn_frame, text="Login", command=check_password, bootstyle="success", width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancel", command=on_cancel, bootstyle="secondary", width=12).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Login", command=check_password, bg='green', fg='white', width=12).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Cancel", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, font=('Arial', 8, 'italic'), foreground='gray').pack(pady=5)
        
        # Calculate size dynamically
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.wait_window()
        return result['authenticated']
    
    def build_admin_tab(self):
        """Build the admin settings interface with sub-tabs and scrolling (FIXED WIDTH)"""
        
        # Initialize variables FIRST
        self.admin_vars = {}

        # --- SCROLLING MECHANISM START ---
        canvas = tk.Canvas(self.tab_admin)
        scrollbar = ttk.Scrollbar(self.tab_admin, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # *** THE GAP FIX ***
        def _configure_width(event):
            if canvas.winfo_exists():
                canvas.itemconfig(frame_id, width=event.width)

        canvas.bind("<Configure>", _configure_width)

        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.tab_admin.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.tab_admin.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        # --- SCROLLING MECHANISM END ---

        # NOTE: All widgets below use 'scrollable_frame' as parent
        
        if THEME_AVAILABLE:
            info_frame = ttk.Frame(scrollable_frame, bootstyle="warning")
        else:
            info_frame = ttk.Frame(scrollable_frame, relief='solid', borderwidth=2)
        info_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Label(info_frame, text="⚠️ Admin Settings - Changes apply immediately to all future analyses", 
                 font=('Arial', 11, 'bold'), foreground='#e67e22').pack(pady=8)
        
        self.admin_notebook = ttk.Notebook(scrollable_frame)
        self.admin_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.admin_tab_engagement = ttk.Frame(self.admin_notebook, padding=15)
        self.admin_tab_academic = ttk.Frame(self.admin_notebook, padding=15)
        self.admin_tab_social = ttk.Frame(self.admin_notebook, padding=15)
        self.admin_tab_recognition = ttk.Frame(self.admin_notebook, padding=15)
        
        self.admin_notebook.add(self.admin_tab_engagement, text="  Engagement Scoring  ")
        self.admin_notebook.add(self.admin_tab_academic, text="  Academic Scoring  ")
        self.admin_notebook.add(self.admin_tab_social, text="  Social Media Scoring  ")
        self.admin_notebook.add(self.admin_tab_recognition, text="  Recognition Scoring  ")
        
        self.build_engagement_settings()
        self.build_academic_settings()
        self.build_social_settings()
        self.build_recognition_settings()
        
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=20)
        
        if THEME_AVAILABLE:
            ttk.Button(btn_frame, text="💾 Save All Changes", command=self.save_admin_settings, 
                      bootstyle="success", width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="🔄 Reset to Defaults", command=self.reset_to_defaults, 
                      bootstyle="warning", width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="🔐 Change Password", command=self.change_admin_password, 
                      bootstyle="info", width=20).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Save All Changes", command=self.save_admin_settings, 
                      bg='green', fg='white', width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Reset to Defaults", command=self.reset_to_defaults, 
                      bg='orange', fg='white', width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Change Password", command=self.change_admin_password, 
                      bg='blue', fg='white', width=20).pack(side=tk.LEFT, padx=5)
        
        self.load_current_config()
    
    def create_param_row(self, parent, label, var_name, default_val, min_val, max_val, description, is_weight=False):
        """Create a parameter configuration row with validation"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5)
        
        # Label
        ttk.Label(frame, text=label, width=30, anchor='w').pack(side=tk.LEFT)
        
        # Input
        var = tk.DoubleVar(value=default_val)
        self.admin_vars[var_name] = var
        
        if is_weight:
            spinbox = ttk.Spinbox(frame, from_=min_val, to=max_val, increment=0.01, 
                                  textvariable=var, width=10, format="%.2f")
        else:
            spinbox = ttk.Spinbox(frame, from_=min_val, to=max_val, increment=1, 
                                  textvariable=var, width=10, format="%.0f")
        spinbox.pack(side=tk.LEFT, padx=10)
        
        # Range info
        range_text = f"Range: {min_val}-{max_val}"
        if is_weight:
            range_text += " (Weight: 0-1)"
        ttk.Label(frame, text=range_text, foreground='gray', font=('Arial', 8)).pack(side=tk.LEFT, padx=5)
        
        # Info icon with tooltip
        info_label = ttk.Label(frame, text="ℹ️", foreground='blue', cursor='hand2')
        info_label.pack(side=tk.LEFT, padx=5)
        
        # Create tooltip
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip_label = tk.Label(tooltip, text=description, background='#ffffcc', 
                                relief='solid', borderwidth=1, wraplength=300, 
                                justify=tk.LEFT, padx=10, pady=5)
        tooltip_label.pack()
        
        def show_tooltip(event):
            tooltip.deiconify()
            x = event.x_root + 20
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        info_label.bind('<Enter>', show_tooltip)
        info_label.bind('<Leave>', hide_tooltip)
    
    def build_engagement_settings(self):
        """Build engagement scoring settings"""
        ttk.Label(self.admin_tab_engagement, text="Engagement Scoring Configuration", 
                 font=('Arial', 13, 'bold')).pack(pady=10)
        
        ttk.Label(self.admin_tab_engagement, 
                 text="Configure how email, WhatsApp, and call engagement metrics contribute to the total engagement score.",
                 wraplength=600, justify=tk.LEFT).pack(pady=5)
        
        ttk.Separator(self.admin_tab_engagement, orient='horizontal').pack(fill='x', pady=10)
        
        # Email weights
        lf = ttk.Labelframe(self.admin_tab_engagement, text="Email Engagement", padding=10)
        lf.pack(fill='x', pady=10)
        
        self.create_param_row(lf, "Email Open Weight:", 'email_open_weight', 0.50, 0, 1,
                             "Weight for email open rates in calculating email engagement sub-score. Higher = more importance.", True)
        self.create_param_row(lf, "Email Click Weight:", 'email_click_weight', 0.50, 0, 1,
                             "Weight for email click rates. Combined with open weight should total 1.0 for balanced scoring.", True)
        
        # WhatsApp weights
        lf2 = ttk.Labelframe(self.admin_tab_engagement, text="WhatsApp Engagement", padding=10)
        lf2.pack(fill='x', pady=10)
        
        self.create_param_row(lf2, "WhatsApp Read Weight:", 'whatsapp_read_weight', 0.50, 0, 1,
                             "Weight for WhatsApp message read rates in sub-score calculation.", True)
        self.create_param_row(lf2, "WhatsApp Click Weight:", 'whatsapp_click_weight', 0.50, 0, 1,
                             "Weight for WhatsApp link clicks. Should sum to 1.0 with read weight.", True)
        
        # Call weights
        lf3 = ttk.Labelframe(self.admin_tab_engagement, text="Call Engagement", padding=10)
        lf3.pack(fill='x', pady=10)
        
        self.create_param_row(lf3, "Call Productive Weight:", 'call_productive_weight', 0.70, 0, 1,
                             "Weight for productive call rate. Higher weight emphasizes call quality over duration.", True)
        self.create_param_row(lf3, "Call Duration Weight:", 'call_duration_weight', 0.30, 0, 1,
                             "Weight for average call duration. Should sum to 1.0 with productive weight.", True)
        
        # Final weights
        lf4 = ttk.Labelframe(self.admin_tab_engagement, text="Channel Weighting", padding=10)
        lf4.pack(fill='x', pady=10)
        
        self.create_param_row(lf4, "Final Email Weight:", 'final_email_weight', 0.33, 0, 1,
                             "Overall weight of email channel in total engagement score.", True)
        self.create_param_row(lf4, "Final WhatsApp Weight:", 'final_whatsapp_weight', 0.33, 0, 1,
                             "Overall weight of WhatsApp channel. Three weights should sum to ~1.0.", True)
        self.create_param_row(lf4, "Final Call Weight:", 'final_call_weight', 0.34, 0, 1,
                             "Overall weight of call channel in final engagement calculation.", True)
        
        # Max score
        lf5 = ttk.Labelframe(self.admin_tab_engagement, text="Score Ceiling", padding=10)
        lf5.pack(fill='x', pady=10)
        
        self.create_param_row(lf5, "Max Engagement Score:", 'engagement_max_score', 100, 50, 200,
                             "Maximum possible engagement score. Standard is 100 for easy percentage interpretation.", False)

        # --- THRESHOLDS (MOVED TO BOTTOM) ---
        lf_th = ttk.Labelframe(self.admin_tab_engagement, text="Cluster Naming Thresholds", padding=10)
        lf_th.pack(fill='x', pady=10)
        
        self.create_param_row(lf_th, "High Threshold:", 'engagement_high_threshold', 30, 10, 100,
                             "Score above this is considered 'Focused' or 'High' for Engagement.", False)
        self.create_param_row(lf_th, "Low Threshold:", 'engagement_low_threshold', 15, 0, 50,
                             "Score below this is considered 'Low' for Engagement.", False)
    
    def build_academic_settings(self):
        """Build academic scoring settings"""
        ttk.Label(self.admin_tab_academic, text="Academic Scoring Configuration", 
                 font=('Arial', 13, 'bold')).pack(pady=10)
        
        ttk.Label(self.admin_tab_academic,
                 text="Configure scoring for publications, clinical trials, and academic associations.",
                 wraplength=600, justify=tk.LEFT).pack(pady=5)
        
        ttk.Separator(self.admin_tab_academic, orient='horizontal').pack(fill='x', pady=10)
        
        # Publications
        lf = ttk.Labelframe(self.admin_tab_academic, text="Publications", padding=10)
        lf.pack(fill='x', pady=10)
        
        self.create_param_row(lf, "Points Per Publication:", 'publication_points_per_item', 10, 1, 50,
                             "Points awarded for each publication. Multiplied by publication count, capped at max score.", False)
        self.create_param_row(lf, "Publication Max Score:", 'publication_max_score', 50, 10, 100,
                             "Maximum points from publications. Prevents over-weighting prolific publishers.", False)
        
        # Trials
        lf2 = ttk.Labelframe(self.admin_tab_academic, text="Clinical Trials", padding=10)
        lf2.pack(fill='x', pady=10)
        
        self.create_param_row(lf2, "Points Per Trial:", 'trial_points_per_item', 20, 5, 50,
                             "Points per clinical trial involvement. Typically higher than publications due to complexity.", False)
        self.create_param_row(lf2, "Trial Max Score:", 'trial_max_score', 30, 10, 100,
                             "Cap on trial points to balance with other academic activities.", False)
        
        # Academic associations
        lf3 = ttk.Labelframe(self.admin_tab_academic, text="Academic Associations", padding=10)
        lf3.pack(fill='x', pady=10)
        
        self.create_param_row(lf3, "Points Per Association:", 'association_points_per_item', 10, 1, 30,
                             "Points for each academic association membership (e.g., professional societies).", False)
        self.create_param_row(lf3, "Association Max Score:", 'association_max_score', 20, 5, 50,
                             "Maximum points from associations to prevent score inflation.", False)
        
        # Overall
        lf4 = ttk.Labelframe(self.admin_tab_academic, text="Overall Academic Score", padding=10)
        lf4.pack(fill='x', pady=10)
        
        self.create_param_row(lf4, "Max Academic Score:", 'academic_max_score', 100, 50, 200,
                             "Ceiling for total academic score across all categories.", False)
        self.create_param_row(lf4, "Baseline Threshold:", 'baseline_threshold', 10, 0, 50,
                             "Minimum score to be considered academically active. Used for filtering.", False)

        # --- THRESHOLDS (MOVED TO BOTTOM) ---
        lf_th = ttk.Labelframe(self.admin_tab_academic, text="Cluster Naming Thresholds", padding=10)
        lf_th.pack(fill='x', pady=10)
        
        self.create_param_row(lf_th, "High Threshold:", 'academic_high_threshold', 30, 10, 100,
                             "Score above this is considered 'Focused' or 'High' for Academic.", False)
        self.create_param_row(lf_th, "Low Threshold:", 'academic_low_threshold', 15, 0, 50,
                             "Score below this is considered 'Low' for Academic.", False)
    
    def build_social_settings(self):
        """Build social media scoring settings"""
        ttk.Label(self.admin_tab_social, text="Social Media Scoring Configuration",
                 font=('Arial', 13, 'bold')).pack(pady=10)
        
        ttk.Label(self.admin_tab_social,
                 text="Configure scoring for social media presence, followers, and healthcare platforms.",
                 wraplength=600, justify=tk.LEFT).pack(pady=5)
        
        ttk.Separator(self.admin_tab_social, orient='horizontal').pack(fill='x', pady=10)
        
        # Followers
        lf = ttk.Labelframe(self.admin_tab_social, text="Follower Metrics", padding=10)
        lf.pack(fill='x', pady=10)
        
        self.create_param_row(lf, "Follower Log Multiplier:", 'follower_log_multiplier', 10, 1, 50,
                             "Multiplier for log10(followers). Logarithmic scale prevents mega-influencers from dominating.", False)
        self.create_param_row(lf, "Follower Max Score:", 'follower_max_score', 50, 10, 100,
                             "Maximum points from follower count alone.", False)
        self.create_param_row(lf, "Follower Min Threshold:", 'follower_min_threshold', 100, 10, 1000,
                             "Minimum followers required to earn points. Filters out inactive accounts.", False)
        
        # Platform diversity
        lf2 = ttk.Labelframe(self.admin_tab_social, text="Platform Presence", padding=10)
        lf2.pack(fill='x', pady=10)
        
        self.create_param_row(lf2, "Points Per Platform:", 'platform_points_per_item', 10, 1, 30,
                             "Points for each social media platform presence (LinkedIn, Twitter, etc.).", False)
        self.create_param_row(lf2, "Platform Max Score:", 'platform_max_score', 30, 5, 50,
                             "Cap on platform diversity points.", False)
        
        # Healthcare platforms
        lf3 = ttk.Labelframe(self.admin_tab_social, text="Healthcare Platforms", padding=10)
        lf3.pack(fill='x', pady=10)
        
        self.create_param_row(lf3, "Points Per HC Platform:", 'healthcare_platform_points_per_item', 10, 1, 30,
                             "Points for presence on healthcare-specific platforms (Doximity, Sermo, etc.).", False)
        self.create_param_row(lf3, "HC Platform Max Score:", 'healthcare_platform_max_score', 20, 5, 50,
                             "Maximum points from healthcare platforms.", False)
        
        # Overall
        lf4 = ttk.Labelframe(self.admin_tab_social, text="Overall Social Media Score", padding=10)
        lf4.pack(fill='x', pady=10)
        
        self.create_param_row(lf4, "Max Social Media Score:", 'social_media_max_score', 100, 50, 200,
                             "Total ceiling for social media influence score.", False)

        # --- THRESHOLDS (MOVED TO BOTTOM) ---
        lf_th = ttk.Labelframe(self.admin_tab_social, text="Cluster Naming Thresholds", padding=10)
        lf_th.pack(fill='x', pady=10)
        
        self.create_param_row(lf_th, "High Threshold:", 'social_media_high_threshold', 30, 10, 100,
                             "Score above this is considered 'Focused' or 'High' for Social Media.", False)
        self.create_param_row(lf_th, "Low Threshold:", 'social_media_low_threshold', 15, 0, 50,
                             "Score below this is considered 'Low' for Social Media.", False)
    
    def build_recognition_settings(self):
        """Build recognition scoring settings"""
        ttk.Label(self.admin_tab_recognition, text="Recognition Scoring Configuration",
                 font=('Arial', 13, 'bold')).pack(pady=10)
        
        ttk.Label(self.admin_tab_recognition,
                 text="Configure scoring for awards, press mentions, event participation, and professional associations.",
                 wraplength=600, justify=tk.LEFT).pack(pady=5)
        
        ttk.Separator(self.admin_tab_recognition, orient='horizontal').pack(fill='x', pady=10)
        
        # Awards
        lf = ttk.Labelframe(self.admin_tab_recognition, text="Awards & Honors", padding=10)
        lf.pack(fill='x', pady=10)
        
        self.create_param_row(lf, "Points Per Award:", 'award_points_per_item', 15, 1, 50,
                             "Points for each professional award or honor received.", False)
        self.create_param_row(lf, "Award Max Score:", 'award_max_score', 30, 10, 100,
                             "Cap on total award points to balance with other recognition.", False)
        
        # Press
        lf2 = ttk.Labelframe(self.admin_tab_recognition, text="Press & Media", padding=10)
        lf2.pack(fill='x', pady=10)
        
        self.create_param_row(lf2, "Points Per Press Mention:", 'press_points_per_item', 10, 1, 30,
                             "Points for each press mention or media appearance.", False)
        self.create_param_row(lf2, "Press Max Score:", 'press_max_score', 25, 5, 75,
                             "Maximum points from media coverage.", False)
        
        # Events
        lf3 = ttk.Labelframe(self.admin_tab_recognition, text="Event Participation", padding=10)
        lf3.pack(fill='x', pady=10)
        
        self.create_param_row(lf3, "Points Per Event:", 'event_points_per_item', 8, 1, 25,
                             "Points for speaking at or organizing professional events.", False)
        self.create_param_row(lf3, "Event Max Score:", 'event_max_score', 25, 5, 75,
                             "Cap on event participation points.", False)
        
        # Associations
        lf4 = ttk.Labelframe(self.admin_tab_recognition, text="Professional Associations", padding=10)
        lf4.pack(fill='x', pady=10)
        
        self.create_param_row(lf4, "Points Per Association:", 'recognition_association_points_per_item', 5, 1, 20,
                             "Points for membership in professional organizations.", False)
        self.create_param_row(lf4, "Association Max Score:", 'recognition_association_max_score', 20, 5, 50,
                             "Maximum points from association memberships.", False)
        
        # Overall
        lf5 = ttk.Labelframe(self.admin_tab_recognition, text="Overall Recognition Score", padding=10)
        lf5.pack(fill='x', pady=10)
        
        self.create_param_row(lf5, "Max Recognition Score:", 'recognition_max_score', 100, 50, 200,
                             "Total ceiling for professional recognition score.", False)

        # --- THRESHOLDS (MOVED TO BOTTOM) ---
        lf_th = ttk.Labelframe(self.admin_tab_recognition, text="Cluster Naming Thresholds", padding=10)
        lf_th.pack(fill='x', pady=10)
        
        self.create_param_row(lf_th, "High Threshold:", 'recognition_high_threshold', 30, 10, 100,
                             "Score above this is considered 'Focused' or 'High' for Recognition.", False)
        self.create_param_row(lf_th, "Low Threshold:", 'recognition_low_threshold', 15, 0, 50,
                             "Score below this is considered 'Low' for Recognition.", False)
    
    def load_current_config(self):
        config = self.admin_manager.get_scoring_config()
        for bucket in ['engagement', 'academic', 'social_media', 'recognition']:
            for key, value in config[bucket].items():                                
                if key in self.admin_vars:
                    self.admin_vars[key].set(value)
                else:
                    prefixed_name = f"{bucket}_{key}"
                    if prefixed_name in self.admin_vars:
                        self.admin_vars[prefixed_name].set(value)
    
    def save_admin_settings(self):
        """Save all admin settings"""
        try:
            # Build config from UI variables
            new_config = {
                'engagement': {
                    'email_open_weight': self.admin_vars['email_open_weight'].get(),
                    'email_click_weight': self.admin_vars['email_click_weight'].get(),
                    'whatsapp_read_weight': self.admin_vars['whatsapp_read_weight'].get(),
                    'whatsapp_click_weight': self.admin_vars['whatsapp_click_weight'].get(),
                    'call_productive_weight': self.admin_vars['call_productive_weight'].get(),
                    'call_duration_weight': self.admin_vars['call_duration_weight'].get(),
                    'final_email_weight': self.admin_vars['final_email_weight'].get(),
                    'final_whatsapp_weight': self.admin_vars['final_whatsapp_weight'].get(),
                    'final_call_weight': self.admin_vars['final_call_weight'].get(),
                    'max_score': int(self.admin_vars['engagement_max_score'].get()),
                    'high_threshold': int(self.admin_vars['engagement_high_threshold'].get()),
                    'low_threshold': int(self.admin_vars['engagement_low_threshold'].get())
                },
                'academic': {
                    'publication_points_per_item': int(self.admin_vars['publication_points_per_item'].get()),
                    'publication_max_score': int(self.admin_vars['publication_max_score'].get()),
                    'trial_points_per_item': int(self.admin_vars['trial_points_per_item'].get()),
                    'trial_max_score': int(self.admin_vars['trial_max_score'].get()),
                    'association_points_per_item': int(self.admin_vars['association_points_per_item'].get()),
                    'association_max_score': int(self.admin_vars['association_max_score'].get()),
                    'max_score': int(self.admin_vars['academic_max_score'].get()),
                    'baseline_threshold': int(self.admin_vars['baseline_threshold'].get()),
                    'high_threshold': int(self.admin_vars['academic_high_threshold'].get()),
                    'low_threshold': int(self.admin_vars['academic_low_threshold'].get())
                },
                'social_media': {
                    'follower_log_multiplier': int(self.admin_vars['follower_log_multiplier'].get()),
                    'follower_max_score': int(self.admin_vars['follower_max_score'].get()),
                    'follower_min_threshold': int(self.admin_vars['follower_min_threshold'].get()),
                    'platform_points_per_item': int(self.admin_vars['platform_points_per_item'].get()),
                    'platform_max_score': int(self.admin_vars['platform_max_score'].get()),
                    'healthcare_platform_points_per_item': int(self.admin_vars['healthcare_platform_points_per_item'].get()),
                    'healthcare_platform_max_score': int(self.admin_vars['healthcare_platform_max_score'].get()),
                    'max_score': int(self.admin_vars['social_media_max_score'].get()),
                    'high_threshold': int(self.admin_vars['social_media_high_threshold'].get()),
                    'low_threshold': int(self.admin_vars['social_media_low_threshold'].get())
                },
                'recognition': {
                    'award_points_per_item': int(self.admin_vars['award_points_per_item'].get()),
                    'award_max_score': int(self.admin_vars['award_max_score'].get()),
                    'press_points_per_item': int(self.admin_vars['press_points_per_item'].get()),
                    'press_max_score': int(self.admin_vars['press_max_score'].get()),
                    'event_points_per_item': int(self.admin_vars['event_points_per_item'].get()),
                    'event_max_score': int(self.admin_vars['event_max_score'].get()),
                    'association_points_per_item': int(self.admin_vars['recognition_association_points_per_item'].get()),
                    'association_max_score': int(self.admin_vars['recognition_association_max_score'].get()),
                    'max_score': int(self.admin_vars['recognition_max_score'].get()),
                    'high_threshold': int(self.admin_vars['recognition_high_threshold'].get()),
                    'low_threshold': int(self.admin_vars['recognition_low_threshold'].get())
                }
            }
            
            # Validate weights sum to ~1.0
            email_sum = new_config['engagement']['email_open_weight'] + new_config['engagement']['email_click_weight']
            if abs(email_sum - 1.0) > 0.1:
                messagebox.showwarning("Validation Warning", 
                                     f"Email weights sum to {email_sum:.2f}, should be ~1.0")
            
            # Save config
            self.admin_manager.save_scoring_config(new_config)
            self.log("✓ Admin settings saved successfully")
            messagebox.showinfo("Success", "Scoring configuration saved!\n\nChanges will apply to all future analyses.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
            self.log(f"❌ Error saving admin settings: {e}")
    
    def reset_to_defaults(self):
        """Reset scoring config to factory defaults"""
        response = messagebox.askyesno("Confirm Reset", 
                                      "Reset all scoring parameters to factory defaults?\n\n"
                                      "This will overwrite your current custom settings.")
        if response:
            self.admin_manager.reset_to_defaults()
            self.load_current_config()
            self.log("✓ Scoring configuration reset to defaults")
            messagebox.showinfo("Success", "Scoring configuration reset to factory defaults!")
    
    def change_admin_password(self):
        """Show dialog to change admin password (Dynamic Sizing)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Admin Password")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Build UI
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Change Admin Password", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Current password
        ttk.Label(main_frame, text="Current Password:").pack(anchor='w', pady=2)
        current_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=current_var, show="●", width=35).pack(pady=(0, 10))
        
        # New password
        ttk.Label(main_frame, text="New Password (min 6 characters):").pack(anchor='w', pady=2)
        new_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=new_var, show="●", width=35).pack(pady=(0, 10))
        
        # Confirm password
        ttk.Label(main_frame, text="Confirm New Password:").pack(anchor='w', pady=2)
        confirm_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=confirm_var, show="●", width=35).pack(pady=(0, 10))
        
        def do_change():
            if new_var.get() != confirm_var.get():
                messagebox.showerror("Error", "New passwords do not match!", parent=dialog)
                return
            
            success, message = self.admin_manager.change_password(current_var.get(), new_var.get())
            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                self.log("✓ Admin password changed")
                dialog.destroy()
            else:
                messagebox.showerror("Error", message, parent=dialog)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        if THEME_AVAILABLE:
            ttk.Button(btn_frame, text="Change Password", command=do_change, bootstyle="success").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Change Password", command=do_change, bg='green', fg='white').pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Calculate size dynamically
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")


# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    # Initialize scoring config from saved settings
    config_manager = PSImsConfig()
    admin_manager = AdminSettingsManager(config_manager)
    
    # You are already in the global scope, so just assign it directly
    SCORING_CONFIG = admin_manager.get_scoring_config()

    if THEME_AVAILABLE:
        root = ttk.Window(themename="flatly")
    else:
        root = tk.Tk()

    app = PSImsGUI(root)
    root.mainloop()