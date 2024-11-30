import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import numpy as np


log_file = './logs/login.json'

def preprocess(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    window_size = '5min'
    # Filter out rows older than 10 days
    df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
    df = df[df['timestamp'] > pd.Timestamp.now(tz='UTC') - pd.DateOffset(hours=48)]

    # Set timestamp as index for time-based operations
    df.set_index('timestamp', inplace=True)

    failures_per_user = df[df['status'] == 0].groupby(['user_id']).resample('5min').size().reset_index(name='failed_attempts_user')
    failures_per_ip = df[df['status'] == 0].groupby(['ip_address']).resample('5min').size().reset_index(name='failed_attempts_ip')

    df = df.merge(failures_per_user, on=['user_id', 'timestamp'], how='left').merge(failures_per_ip, on=['ip_address', 'timestamp'], how='left')
    df['failed_attempts_user'] = df['failed_attempts_user'].fillna(0)
    df['failed_attempts_ip'] = df['failed_attempts_ip'].fillna(0)

    # Step 2: Compute rolling and EWMA statistics
    df['rolling_failed_mean_user'] = df.groupby('user_id')['status'].rolling(10, min_periods=1).mean().reset_index(level=0, drop=True)
    df['rolling_failed_count_user'] = df.groupby('user_id')['status'].rolling(10, min_periods=1).count().reset_index(level=0, drop=True)
    
    df['failed_ewma_user'] = (
        df.groupby('user_id')['status']
        .apply(lambda x: x.ewm(span=10, adjust=False).mean())
        .reset_index(level=0, drop=True)
    )

    df['failed_ewma_ip'] = (
        df.groupby('ip_address')['status']
        .apply(lambda x: x.ewm(span=10, adjust=False).mean())
        .reset_index(level=0, drop=True)
    )

    # compute for ip also
    df['rolling_failed_mean_ip'] = df.groupby('ip_address')['status'].rolling(10, min_periods=1).mean().reset_index(level=0, drop=True)
    df['rolling_failed_count_ip'] = df.groupby('ip_address')['status'].rolling(10, min_periods=1).count().reset_index(level=0, drop=True)

    # Step 3: Add features for anomaly detection
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['consecutive_failed_attempts_user'] = (
    df['status']
    .eq(-1)  # Check for failed attempts
    .groupby(df['user_id'])  # Group by user_id
    .cumsum()  # Cumulative sum of failures within each group
    .where(df['status'].eq(-1), 0)  # Reset to 0 if the status is not a failure
    )
    df['time_window'] = df['timestamp'].dt.floor(window_size)
    df['is_failed'] = (df['status'] == -1).astype(int)

    failure_counts = (
    df[df['is_failed'] == 1]
    .groupby(['user_id', 'time_window'])
    .size()
    .rename('failures_in_window_user')
    .reset_index()
    )

    failure_counts_ip = (
    df[df['is_failed'] == 1]
    .groupby(['ip_address', 'time_window'])
    .size()
    .rename('failures_in_window_ip')
    .reset_index()
    )

    df = df.merge(failure_counts, how='left', on=['user_id', 'time_window'])
    df = df.merge(failure_counts_ip, how='left', on=['ip_address', 'time_window'])
    df['failures_in_window_user'] = df['failures_in_window_user'].fillna(0)
    df['failures_in_window_ip'] = df['failures_in_window_ip'].fillna(0)
    scaling_factor = 0.5  # Adjust this as needed

    df['consecutive_failed_attempts_ip'] = (
    df['status']
    .eq(-1)  # Check for failed attempts
    .groupby(df['ip_address'])  # Group by ip_address
    .cumsum()  # Cumulative sum of failures within each group
    .where(df['status'].eq(-1), 0)  # Reset to 0 if the status is not a failure
    )

    df['time_since_last_attempt_user'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds()
    df['short_rolling_failed_mean_user'] = df.groupby('user_id')['status'].rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    df['consecutive_failures_user'] = (
        df.groupby('user_id')['is_failed']
        .apply(lambda x: x * (x.groupby((x == 0).cumsum()).cumcount() + 1))
        .reset_index(level=0, drop=True)  # Reset the index to match the original df
    )    
    df['weighted_failures_user'] = np.exp(scaling_factor * df['failures_in_window_user'])
    df['weighted_failures_ip'] = np.exp(scaling_factor * df['failures_in_window_ip'])

    # do same for ip_address
    df['time_since_last_attempt_ip'] = df.groupby('ip_address')['timestamp'].diff().dt.total_seconds()
    df['short_rolling_failed_mean_ip'] = df.groupby('ip_address')['status'].rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    df['consecutive_failures_ip'] = (
        df.groupby('ip_address')['is_failed']
        .apply(lambda x: x * (x.groupby((x == 0).cumsum()).cumcount() + 1))
        .reset_index(level=0, drop=True)  # Reset the index to match the original df
    )    

    # group by user_id, time_window and shrink the data and keep max weighted_failures_user
    df_user = df.groupby(['user_id', 'time_window']).agg({'weighted_failures_user': 'max'}).reset_index()
    df_ip = df.groupby(['ip_address', 'time_window']).agg({'weighted_failures_ip': 'max'}).reset_index()

    return df_user, df_ip

def scale_features(df_user, df_ip):

    # Initialize the StandardScaler
    scaler = StandardScaler()
    scaled_features_user = scaler.fit_transform(df_user[get_features_list("user_id")])
    scaled_features_ip = scaler.fit_transform(df_ip[get_features_list("ip_address")])
    return scaled_features_user, scaled_features_ip

def get_features_list(type: str):
    if type=="user_id":
        # user_features = [
        # 'failed_attempts_user', 'rolling_failed_mean_user', 'rolling_failed_count_user',
        # 'failed_ewma_user', 'hour_of_day', 'day_of_week', 'consecutive_failed_attempts_user', 'weighted_failures_user'
        # ]
        user_features = [
            'weighted_failures_user'
        ]
        return user_features
    elif type=="ip_address":
        # ip_features = [
        # 'failed_attempts_ip', 'rolling_failed_mean_ip', 'rolling_failed_count_ip',
        # 'failed_ewma_ip', 'hour_of_day', 'day_of_week', 'consecutive_failed_attempts_ip', 'weighted_failures_ip'
        # ]
        ip_features = [
            'weighted_failures_ip'
        ]
        return ip_features

def get_model():

    data = pd.read_json(log_file)
    df_user, df_ip = preprocess(data) 

    feature_columns_user = get_features_list("user_id")

    feature_columns_ip = get_features_list("ip_address")

    # scale the features
    scaled_features_user, scaled_features_ip = scale_features(df_user, df_ip)

    # Initialize Isolation Forest model for user_id
    iso_forest_user = IsolationForest(n_estimators=200, contamination=0.01, max_features=0.8, random_state=42)  # You can adjust the contamination parameter

    # Fit the model for user_id
    iso_forest_user.fit(scaled_features_user)

    # Initialize Isolation Forest model for ip_address
    iso_forest_ip = IsolationForest(n_estimators=200, contamination=0.01, max_features=0.8, random_state=42)  # You can adjust the contamination parameter

    # Fit the model for ip_address
    iso_forest_ip.fit(scaled_features_ip)

    return iso_forest_user, iso_forest_ip

def get_predictions(model_user, model_ip, df):
    # preprocess the data[convert timestamp to datetime, sort by user_id and timestamp]
    df_user, df_ip = preprocess(df)

    # scale the features
    scaled_features_user, scaled_features_ip = scale_features(df_user, df_ip)

    # get anomaly scores for user_id
    df_user['anomaly_score_user_id'] = model_user.decision_function(scaled_features_user)

    # get anomaly scores for ip_address
    df_ip['anomaly_score_ip_address'] = model_ip.decision_function(scaled_features_ip)

    # return the predictions for all users and ip addresses
    return df_user, df_ip

