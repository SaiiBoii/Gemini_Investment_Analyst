import os
import google.generativeai as genai
from flask import Flask, render_template, request
import yfinance as yf
import markdown

# --- Configuration ---
app = Flask(__name__)

'''ENSURE TO SET THE GOOGLE_API_KEY ENVIRONMENT VARIABLE BEFORE RUNNING THE APP: 
   RUN THE FILE, AND ENTER $env:GOOGLE_API_KEY="YOUR_API_KEY" IN THE TERMINAL, 
   PRESS ENTER AND THEN RUN THE APP.'''

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    print("ERROR: The GOOGLE_API_KEY environment variable is not set.")
    print("Please set it to your Google API key.")
    exit()
except Exception as e:
    print(f"An error occurred during API configuration: {e}")
    exit()

def get_financial_summary(company_ticker: str) -> str:
    stock = yf.Ticker(company_ticker)
    info = stock.info

    return f"""
    
Company Financial Summary – {company_ticker.upper()}

Name: {info.get('longName')}
Sector: {info.get('sector')}
Industry: {info.get('industry')}
Country: {info.get('country')}
Full Time Employees: {info.get('fullTimeEmployees')}

Valuation Metrics
Market Cap: {info.get('marketCap')}
Enterprise Value: {info.get('enterpriseValue')}
Trailing P/E Ratio: {info.get('trailingPE')}
Forward P/E Ratio: {info.get('forwardPE')}
PEG Ratio (5 yr expected): {info.get('pegRatio')}
Price-to-Sales (TTM): {info.get('priceToSalesTrailing12Months')}
Price-to-Book: {info.get('priceToBook')}
EV/EBITDA: {info.get('enterpriseToEbitda')}
EV/Revenue: {info.get('enterpriseToRevenue')}

Profitability & Margins
Revenue: {info.get('totalRevenue')}
Gross Profit: {info.get('grossProfits')}
Net Income: {info.get('netIncomeToCommon')}
Profit Margin: {info.get('profitMargins')}
Gross Margin: {info.get('grossMargins')}
Operating Margin: {info.get('operatingMargins')}
Return on Assets (ROA): {info.get('returnOnAssets')}
Return on Equity (ROE): {info.get('returnOnEquity')}

Balance Sheet Ratios
Current Ratio: {info.get('currentRatio')}
Quick Ratio: {info.get('quickRatio')}
Debt to Equity: {info.get('debtToEquity')}
Total Cash: {info.get('totalCash')}
Total Debt: {info.get('totalDebt')}
Book Value per Share: {info.get('bookValue')}

Earnings & Per Share
EPS (TTM): {info.get('trailingEps')}
Forward EPS: {info.get('forwardEps')}
Free Cash Flow: {info.get('freeCashflow')}
Operating Cash Flow: {info.get('operatingCashflow')}
Dividend Yield: {info.get('dividendYield')}
Dividend Rate: {info.get('dividendRate')}
Payout Ratio: {info.get('payoutRatio')}

Stock Performance
52-Week High: {info.get('fiftyTwoWeekHigh')}
52-Week Low: {info.get('fiftyTwoWeekLow')}
Beta: {info.get('beta')}
Shares Outstanding: {info.get('sharesOutstanding')}
Float Shares: {info.get('floatShares')}
Short Ratio: {info.get('shortRatio')}
Implied Volatility: {info.get('impliedVolatility')}
"""




# --- AI Assessment Function ---
def get_ai_investment_assessment(company_name):
    """
    Uses the Gemini API to generate a simple investment assessment.
    """
    if not company_name:
        return "Please enter a company name."
    

    def get_ticker_from_name(name):

        prompt=f'''In one word give the ticker symbol of {name} name so I can input it into yfinance.
        Keep in mind the where the company is based. For instance a company listed on LSE will be XYZ.L,
        while a company listed on NIFTY will be XYZ.NS.
        Do not include any other information, just the ticker symbol.'''
        
        try:
            response = model.generate_content(prompt)
            return response.text.strip().upper()
        except Exception as e:
            print(f"An error occurred while calling the API: {e}")
            return None    
    
    company_ticker = get_ticker_from_name(company_name)

    financials = get_financial_summary(company_ticker)

    prompt = f""" You are an expert financial analyst. Your task is to perform an in-depth analysis of the company's financial data provided below and present your findings in a structured, five-part report.

    ---
    FINANCIAL SUMMARY
    {financials}

    *recognize whether the region of the company and use the appropriate currency symbol (e.g., $ for USD, ₹ for INR, etc.) when discussing financial figures.*
    ---

    Your report should be titled "Analysis for (given company)". Please follow this exact structure for your response, using the provided headings:

    ### 1) Company Overview
    Based on the financial summary, provide a brief overview of the company, including its name, sector, industry, and country. Mention its size based on market capitalization and number of employees.

    ### 2) Financials
    Analyze the company's financial health and profitability. Discuss key metrics like revenue, gross profit, net income, and various margins (gross, operating, profit). Also, comment on its balance sheet by looking at the current ratio, quick ratio, debt to equity, and cash levels.

    ### 3) Valuation
    Evaluate the company's valuation based on the provided metrics. Discuss the P/E ratios (trailing and forward), PEG ratio, Price-to-Sales, and Price-to-Book. Explain whether the company appears to be overvalued, undervalued, or fairly valued compared to potential industry benchmarks.

    ### 4) Growth Prospects
    Assess the company's future growth potential. Examine metrics such as forward P/E, forward EPS, and free cash flow. Mention any dividend yield or payout ratio as a potential indicator of a mature vs. growth-oriented company.

    ### 5) Final Recommendation
    Based on all the preceding analysis, provide a clear and definitive final recommendation. The recommendation must be one of the following and must stand alone as the final output of this section: **BUY**, **HOLD**, or **SELL**. After the recommendation, provide a short summary (2-3 sentences) of the primary reasons for your conclusion.
    """

    try:
        print(f"Generating assessment for: {company_name}")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred while calling the API: {e}")
        return "Sorry, there was an error getting the AI assessment."


# --- Web Page Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    company_name = ""

    if request.method == "POST":
        form = request.form
        company_name = form.get("company_name", "").strip()
        result_raw = get_ai_investment_assessment(company_name)
        result = markdown.markdown(result_raw)


    return render_template("index.html", result=result, company_name=company_name)

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)


        
