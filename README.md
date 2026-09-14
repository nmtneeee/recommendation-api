
🛍️ Recommendation System API & Web Demo

A product recommendation system developed for the CS116 course project at the University of Information Technology (UIT).

The system predicts the Top-10 products that each customer is likely to purchase in the future based on historical transaction data and behavioral features. The trained recommendation results are served through a FastAPI backend and an interactive web interface.

🔗 Live Demo: https://recommendation-api-7kcl.onrender.com/

⸻

📌 Project Overview

The goal of this project is to build a recommendation system capable of predicting products that a customer may purchase or repurchase in the future.

The system addresses several challenges commonly found in real-world recommendation problems:

* Large-scale but sparse transaction data
* Different purchasing behaviors across customers
* Changes in purchasing behavior over time
* Cold-start customers with limited or no purchase history
* Difficulty ranking products across a very large product catalog

For each customer_id, the system generates a ranked list of Top-10 recommended products.

⸻

🎯 Objectives

The main objectives of the project are:

* Perform exploratory data analysis (EDA)
* Clean and preprocess large-scale transaction data
* Perform feature engineering based on customer and product behavior
* Train and compare multiple ranking models
* Evaluate recommendation quality using Precision@10
* Select the best-performing model
* Build an API and web interface for demonstrating the recommendation results

⸻

📊 Dataset

The dataset consists of four main components:

Dataset	Size	Description
Users	27,331 × 18	Customer information and demographic attributes
Items	4,573,964 × 34	Product information and product categories
Transactions	39,028,077 × 16	Historical customer purchase transactions
Ground Truth	644,970 × 2	Products actually purchased during the evaluation period

The datasets are connected primarily through customer_id and item_id.

The large-scale transaction data makes this a realistic recommendation scenario with sparse user-item interactions.

⸻

🗓️ Train / Validation / Test Split

The project uses a time-based split to reflect the real-world recommendation scenario.

Period	Purpose
Jan–Dec 2024	Training
Jan 1–31, 2025	Validation
Feb 1–28, 2025	Test

Using a temporal split prevents future transactions from leaking into the training data and allows the model to be evaluated on future purchasing behavior.

⸻

🧹 Data Preprocessing

The preprocessing pipeline includes:

* Removing unnecessary technical and synchronization-related columns
* Handling missing values
* Removing columns with no useful variation
* Detecting potential abnormal users
* Processing numerical features
* Applying transformations to highly skewed variables such as product prices
* Preparing customer, product, and transaction features for model training

Examples of removed technical fields include synchronization status, deletion flags, synchronization timestamps, and other metadata that do not provide useful predictive information.

⸻

🤖 Recommendation Models

Several ranking models were investigated and compared:

* LightGBM
* XGBoost
* CatBoost

The models were trained as ranking models to generate an ordered list of candidate products for each customer.

Model Configuration

The project explored hyperparameter tuning for models such as LightGBM and XGBoost, including learning rate, tree depth, number of leaves, subsampling, and regularization parameters.

⸻

📈 Model Evaluation

The primary evaluation metric is Precision@10.

Precision@10 measures the proportion of products in the Top-10 recommendation list that were actually purchased by the customer during the evaluation period.

Results

Model	With History	Without History
LightGBM	11.43%	1.28%
XGBoost	7.03%	0.00%
CatBoost	8.75%	0.98%

LightGBM achieved the best overall performance, reaching a Precision@10 of 11.43% for customers with purchase history.

The large performance difference between the two scenarios also demonstrates the importance of historical customer behavior for personalized recommendation.

⸻

🔄 Recommendation Scenarios

The deployed system supports two recommendation scenarios:

1. With History

Recommendations are generated for customers who have historical purchase information.

This scenario benefits from behavioral signals such as previous purchases and recent purchasing patterns.

2. Without History

This scenario represents customers with limited or unavailable purchase history.

The significantly lower Precision@10 in this scenario highlights the cold-start challenge in recommendation systems.

⸻

🖥️ Web Demo

The project includes a web interface for querying recommendation results by customer_id.

The interface allows users to:

* Enter a Customer ID
* Select the recommendation scenario
* View the Top-10 recommended products
* Inspect product information
* Compare predicted products against the available ground truth
* Identify HIT / MISS recommendations

