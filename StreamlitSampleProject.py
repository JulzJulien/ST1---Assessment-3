import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from scipy.stats import pearsonr

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import preprocessing

# Import necessary libraries for machine learning models
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import mean_absolute_error

import joblib

## label encoding on dataset


# Caching expensive operations
@st.cache_resource
def train_models(X_train_scaled, y_train):
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(),
        "Random Forest Regressor": RandomForestRegressor(),
        "KNN Regressor": KNeighborsRegressor(),
        "SVM Regressor": SVR()
    }
    trained_models = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        trained_models[name] = model
    return trained_models


@st.cache_resource
def scale_data(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return scaler, X_train_scaled, X_test_scaled


# # Function to clean dataset by converting object columns to appropriate data types
def clean_dataset(data):
#     # Step 1: Convert object columns to numeric where possible, but keep original value if conversion fails
    for col in data.select_dtypes(include=['object']).columns:
#         # Try to convert to numeric, if not possible keep the original value
        data[col] = data[col].apply(lambda x: pd.to_numeric(x, errors='ignore') if isinstance(x, str) else x)

#     # Step 2: Convert columns that may be dates, but keep original value if conversion fails
    for col in data.select_dtypes(include=['object']).columns:
#         # Try to convert to datetime, if not possible keep the original value
        try:
            data[col] = pd.to_datetime(data[col], errors='ignore')
        except:
            pass  # Ignore errors during datetime conversion

#   # Step 3: Remove missing values
    # data = data.dropna()

    # Step 3: Convert object data types to string.
    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].astype('string')

#     # Step 4: Infer remaining object columns
    # data = data.infer_objects()
#
#     # Step 5: Return the cleaned dataset
    return data

label_encoder = preprocessing.LabelEncoder()



# Sidebar for file uploads
st.sidebar.title("Upload Dataset(s)")
uploaded_files = st.sidebar.file_uploader("Choose one or more CSV files", type="csv", accept_multiple_files=True)

