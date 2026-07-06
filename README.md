# ☕ Afficionado Coffee Roasters — Sales Analytics Dashboard

A Streamlit-based data analytics dashboard designed to analyze sales trends, customer demand patterns, and store performance using transaction data from Afficionado Coffee Roasters.

## 📌 Project Overview

This project performs Exploratory Data Analysis (EDA) and builds an interactive dashboard to understand sales behavior over time.

The dashboard helps identify revenue trends, peak demand hours, product performance, and location-wise sales patterns to support data-driven business decisions.

## 🎯 Objectives

* Analyze overall sales trends
* Identify peak transaction hours
* Study time-based demand patterns
* Compare sales performance across store locations
* Generate actionable business insights

## 🛠️ Technologies Used

* Python
* Pandas
* Plotly
* Streamlit
* Data Visualization
* Exploratory Data Analysis (EDA)

## 📂 Project Structure

```
sales-analysis-project/

├── app.py
├── requirements.txt
├── README.md

├── data/
│   └── coffee_transactions.csv

├── utils/
│   ├── data_loader.py
│   └── charts.py

└── images/
    └── dashboard screenshots
```

## 📊 Dashboard Features

### Sales Trend Analysis

* Overall revenue analysis
* Daily, weekly, and monthly sales trends
* Time-based sales distribution

### Day & Hour Analysis

* Day-wise sales comparison
* Hourly demand analysis
* Peak hour identification
* Day × Hour heatmap visualization

### Location Analysis

* Store-wise revenue comparison
* Store performance analysis
* Location-based demand patterns

### Interactive Filters

Users can filter dashboard results using:

* Store location
* Day of week
* Hour range
* Revenue or transaction count

## 📁 Dataset Description

The dataset contains coffee shop transaction records including:

* Transaction information
* Store locations
* Product details
* Quantity sold
* Unit price
* Transaction time

Note:
The source dataset contains transaction time information but does not contain a calendar date column. Therefore, temporal features are created for analysis while maintaining the available transaction time information.

## ⚙️ Data Processing

The project includes:

* Data loading and validation
* Missing value checking
* Duplicate transaction checking
* Revenue calculation
* Feature engineering
* Time-based analysis

Revenue is calculated as:

```
Revenue = Transaction Quantity × Unit Price
```

## ▶️ How to Run the Project

### 1. Clone the repository

```
git clone <repository-link>
```

### 2. Install required libraries

```
pip install -r requirements.txt
```

### 3. Run Streamlit Dashboard

```
streamlit run app.py
```

The dashboard will open in the browser.

## 📈 Key Insights Generated

The dashboard provides insights about:

* Sales performance trends
* High-demand hours
* Store contribution
* Product performance
* Customer demand behavior

## 🚀 Deployment

The application can be deployed using Streamlit Cloud for online access.

## Project Deliverables

- 🔗 Research Paper: [https://docs.google.com/document/d/1nXSVm2OV9vMUgvX-nJB3u6NGzEexq8bh/edit?usp=drivesdk&ouid=105635979916499483150&rtpof=true&sd=true](docs/research_paper.pdf)
- 🔗 Executive Summary: [https://docs.google.com/document/d/1gqPsQhA2bFFMCl9MgeUwHkuC3wDOu1k_/edit?usp=drivesdk&ouid=105635979916499483150&rtpof=true&sd=true](docs/executive_summary.pdf)
- 🔗 Live Dashboard: [https://afficionado-coffee-sales.streamlit.app/]
- 🔗 Github: [https://github.com/aditimarwadi/Afficionado-Coffee-Sales-Analytics]

## 👩‍💻 Author

Aditi Marwadi
