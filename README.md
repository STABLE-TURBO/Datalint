# DataLint

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

**Automated data validation for ML teams** - Find data quality issues before they break your models.

DataLint learns from clean datasets to automatically validate new data and prevent ML training failures. Simple, fast, and focused on real ML problems.

## 🚀 Quick Start

```bash
# Install
pip install datalint

# Validate your dataset
datalint validate mydata.csv

# Get detailed profile
datalint profile mydata.csv
```

## 📋 What It Checks

DataLint automatically detects:

- ✅ **Missing Values**: Identifies columns with too many nulls
- ✅ **Data Types**: Flags inconsistent or mixed data types
- ✅ **Outliers**: Detects statistical anomalies using IQR method
- ✅ **Constant Columns**: Finds features with no variation
- ✅ **Correlations**: Identifies highly correlated features (>95%)

## 💡 Why DataLint?

**Problem**: Data quality issues cause 60% of ML project failures, but validation is tedious manual work.

**Solution**: DataLint automates data validation with sensible defaults, helping ML teams catch issues before training.

**Unlike other tools**:
- **Simple**: No complex setup or configuration
- **Fast**: Validates large datasets in seconds
- **ML-Focused**: Optimizes for model training data quality
- **Actionable**: Clear recommendations for fixing issues

## 📖 Usage Examples

### Basic Validation
```bash
datalint validate iris.csv
```
Output:
```
Loaded dataset: 150 rows × 5 columns

✅ missing_values: No missing values found
✅ data_types: Data types appear consistent
✅ outliers: Outlier levels appear normal
⚠️  correlations: Found 1 highly correlated feature pairs
❌ constant_columns: Found 1 columns with constant values

Summary: 3 passed, 1 warnings, 1 failed
💡 Tip: Address failed checks before training ML models
```

### JSON Output for CI/CD
```bash
datalint validate data.csv --format json --output results.json
```

### Dataset Profiling
```bash
datalint profile sales_data.xlsx
```

## 🏗️ Architecture

```
datalint/
├── engine/          # Core validation logic
│   ├── validators.py   # Statistical checks
├── cli.py           # Command line interface
└── api.py           # Python API (future)
```

## 🎯 Roadmap

- **Week 1** ✅: Core validation engine with CLI
- **Week 2**: Learning system (auto-generate rules)
- **Week 3**: Beautiful reports + CI/CD integration
- **Week 4**: SaaS launch + user testing

## 🤝 Contributing

DataLint is in early development. We welcome:
- Bug reports and feature requests
- Code contributions
- User feedback and use cases

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**DataLint** - Because good models start with good data.