# Dictionary to hold multiple datasets
datasets = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Read each uploaded dataset and store it in a dictionary with the filename as the key
        datasets[uploaded_file.name] = pd.read_csv(uploaded_file)

    # Select dataset from uploaded files
    selected_file = st.sidebar.selectbox("Select a dataset to proceed with:", options=list(datasets.keys()))

    # Select the dataset to proceed with
    data = datasets[selected_file]
    data = pd.read_csv('FurniturePricePrediction.csv')
  

    # Clean the dataset (convert object columns to numeric or datetime)
    data_cleaned = clean_dataset(data)

    visual_data = pd.read_csv('FurniturePricePrediction.csv').drop_duplicates()

    visual_data['furniture'] = label_encoder.fit_transform(visual_data['furniture'])
    visual_data['type'] = label_encoder.fit_transform(visual_data['type'])
    visual_data['url'] = label_encoder.fit_transform(visual_data['url'])
    visual_data['sale'] = visual_data['sale'].str.replace('%', '').astype(float)

    logprice = np.log1p(visual_data['price'])
    visual_data['price'] = logprice
    
    # Main section for displaying and processing the selected dataset
    st.title(f"Processing Dataset: Furniture Prices")

    # Step 1: Display a sample of the selected dataset
    st.write("## Step 1: Reading the dataset")

    st.write("#### Firstly, we read the raw and uncleaned data to see what we're dealing with. We do this with the 'pd.read_csv' function.")

    st.dataframe(data_cleaned, use_container_width=True)

    data_cleaned = data.drop_duplicates()          

    # Check and drop "Unnamed: 0" column if it exists
    if "Unnamed: 0" in data_cleaned.columns:
        data_cleaned = data_cleaned.drop(columns=["Unnamed: 0"])
        st.write("Dropped 'Unnamed: 0' column from the dataset.")
        st.dataframe(data_cleaned, use_container_width=True)

    # Display the cleaned data types
    st.write("### Cleaned Data Types")
    dtype_df = pd.DataFrame(data_cleaned.dtypes, columns=["Data Type"]).reset_index().rename(
        columns={"index": "Column Name"})
    st.dataframe(dtype_df, use_container_width=True)

    # Display the shape and columns of the selected dataset
    st.write("### Dataset Information")
    st.write(f"### Shape: `{data_cleaned.shape}`")
    st.write("Columns in the dataset:", data_cleaned.columns.tolist())

    # Step 1: Display a sample of the selected dataset
    st.write("## Cleaned Data for Visualization")

    st.dataframe(visual_data, use_container_width=True)

    # # Step 2: Problem Statement Definition
    # st.write("## Step 2: Problem Statement Definition")
    # target = st.selectbox("Select the target variable (dependent variable):", data_cleaned.columns)
    # st.write(f"### Selected Target Variable: `{target}`")

    # Step 2: Problem Statement Definition
    st.write("## Step 2: Problem Statement Definition")

    # Displaying the problem statement
    st.write("""
    In this project, we aim to predict the price of various furniture items based on features such as
    furniture type, rating, delivery cost, and sale percentage. The goal is to build a machine learning model
    that can accurately estimate the price, which will help in understanding the pricing patterns and
    allow potential buyers or sellers to have an idea of the price range for similar items.
    """)

    # Displaying the shape and columns of the selected dataset
    st.write("### Dataset Information")
    st.write(f"The dataset has a total of {data.shape[0]} rows and {data.shape[1]} columns.")
    st.write("Columns in the dataset:", data.columns.tolist())

    # Defining dependent and independent variables
    # target = "price"
    target = st.selectbox("Select the target variable (dependent variable):", visual_data.columns)

    st.write(f"### Target Variable (Dependent Variable): `{target}`")

    # Step 3 - Visualizing the Target Variable
    st.write("## Step 3: Visualizing the Target Variable")

    fig, ax = plt.subplots()
    ax.hist(visual_data[target], bins=30, edgecolor='k', alpha=0.7)
    ax.set_title(f"Distribution of {target}")
    ax.set_xlabel(target)
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

    # Plot a pairplot of all numeric columns in the dataset
    numeric_cols1 = visual_data.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols1) > 1:
        sns.pairplot(visual_data[numeric_cols1].dropna())
        st.pyplot(plt.gcf())
    else:
        st.write("Not enough numeric variables to plot a pairplot.")
        
    st.write("## Identified and removed unwanted columns: 'url'")
    data_cleaned = data_cleaned.drop('url', axis=1)
    visual_data = visual_data.drop('url', axis=1)
    st.dataframe(data_cleaned, use_container_width=True)

    # Step 4: Basic Data Exploration
    st.write("## Step 4: Data Exploration")

    # Create two columns for data types and summary statistics
    col1, col2 = st.columns(2)

    # Column 1: Data Types
    with col1:
        st.write("### Data Types:")
        # Create a DataFrame for the column names and their corresponding data types
        dtype_df = pd.DataFrame(data_cleaned.dtypes, columns=["Data Type"]).reset_index()
        dtype_df = dtype_df.rename(columns={"index": "Column Name"})

        st.dataframe(dtype_df, use_container_width=True)
        
    # Column 2: Summary Statistics
    with col2:
        st.write("### Summary Statistics:")
        st.dataframe(data_cleaned.describe(), use_container_width=True)

    # Step 5: Visual EDA - Histograms for Continuous Variables
    st.write("## Step 5: Visual EDA - Histograms of Continuous Variables / Bar Plots of Categorical Variables")

    continuous_columns = st.multiselect("Select continuous variables to visualize:",
                                        visual_data.select_dtypes(include=['float64', 'int64']).columns)

    if continuous_columns:
        for column in continuous_columns:
            # Create a new figure for each column
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.hist(visual_data[column], bins=30, edgecolor='k', alpha=0.7)
            ax.set_title(f"Distribution of {column}")
            ax.set_xlabel(column)
            ax.set_ylabel('Frequency')

            # Display the individual figure
            st.pyplot(fig)

    # categorical_columns = st.multiselect("Select categorical variables to visualize:",
    #                                     data_cleaned.select_dtypes(include=['string']).columns)

    # 2. Visualizing Categorical Variables using Bar Plots
    # Identify categorical columns (i.e., columns with object data types)
    categorical_columns = visual_data.select_dtypes(include=['float64', 'int64']).columns


    # If categorical columns are available
    if len(categorical_columns) > 0:
        selected_categorical_columns = st.multiselect(
            "Select categorical variables to visualize with bar plots:",
            categorical_columns
        )

        # Create bar plots for each selected categorical column
        for column in selected_categorical_columns:
            st.write(f"#### Distribution of {column}")
        
            # Create a count plot (bar plot) for each categorical variable
            fig, ax = plt.subplots()
            sns.countplot(x=column, data=visual_data, ax=ax)
            ax.set_title(f"Count of {column}")
            ax.set_xlabel(column)
            ax.set_ylabel('Frequency')
        
            st.pyplot(fig)
    else:
        st.write("No categorical variables available for bar plot visualization.")
        
        # Step 6: Outlier Analysis
    st.write("## Step 6: Outlier Analysis")

    data_cleaned['sale'] = data_cleaned['sale'].str.replace('%', '').astype(float)
    wRate = data_cleaned.copy()

    # Select only continuous numerical columns
    data_cleaned = data_cleaned.drop('rate', axis=1)
    numeric_cols = data_cleaned.select_dtypes(include=['float64', 'int64'])

    if not numeric_cols.empty:
        # Proceed with the outlier analysis if there are numeric columns
        Q1 = numeric_cols.quantile(0.25)
        Q3 = numeric_cols.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Identifying outliers using the IQR method
        outliers = (numeric_cols < (Q1 - 1.5 * IQR)) | (numeric_cols > (Q3 + 1.5 * IQR))

        # Count outliers in each column
        outlier_count = outliers.sum()

        # Display the number of outliers in each column
        st.write("### Number of Outliers in Each Numeric Column")
        dtype_df_outlier = pd.DataFrame(outlier_count, columns=["Number of Outliers"]).reset_index()
        dtype_df_outlier = dtype_df_outlier.rename(columns={"index": "Column Name"})
        st.dataframe(dtype_df_outlier, use_container_width=True)

    else:
        st.write("No continuous numeric columns available for outlier analysis.")

    # Step 7: Missing Value Analysis
    st.write("## Step 7: Missing Value Analysis")
    missing_values = data_cleaned.isnull().sum()
    st.write("### Missing Values in Each Column")
    dtype_df_missing_values = pd.DataFrame(missing_values, columns=["Missing Values"]).reset_index()
    dtype_df_missing_values = dtype_df_missing_values.rename(columns={"index": "Column Name"})
    st.dataframe(dtype_df_missing_values, use_container_width=True)

    st.write("## Dataset after removing outliers and replacing missing values with 0")


    final_data = data_cleaned[~((data_cleaned[numeric_cols.columns] < lower_bound) | (data_cleaned[numeric_cols.columns] > upper_bound)).any(axis=1)]
    # filtered_df = data_cleaned[~(data_cleaned[numeric_cols.columns] < lower_bound) | (data_cleaned[numeric_cols.columns] > upper_bound)]
    # corrDataFrame.insert(x, f"{i}", final_data[i], True)
    final_data.insert(2, 'rate', wRate['rate'],True)
    final_data = final_data.fillna(0)
    st.dataframe(final_data, use_container_width=True)
    
    # Step 8: Feature Selection - Correlation Analysis
    st.write("## Step 8: Feature Selection - Correlation Matrix")

    selected_features = st.multiselect("Select predictor variables (independent variables):",
                                    visual_data.select_dtypes(include=['float64', 'int64']).columns)

    # cleaned_columns = ['price','rate','delivery']
    # selected_features = st.selectbox("Select the predictor variable (independent variables):", [column for column in data_cleaned.columns if column in cleaned_columns])

    # selected_features = st.selectbox("Select the predictor variable (independent variable):", data_cleaned.columns)

    # Select only continuous numerical columns for correlation analysis
    numeric_columns = visual_data.select_dtypes(include=['float64', 'int64'])

    if not numeric_columns.empty:
        # Calculate and display the correlation matrix
        correlation_matrix = numeric_columns.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        
        # if target == 'price' or target == 'rate' or target == 'delivery':
        # #convert the data frame into series 
        #     pearsonTargetVariable = correlation_matrix[target] #converting data frame into series for target variable
        #     pearsonpredictorVariable = correlation_matrix[selected_features] #converting data frame into series for predictor variable

        # st.write(f"{pearsonpredictorVariable, pearsonTargetVariable}")
        #applying the pearson correlation and probability value 

        # corr, p_value = pearsonr(pearsonTargetVariable,pearsonpredictorVariable)
        # st.write(f"Pearson's correlation: {corr}, Probability value: {p_value}")
        
        #defining is probability value is statistically significant or not  
        # if p_value <= 0.05:
        #     st.write("probability value is statistically significant")
        # else:
        #     st.write("probability value is not statistically significant")

        new_visual = final_data.copy()

        new_visual['furniture'] = label_encoder.fit_transform(new_visual['furniture'])
        new_visual['type'] = label_encoder.fit_transform(new_visual['type'])

        logprice = np.log1p(new_visual['price'])
        new_visual['price'] = logprice

        try:     
            # list1 = new_visual[f'{target}']
            # list2 = new_visual[f'{selected_features}']
            
            corrDataFrame = pd.DataFrame(final_data[target])
            
            x = 1
            for i in selected_features:
                corrDataFrame.insert(x, f"{i}", final_data[i], True)
                x = x + 1
                
            # corr, p_value = pearsonr(list1, list2)
            # st.write(f"Pearson's correlation value: {corr:.3f}    probability value: {p_value}")
            
            st.write("## Pearson's Correlation Matrix: Target Variable vs. Predictor Variable(s)")
            
            st.dataframe(corrDataFrame.corr(method='pearson', min_periods=1), use_container_width=True)

            st.scatter_chart(new_visual, x = target, y = selected_features)

            # Display the full correlation matrix
            st.write("### Correlation Matrix:")
            st.dataframe(correlation_matrix, use_container_width=True)

            # Extract correlations with the target variable
            target_correlations = correlation_matrix[target].drop(target)  # Drop correlation of target with itself

            # Display the correlation of each feature with the target variable
            st.write(f"### Correlation of Features with Target Variable: `{target}`")
            st.dataframe(target_correlations, use_container_width=True)

            # Identify strong, moderate, and weak relationships
            strong_corr = target_correlations[target_correlations.abs() >= 0.7]
            moderate_corr = target_correlations[(target_correlations.abs() >= 0.3) & (target_correlations.abs() < 0.7)]
            weak_corr = target_correlations[target_correlations.abs() < 0.3]

            # Display the correlations classified as strong, moderate, and weak
            st.write("### Strong Correlations (|correlation| ≥ 0.7):")
            st.dataframe(strong_corr, use_container_width=True)

            st.write("### Moderate Correlations (0.3 ≤ |correlation| < 0.7):")
            st.dataframe(moderate_corr, use_container_width=True)

            st.write("### Weak Correlations (|correlation| < 0.3):")
            st.dataframe(weak_corr, use_container_width=True)
        except IndexError:
            st.write("## Please select variable.")
    else:
        st.write("No continuous numeric columns available for correlation analysis.")

    # Step 9: Statistical Feature Selection using ANOVA for Categorical Variables
    st.write("## Step 9: Statistical Feature Selection (ANOVA for Categorical Variables)")

    # Select categorical columns for ANOVA analysis
    categorical_columns = final_data.select_dtypes(include=['string'])

    # agg_funcs = {
    #     'price' :'mean'
    # }

    if not categorical_columns.empty:
        selected_categorical = st.multiselect("Select categorical variables for ANOVA:", categorical_columns.columns)

        # Ensure the target variable is continuous
        if pd.api.types.is_numeric_dtype(final_data[target]):
            # Dictionary to store ANOVA results
            anova_results = []

            # Perform ANOVA for each selected categorical variable
            for cat_col in selected_categorical:
                # df_apply=df.groupby(['Outlet_Establishment_Year'])['Item_MRP'].apply(lambda x: x - x.mean())
                
                # anova_groups = pd.DataFrame(final_data[cat_col])
                # anova_groups.insert(1, f"{target}", final_data[target], True)

                anova_groups = final_data.groupby(cat_col)[target].apply(list)
                # df.groupby('Outlet_Location_Type').count()
                # df.groupby('Outlet_Location_Type')['Item_Outlet_Sales']
                # df.groupby('Outlet_Location_Type')['Item_Outlet_Sales'].sum()
                
                # anova_groups = final_data.groupby(cat_col).agg(agg_funcs)
                # anova_groups = final_data.groupby(cat_col).sum()
                
                # anova_groups[f'{cat_col}'] = final_data.groupby(cat_col)[target].transform(np.mean)
                
                st.dataframe(anova_groups)
               
                f_val, p_val = stats.f_oneway(*anova_groups)
    
                # Append the results to a list
                anova_results.append({"Categorical Variable": cat_col, "F-value": f_val, "p-value": p_val})
 

            # Convert results to DataFrame
            anova_df = pd.DataFrame(anova_results)

            # Display the ANOVA results
            st.write("### ANOVA Results")
            st.write("The following table shows F-values and P-values for each categorical variable.")
            st.dataframe(anova_df, use_container_width=True)

            # Display significant variables based on p-value
            if "p-value" in anova_df.columns:
                significant_vars = anova_df[anova_df["p-value"] < 0.05]
                st.write("### Significant Variables (p < 0.05):")
                if not significant_vars.empty:
                    st.dataframe(significant_vars, use_container_width=True)
                else:
                    st.write("No significant variables found.")
                # Visualize the relationship using box plots
                st.write("### Box Plot: Categorical Variable vs Target")
                for cat_col in selected_categorical:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.boxplot(x=cat_col, y=target, data=final_data, ax=ax)
                    ax.set_title(f"{cat_col} vs {target}")
                    st.pyplot(fig)
            else:
                st.write("No categorical variables selected for ANOVA.")

        else:
            st.write("The target variable must be continuous for ANOVA analysis.")
    else:
        st.write("No categorical variables available for ANOVA analysis.")

    # Step 10: Selecting Final Predictors for Building Machine Learning Model
    st.write("## Step 10: Selecting Final Predictors")
    # Ensure that numeric columns are selected
    st.write("### Selected Features:", selected_features)

    # Check if the user selected features and the target variable
    if selected_features:
        st.write(f"### Target Variable: `{target}`")

        # Step 11: Data Preparation for Machine Learning
        st.write("## Step 11: Data Preparation for Machine Learning")
        # Extracting the features and target variable
        X = new_visual[selected_features]
        y = new_visual[target]

        # Splitting the data into train and test sets
        test_size = st.slider("Select the test size (percentage)", min_value=0.1, max_value=0.5, value=0.2, step=0.05)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        # Cache the scaler and scaled data
        scaler, X_train_scaled, X_test_scaled = scale_data(X_train, X_test)
        st.write(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")

        # Step 12: Model Training and Evaluation
        st.write("## Step 12: Model Training and Evaluation")
        # Check if models are already cached, otherwise train and cache them
        if 'trained_models' not in st.session_state:
            st.session_state.trained_models = train_models(X_train_scaled, y_train)

        trained_models = st.session_state.trained_models

        model_performance = {}
        for name, model in trained_models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)

            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)

            # Store the results in the dictionary
            model_performance[name] = {"MSE": mse, "R2 Score": r2, "MAE": mae}

        # Convert the performance dictionary to a pandas DataFrame for better visualization
        performance_df = pd.DataFrame(model_performance).T  # Transpose to get model names as rows

        # Apply styles using pandas built-in styling
        styled_df = performance_df.style.format(precision=2) \
            .background_gradient(subset=["MSE"], cmap="Blues", low=0, high=1) \
            .background_gradient(subset=["R2 Score"], cmap="Greens", low=0, high=1) \
            .background_gradient(subset=["MAE"], cmap="Reds", low=0, high=1) \
            .set_properties(**{'text-align': 'center'}) \
            .set_table_styles([{
            'selector': 'th',
            'props': [('font-size', '14px'), ('text-align', 'center'), ('color', '#ffffff'),
                    ('background-color', '#404040')]
        }])

        # Display the table with st.table or st.dataframe
        st.write("## Model Performance Table")
        st.dataframe(styled_df, use_container_width=True)

        # Step 12: Visualizing the Performance Comparison between Models
        st.write("## Visualizing Model Performance Comparison")

        # Extracting model names and their respective performance metrics
        model_names = list(model_performance.keys())
        mse_values = [model_performance[model]["MSE"] for model in model_names]
        r2_values = [model_performance[model]["R2 Score"] for model in model_names]
        mae_values = [model_performance[model]["MAE"] for model in model_names]

        # Creating a bar plot to compare MSE, R2, and MAE across models
        fig, ax = plt.subplots(3, 1, figsize=(10, 12))

        # MSE Comparison
        ax[0].bar(model_names, mse_values, color='blue')
        ax[0].set_title("Model Comparison: Mean Squared Error (MSE)")
        ax[0].set_ylabel("MSE")

        # R2 Score Comparison
        ax[1].bar(model_names, r2_values, color='green')
        ax[1].set_title("Model Comparison: R2 Score")
        ax[1].set_ylabel("R2 Score")

        # MAE Comparison
        ax[2].bar(model_names, mae_values, color='red')
        ax[2].set_title("Model Comparison: Mean Absolute Error (MAE)")
        ax[2].set_ylabel("MAE")

        # Display the plot
        plt.tight_layout()
        st.pyplot(fig)

        # Step 13: Selecting the Best Model
        st.write("## Step 13: Selecting the Best Model")

        # Check if model performance dictionary has been populated
        if model_performance:
            # Select the model with the lowest MSE
            best_model_mse = min(model_performance, key=lambda x: model_performance[x]["MSE"])
            st.write(f"### Best Model based on Lowest Mean Squared Error (MSE): {best_model_mse}")

            # Step 14: Retraining the Best Model on Entire Data
            st.write("## Step 14: Retraining the Best Model")
            best_model = trained_models[best_model_mse]
            # Retrain the best model on the entire dataset
            # Combine and scale the entire dataset
            X_combined_scaled = scaler.fit_transform(X)
            best_model.fit(X_combined_scaled, y)

            # Save the best model in session state and also as a file
            if 'best_model' not in st.session_state:
                st.session_state.best_model = best_model

            # save the model after retraining
            model_filename = "best_model.pkl"
            joblib.dump(best_model, model_filename)
            st.write(f"Model `{best_model_mse}` has been retrained and saved as `{model_filename}`.")
        else:
            st.write("No model performance results available. Please ensure models were trained successfully.")

        # Step 15: Model Deployment - Load the Saved Model and Predict
        st.write("## Step 15: Model Deployment - Predict Using Saved Model")

        # Load the saved model
        model_filename = "best_model.pkl"

        try:
            loaded_model = joblib.load(model_filename)
            st.write(f"Model `{model_filename}` loaded successfully!")

            # Allow user to input values for the features
            st.write("### Provide the input values for prediction")

            # Generate input fields dynamically based on the selected features
            user_input_values = {}
            for feature in selected_features:  # Ensure selected_features from step 11 is available
                user_input_values[feature] = st.number_input(f"Enter value for {feature}",
                                                            value=float(new_visual[feature].mean()))

            # Add Predict button
            if st.button("Predict"):
                # Convert the user inputs into a DataFrame
                user_input_df = pd.DataFrame([user_input_values])

                # Scale the user inputs using the same scaler
                user_input_scaled = scaler.transform(user_input_df)

                # Make predictions using the loaded model
                predicted_value = loaded_model.predict(user_input_scaled)

                # Display the predicted value
                st.write(f"### Predicted {target}: {predicted_value[0]:.2f}")

                # Visualizing the Prediction with Input Features
                st.write("## Visualizing Prediction and Feature Values")

                # Create a combined bar plot for input features and prediction
                fig, ax = plt.subplots()

                # Plot the input feature values
                feature_names = list(user_input_values.keys())
                feature_values = list(user_input_values.values())

                ax.bar(feature_names, feature_values, color='lightblue', label='Feature Values')

                # Add the predicted value at the bottom of the chart
                ax.bar(['Predicted ' + target], [predicted_value[0]], color='orange', label='Predicted Value')

                ax.set_xlabel("Value")
                ax.set_title(f"Input Features and Predicted {target}")
                ax.legend()

                # Display the plot
                st.pyplot(fig)

                # Create a line chart for input features and predicted value
                fig, ax = plt.subplots(figsize=(10, 6))

                copy_feature_names = feature_names.copy()
                copy_feature_values = feature_values.copy()
                # Add the predicted value at the end
                copy_feature_names.append(f"Predicted {target}")
                copy_feature_values.append(predicted_value[0])

                ax.plot(copy_feature_names, copy_feature_values, marker='o', linestyle='-', color='blue',
                        label='Feature and Predicted Values')

                ax.set_xlabel("Features and Prediction")
                ax.set_ylabel("Values")
                ax.set_title(f"Input Features and Predicted {target}")
                ax.grid(True)

                # Add data labels
                for i, txt in enumerate(copy_feature_values):
                    ax.annotate(f'{txt:.2f}', (copy_feature_names[i], copy_feature_values[i]),
                                textcoords="offset points",
                                xytext=(0, 10), ha='center')

                # Display the plot
                st.pyplot(fig)

        except FileNotFoundError:
            st.write(f"Model `{model_filename}` not found. Please ensure the model has been saved correctly.")
    else:
        st.write("No numeric features selected for training.")
else:
    st.write("Please upload one or more CSV files from the sidebar to get started.")

# # st.button("Execute Furniture Price Analysis", on_click=testFunction)