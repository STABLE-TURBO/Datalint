import pandas as pd
import numpy as np

def check_missing_values(df: pd.DataFrame, threshold: float = 0.05) -> dict:
    """
    Check for columns with excessive missing values.

    Args:
        df: Input DataFrame
        threshold: Maximum allowed missing value ratio (default 5%)

    Returns:
        Dict with results and recommendations

    Reference: IEEE Transactions on Knowledge and Data Engineering
    "Data Quality Assessment: A Survey" (Batini et al., 2009)
    """
    missing_ratios = df.isnull().mean()
    problematic_cols = missing_ratios[missing_ratios > threshold]

    return {
        'passed': len(problematic_cols) == 0,
        'issues': problematic_cols.to_dict(),
        'recommendations': [
            f"Column '{col}' has {ratio:.1%} missing values. "
            f"Consider imputation or removal if >5%."
            for col, ratio in problematic_cols.items()
        ]
    }


def check_data_types(df: pd.DataFrame) -> dict:
    """
    Validate data type consistency and detect mixed types.

    Reference: Pandas documentation on dtype inference
    https://pandas.pydata.org/docs/user_guide/basics.html#dtypes
    """
    type_consistency = {}
    issues = []

    for col in df.columns:
        # Check for object columns with mixed types
        if df[col].dtype == 'object':
            unique_types = df[col].dropna().apply(type).unique()
            if len(unique_types) > 1:
                issues.append(f"Column '{col}' has mixed types: {list(unique_types)}")

        # Check for numeric columns with non-numeric values
        elif pd.api.types.is_numeric_dtype(df[col]):
            non_numeric = pd.to_numeric(df[col], errors='coerce').isnull()
            if non_numeric.any():
                issues.append(f"Column '{col}' contains non-numeric values")

    return {
        'passed': len(issues) == 0,
        'issues': issues,
        'recommendations': [
            "Consider explicit type conversion or data cleaning"
        ] if issues else []
    }

def check_outliers(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> dict:
    """
    Detect outliers using Interquartile Range method.

    Args:
        df: Input DataFrame
        iqr_multiplier: IQR multiplier for outlier bounds (default 1.5)

    Reference: "Robust Statistics" by Peter J. Huber (1981)
    IQR method widely used in exploratory data analysis.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_summary = {}

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_ratio = len(outliers) / len(df)

        if outlier_ratio > 0.05:  # More than 5% outliers
            outlier_summary[col] = {
                'count': len(outliers),
                'ratio': outlier_ratio,
                'bounds': (lower_bound, upper_bound)
            }

    return {
        'passed': len(outlier_summary) == 0,
        'issues': outlier_summary,
        'recommendations': [
            f"Column '{col}' has {info['ratio']:.1%} outliers. "
            f"Consider winsorization or investigation."
            for col, info in outlier_summary.items()
        ]
    }