The web application communicates with the FastAPI backend through HTTP requests.

⸻

🔌 API

Get Recommendations

GET /recommend/{customer_id}?use_history=true

Parameters

Parameter	Type	Description
customer_id	string	Customer identifier
use_history	boolean	true for With History, false for Without History

Example

GET /recommend/92752?use_history=true

Example Response

{
  "customer_id": "92752",
  "recommendations": [
    {
      "item_id": "5420000000003",
      "brand": "Brand Name",
      "category_l1": "Category",
      "category_l2": "Subcategory",
      "price": 150000.0,
      "is_hit": true,
      "status": "HIT"
    }
  ]
}

The API response provides additional product information such as brand, category, price, and whether the recommended item matches the ground-truth purchase set.

⸻

🏗️ System Architecture

                    ┌──────────────────────┐
                    │   Historical Data    │
                    │ Users / Items /      │
                    │ Transactions / GT    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Data Preprocessing   │
                    │ & Feature Engineering│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Ranking Models      │
                    │ LightGBM / XGBoost / │
                    │ CatBoost             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Top-10 Predictions │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    SQLite Database   │
                    │      recs.db         │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │          FastAPI API            │
              └────────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Web UI          │
                    │   HTML + JavaScript  │
                    └──────────────────────┘

⸻

🛠️ Tech Stack

Machine Learning

* Python
* LightGBM
* XGBoost
* CatBoost
* Pandas

Backend

* FastAPI
* Uvicorn
* SQLite

Data Processing

* Polars
* PyArrow
* Parquet
* JSON
* Pickle

Frontend

* HTML5
* JavaScript
* Fetch API

Deployment

* Docker
* Render

⸻

📁 Project Structure

recommendation-api/
│
├── main.py
├── convert_to_db.py
├── index.html
├── Dockerfile
├── requirements.txt
│
├── .gitignore
│
└── recs.db                    # Generated database

Large datasets and generated database files are excluded from the Git repository.

⸻

💻 Local Setup

1. Clone the repository

git clone https://github.com/nmtneeee/recommendation-api.git
cd recommendation-api

2. Create a virtual environment

python -m venv venv
source venv/bin/activate

On Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

Additional dependencies may be required when rebuilding the database from Parquet data:

pip install pandas pyarrow

4. Generate the SQLite database

Place the required data files in the project directory and run:

python convert_to_db.py

This generates the recs.db database used by the API.

5. Run the API

uvicorn main:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

⸻

🐳 Docker

Build the Docker image:

docker build -t recommendation-api .

Run the container:

docker run -p 8000:8000 recommendation-api

Then open:

http://localhost:8000

⸻

☁️ Deployment

The API is deployed using Docker on Render.

The deployment architecture separates the application source code from the large recommendation database. The generated SQLite database is therefore not stored directly in the Git repository.

GitHub
   │
   ▼
Application Source Code
   │
   ▼
Docker Build
   │
   ▼
Render
   │
   └──────► Recommendation Database

⸻

🔍 Example Recommendation Analysis

The project also analyzes individual recommendation cases.

Best Case

A customer with a clear and repeated purchasing pattern can receive recommendations that correctly capture both:

* Previously purchased products
* New but behaviorally relevant products

The report shows that good candidate generation can provide strong coverage of the ground truth, while the ranking model prioritizes products related to recent customer behavior.

Worst Case

Performance becomes more difficult when:

* Customer purchase history is highly scattered
* The customer purchases across many unrelated categories
* The model over-relies on popular or previously purchased items
* New purchases cannot be inferred reliably from recent context

These cases illustrate the difficulty of recommendation under sparse and diverse user behavior.

⸻

👥 Team

CS116.Q11 — Group 13

* Lương Quang Duy — 23520368
* Trần Minh Nhất — 23521101
* Dương Thái Ý Nhi — 23521106
* Vũ Hiếu Thiên — 23521490

University of Information Technology (UIT)

⸻

📚 Project Report

This project was developed as part of the CS116 Recommendation System course project.

The project focuses on data preprocessing, feature engineering, learning-to-rank models, recommendation evaluation, and deployment of the resulting recommendation system.

⸻

📄 License

This project was developed for academic purposes as part of the CS116 course project at UIT.
