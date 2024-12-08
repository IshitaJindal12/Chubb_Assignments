from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://inf_dev_hr1:inf_dev_hr1@ishita:1433/hr' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def home():
    return render_template('home.html')


db = SQLAlchemy(app)


class FactIndicatorValues(db.Model):
    __tablename__ = 'FACT_INDICATOR_VALUES'
    fact_id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('DIM_C_REGION.r_id'))
    year_id = db.Column(db.Integer, db.ForeignKey('DIM_YEARS.y_id'))
    income_id = db.Column(db.Integer, db.ForeignKey('DIM_INCOME.inc_id'))
    country_id = db.Column(db.Integer, db.ForeignKey('DIM_COUNTRY.c_id'))
    indicator_id = db.Column(db.Integer, db.ForeignKey('DIM_INDICATORS.i_id'))
    indicator_value = db.Column(db.Float)

class DimRegion(db.Model):
    __tablename__ = 'DIM_C_REGION'
    r_id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))

class DimYears(db.Model):
    __tablename__ = 'DIM_YEARS'
    y_id = db.Column(db.Integer, primary_key=True)
    rec_year = db.Column(db.Integer)

class DimCountry(db.Model):
    __tablename__ = 'DIM_COUNTRY'
    c_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100))
    country_code = db.Column(db.String(10))

class DimIndicators(db.Model):
    __tablename__ = 'DIM_INDICATORS'
    i_id = db.Column(db.Integer, primary_key=True)
    indicator_name = db.Column(db.String(255))
    indicator_code = db.Column(db.String(255))

class DimIncome(db.Model):
    __tablename__ = 'DIM_INCOME'
    inc_id = db.Column(db.Integer, primary_key=True)
    income = db.Column(db.String(100))


def fetch_data():
    with app.app_context():
        # Join Query
        query = db.session.query(
            DimRegion.region,
            DimYears.rec_year,
            DimCountry.country_name,
            DimIndicators.indicator_name,
            DimIncome.income,
            FactIndicatorValues.indicator_value
        ).join(
            FactIndicatorValues, FactIndicatorValues.region_id == DimRegion.r_id
        ).join(
            DimYears, FactIndicatorValues.year_id == DimYears.y_id
        ).join(
            DimCountry, FactIndicatorValues.country_id == DimCountry.c_id
        ).join(
            DimIndicators, FactIndicatorValues.indicator_id == DimIndicators.i_id
        ).join(
            DimIncome, FactIndicatorValues.income_id == DimIncome.inc_id
        )

        results = query.all()

        data = [
            {
                "Region": row.region,
                "Year": row.rec_year,
                "Country": row.country_name,
                "Indicator": row.indicator_name,
                "Income Group": row.income,
                "Value": row.indicator_value
            }
            for row in results
        ]
        df = pd.DataFrame(data)

        return df
    
@app.route('/table')
def test_query():
    with app.app_context():

        query = db.session.query(
            DimRegion.region,
            DimYears.rec_year,
            DimCountry.country_name,
            DimIndicators.indicator_name,
            DimIncome.income,
            FactIndicatorValues.indicator_value
        ).join(
            FactIndicatorValues, FactIndicatorValues.region_id == DimRegion.r_id
        ).join(
            DimYears, FactIndicatorValues.year_id == DimYears.y_id
        ).join(
            DimCountry, FactIndicatorValues.country_id == DimCountry.c_id
        ).join(
            DimIndicators, FactIndicatorValues.indicator_id == DimIndicators.i_id
        ).join(
            DimIncome, FactIndicatorValues.income_id == DimIncome.inc_id
        ).filter(
            DimRegion.region.isnot(None)
        )

        results = query.all()

        for row in results:
            print(f"Region: {row.region}, Year: {row.rec_year}, Country: {row.country_name}, "
                  f"Indicator: {row.indicator_name}, Income: {row.income}, Value: {row.indicator_value}")
            
        return render_template('table_gen.html', results=results)


