from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import statistics
from datetime import date

# Function to extract specific tables from the given URLs
def extract_specific_tables(url, dividend_url, beta_url):
    # Initialize the WebDriver (using Chrome in this case)
    driver = webdriver.Chrome()

    try:
        # Open the webpage for financial data
        driver.get(url)
        time.sleep(2)  # Allow some time for the page to load

        # Extract the current stock price
        price_element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text-4xl.font-bold.block.sm\\:inline")))
        current_price = float(price_element.text.strip())

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all tables on the webpage with the specified class
        target_class = "w-full whitespace-nowrap border border-gray-200 text-right text-sm dark:border-dark-700 sm:text-base"
        tables = soup.find_all('table', class_=target_class)

        if not tables:
            raise Exception("No tables with the specified class found on the webpage")

        # Extract data from the relevant table
        financial_data = {}
        for table in tables:
            headers = [header.text.strip() for header in table.find_all('th')]
            rows = table.find_all('tr')[1:]  # Skip the header row
            for row in rows:
                cells = row.find_all('td')
                row_header = cells[0].text.strip()
                financial_data[row_header] = [cell.text.strip() for cell in cells[1:]]
        
        # Extract years for reference
        years = headers[1:]  # Skip the 'Year' header

        # Open the dividend webpage
        driver.get(dividend_url)
        time.sleep(2)  # Allow some time for the page to load

        # Extract the annual dividend
        dividend_elements = driver.find_elements(By.CSS_SELECTOR, "div.mt-0\\.5.text-lg.font-semibold.bp\\:text-xl.sm\\:text-2xl")
        annual_dividend = None
        for element in dividend_elements:
            if "$" in element.text:
                annual_dividend = float(element.text.replace('$', '').replace(',', ''))
                break

        if annual_dividend is None:
            raise Exception("Annual dividend element not found or incorrectly formatted.\n-------------------------------------------------------------------------------------------------------------------\nThe chosen company likely does not pay a dividend.\nThe dividend discount model only works on companies paying a dividend.\n-------------------------------------------------------------------------------------------------------------------")
  

        # Open the beta webpage
        driver.get(beta_url)
        time.sleep(2)  # Allow some time for the page to load

        # Extract the suggested beta
        suggested_beta = extract_beta(driver.page_source)

        print("-------------------------Debugging------------------------------------>")
        print("Extracted financial data headers:", financial_data.keys())
        print("Years:", years)
        print("Annual Dividend:", annual_dividend)
        print("Suggested Beta:", suggested_beta)
        print("-------------------------Debugging------------------------------------>")
        print(" ")
        print("Loading.......................................give it a sec............")
        
        return financial_data, current_price, years, annual_dividend, suggested_beta
    finally:
        driver.quit()

# Function to extract beta from the page source
def extract_beta(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    try:
        # Find the <td> containing "Beta" and get the sibling <td> for beta value
        beta_td = soup.find('td', text='Beta')
        beta = float(beta_td.find_next_sibling('td').text.strip())
        return beta
    except Exception as e:
        print(f"Error extracting beta: {e}")
        return None

# Function to calculate the required rate of return
def calculate_required_rate_of_return(beta, treasury_yield=4.45, market_return=9.67, risk_premium=4.62):
    return treasury_yield + beta * risk_premium

# Function to project future price based on financial data
def project_future_price(financial_data, years):
    try:
        # Extract EPS for 2024 and 2025 and convert to float
        eps_2024 = float(financial_data['EPS'][years.index('2024')])
        eps_2025 = float(financial_data['EPS'][years.index('2025')])

        # Extract Forward PE for 2024 and 2025, skip '-' values, and convert to float
        forward_pe_2024 = float(financial_data['Forward PE'][years.index('2024')])
        forward_pe_2025 = float(financial_data['Forward PE'][years.index('2025')])

        # Project future EPS for 2026 (assuming constant growth rate based on 2024 and 2025)
        future_eps = eps_2025 * ((1 + (eps_2025 - eps_2024) / eps_2024))

        # Calculate average PE for 2024 and 2025
        average_pe = statistics.mean([forward_pe_2024, forward_pe_2025])

        # Calculate future price using average PE and projected EPS
        future_price = average_pe * future_eps

        return future_price
    except KeyError as e:
        print(f"Missing key in financial data: {e}")
        raise

# Function to calculate future price using Dividend Discount Model
def dividend_discount_model(future_price, required_rate_of_return, annual_dividend):
    # Projected price with dividends over the next two years
    return (future_price + 2 * annual_dividend) / (1 + required_rate_of_return / 100) ** 2

# Main function to run the program
def main():
    while True:
        # Ask the user for the URL or display help
        ticker_input = input("Please enter the ticker symbol of the company to analyze (type 'help' for list or 'quit' to exit): ")
        
        if ticker_input.lower() == 'help':
            with open('tickers.txt', 'r') as file:
                companies = file.readlines()
                print("List of 100 biggest companies that pay dividends:")
                for company in companies:
                    print(company.strip())
                continue
        elif ticker_input.lower() == 'quit':
            break
        
        url = f'https://stockanalysis.com/stocks/{ticker_input.lower()}/forecast/'
        dividend_url = f'https://stockanalysis.com/stocks/{ticker_input.lower()}/dividend/'
        beta_url = f'https://stockanalysis.com/stocks/{ticker_input.lower()}/'
        
        try:
            financial_data, current_price, years, annual_dividend, suggested_beta = extract_specific_tables(
                url, dividend_url, beta_url
            )
        except Exception as e:
            print(f"Error: {e}")
            continue
        
        # Display suggested beta and prompt user for input
        print(f"Suggested Beta: {suggested_beta}")
        user_input_beta = input("Enter your own beta value (press Enter to use suggested beta): ")
        
        # Use suggested beta if user input is empty, otherwise use user input
        beta = suggested_beta if user_input_beta.strip() == '' else float(user_input_beta)

        # Calculate the required rate of return
        required_rate_of_return = calculate_required_rate_of_return(beta)

        # Project the future price
        future_price = project_future_price(financial_data, years)

        # Calculate the final future price using DDM
        final_future_price = dividend_discount_model(future_price, required_rate_of_return, annual_dividend)

        # Calculate the percentage difference
        percent_difference = ((final_future_price - current_price) / current_price) * 100

        # Provide a buy, sell, or hold rating
        if final_future_price > current_price * 1.02:
            rating = "Buy"
        elif final_future_price < current_price * .95:
            rating = "Sell"
        else:
            rating = "Hold"

        # Output the results
        print("-------------------------Results------------------------------------>")
        print(f"Current Price: ${current_price:.2f} as of ", date.today())
        print(f"Beta Used: {beta}")
        print(f"Future Price (DDM-2ys): ${final_future_price:.2f}")
        print(f"Rating: {rating}")
        print(f"Percent Difference: {percent_difference:.2f}%")
        print("-------------------------Results------------------------------------>")

if __name__ == "__main__":
    main()
