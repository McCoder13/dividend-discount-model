# Stock Analysis Tool

This tool allows you to analyze stock data including current price, future price projections using the Dividend Discount Model (DDM), and more.

## Setup

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/stock-analysis-tool.git
   cd stock-analysis-tool
   
2. Install the required libraries using pip:
      ```bash
      pip install -r requirements.txt

### Usage

3. Run the script in your terminal:

   ```bash
   python stock_analysis_tool.py
   Enter a ticker symbol when prompted. You can also type "help" for a list of 100 biggest companies that pay dividends or "quit" to exit.

Financial Values Used
Market Risk Premium: This is used in the calculation of the required rate of return. It typically represents the additional return expected by investors for taking on higher-risk investments compared to risk-free assets.

Default value used: 4.62%
30-Year Treasury Yield: This is used as a proxy for the risk-free rate in the required rate of return calculation.

Default value used: 4.45%
Disclaimer
This tool provides financial projections based on data fetched from public sources and calculations based on established financial models. Results may vary based on the accuracy and timeliness of data sources and assumptions made. Use this tool at your own risk. The authors are not responsible for any financial decisions made based on the output of this tool.