def plot_inflation_trend(data):
    filtered_data = data[(data["Region"] == "South Asia") & (data["Indicator"] == "Inflation, GDP deflator (annual %)")]
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=filtered_data, x="Year", y="Value", hue="Country", marker="o")
    plt.title("Inflation Trend in South Asian Countries")
    plt.xlabel("Year")
    plt.ylabel("Inflation Rate")
    plt.legend(title="Country")
    plt.tight_layout()
    plt.savefig("static/inflation_trend_south_asia.png")
    plt.close()

def plot_gdp_per_capita_scatter(data):
    region = "Middle East & North Africa"
    filtered_data = data[(data["Indicator"] == "GDP per capita (current US$)") & (data["Region"] == region)]
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=filtered_data, x="Year", y="Value", hue="Country", size="Value", sizes=(50, 200))
    plt.title("GDP Per Capita Over Years (Middle East & North Africa)")
    plt.xlabel("Year")
    plt.ylabel("GDP Per Capita")
    plt.legend(title="Country")
    plt.tight_layout()
    plt.savefig("static/gdp_per_capita_scatter.png")
    plt.close()

def plot_global_gdp_share(data, year):
    filtered_data = data[(data["Indicator"] == "GDP growth (annual %)") & (data["Year"] == year)]
    region_gdp = filtered_data.groupby("Region")["Value"].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.pie(region_gdp["Value"], labels=region_gdp["Region"], autopct="%1.1f%%", startangle=140, colors=sns.color_palette("tab10"))
    plt.title(f"Share of Global GDP by Region in {year}")
    plt.tight_layout()
    plt.savefig("static/global_gdp_share.png")
    plt.close()

def plot_inflation_vs_gdp(data):
    region = "North America"
    filtered_data = data[(data["Region"] == region) & (data["Indicator"].isin(["Inflation, GDP deflator (annual %)", "GDP per capita (current US$)"]))]
    inflation_data = filtered_data[filtered_data["Indicator"] == "Inflation, GDP deflator (annual %)"].rename(columns={"Value": "Inflation"})
    gdp_data = filtered_data[filtered_data["Indicator"] == "GDP per capita (current US$)"].rename(columns={"Value": "GDP per Capita"})
    merged_data = pd.merge(inflation_data, gdp_data, on=["Country", "Year", "Region"], suffixes=("_inflation", "_gdp"))
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_data, x="Inflation", y="GDP per Capita", hue="Country", size="GDP per Capita", sizes=(50, 300))
    plt.title("Inflation vs. GDP Per Capita (North America)")
    plt.xlabel("Inflation Rate")
    plt.ylabel("GDP Per Capita")
    plt.tight_layout()
    plt.savefig("static/inflation_vs_gdp.png")
    plt.close()

def plot_gross_savings_trend(data):
    region = "Europe & Central Asia"
    year = 2022
    filtered_data = data[(data["Indicator"] == "GDP per capita growth (annual %)") & (data["Year"] == year) & (data["Region"] == region)]
    avg_savings = filtered_data.groupby("Country")["Value"].mean().reset_index()
    
    plt.figure(figsize=(14, 5))
    sns.barplot(data=avg_savings, x="Country", y="Value", palette="viridis")
    plt.title(f"Average GDP per capita growth (annual %) in {region} ({year})")
    plt.xlabel("Country")
    plt.ylabel("GDP per capita growth (annual %))")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/gross_savings_trend.png")
    plt.close()


def generate_analysis_charts():
    df = fetch_data()
    plot_inflation_trend(df)
    plot_gdp_per_capita_scatter(df)
    plot_global_gdp_share(df, year=2022)
    plot_inflation_vs_gdp(df)
    plot_gross_savings_trend(df)


@app.route('/analysis')
def analysis():
    generate_analysis_charts()
    return render_template('analysis.html')

if __name__ == '__main__':
    app.run(debug=True)