# boconvert.py - Easily record foreign currency transactions using double-entry accounting by automatically obtaining conversion rates
# Released under the MIT License

"""
This script uses the Valet API to obtain observation data from the Bank of Canada and shows how to record foreign currency transactions using double-entry accounting.

"""
import requests
from datetime import date, datetime, timedelta
from dateutil import parser
import re

from datetime import datetime, timedelta, date
import requests

def get_exchange_rate(target_date, currency):
    """
    Fetches the Bank of Canada exchange rate for the most recent business day
    on or before the target_date by walking backwards until complete observations are found.
    
    Returns (rate, actual_date) or (None, None) on failure.
    """
    
    # Quickly check and normalize to date-only as early as possible
    if not isinstance(target_date, datetime):
        raise TypeError(f"target_date must be datetime, got {type(target_date).__name__}")

    current_date = target_date.date()            # Start at the date the user requested and check if observations exist
    
    EARLIEST_DATE = date(2017, 1, 3)             # No data exists in the Valet before this date
    currency_key = f"FX{currency.upper()}CAD"    # For operations in Canadian dollars
    
    while current_date >= EARLIEST_DATE:
        date_str = current_date.strftime('%Y-%m-%d')
        
        url = f"https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/json?start_date={date_str}&end_date={date_str}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            
            if observations:  # Found a business day with data
                obs = observations[0]  # single-day query → exactly one entry when present
                actual_date_str = obs['d']
                
                if currency_key not in obs:
                    print(f"Error: Currency {currency} is missing even on {actual_date_str}")
                    return None, None
                
                rate = float(obs[currency_key]['v'])
                
                target_date_str = target_date.strftime('%Y-%m-%d')
                if actual_date_str != target_date_str:
                    print(f"Note: No data for {target_date_str}. "
                          f"Using rate from nearest prior business day ({actual_date_str}).")
                
                return rate, date.fromisoformat(obs['d'])
            
            # No observations for the given date → go back one day & try again
            current_date -= timedelta(days=1)
            
        except requests.exceptions.RequestException as e:
            print(f"Connection error while fetching {date_str}: {e}")
            return None, None
        except (KeyError, ValueError) as e:
            print(f"Data format error on {date_str}: {e}")
            return None, None
    
    print(f"No exchange rate data found on or before {target_date.strftime('%Y-%m-%d')} "
          f"(earliest available is 2017-01-03).")
    return None, None


def main():
    print("Welcome to convert.py")
    
    # Date Loop
    while True:
        date_input = input("Enter the date the transaction occured (e.g., 2026-03-11, March 11 2026, 11/03/2026): ")
        try:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", date_input):
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d")
            else:
                parsed_date = parser.parse(date_input, dayfirst=True)
                
            if parsed_date < datetime(2017, 1, 3):
                print("Please choose a date no earlier than 2017-01-03 (3 January 2017).")
                continue
        
            if parsed_date > datetime.now():
                print("Predicting future rates is really hard. Please choose a date that's today or earlier.")
                continue
            
            break # Exit loop if date input is valid and within acceptable range
        
        except ValueError:
            print("Invalid date format. Please try again.")
    
    # Transaction Value Loop
    while True:
        try:
            val_input = input("Enter the foreign currency transaction value (Enter 0 for free): ")
            value = float(val_input)
            if value < 0:
                print("Transaction value must be greater than zero. Please try again.")
                continue
            break # Exit loop if input is valid
        except ValueError:
            print("Invalid transaction value. Please enter numbers only.")
            
    # Currency Loop
    while True:
        currency = input("Enter the currency the transaction occured in (e.g., USD, EUR): ")
        currency_input = currency.strip().upper()
        
        if len(currency_input) != 3 or not currency_input.isalpha():
            print("Invalid currency code. Please enter a 3-letter currency code (e.g., USD, EUR).")
            continue
        if currency_input == "CAD":
            print("Please enter a foreign currency, not CAD.")
            continue
        break # Exit loop if input is valid
            
    # Fee Loop
    while True:
        try:
            fee_input = input(f"Enter the payment processing fee in {currency_input} (Enter 0 for no fee):")
            fee_foreign = float(fee_input)
            if fee_foreign < 0:
                print("Fee amount cannot be negative. Please try again.")
                continue
            break # Exit loop if input is valid
        except ValueError:
            print("Invalid fee amount. Please enter numbers only.")

    # 2. Fetch Exchange Rate and the date for the data
    rate, actual_date = get_exchange_rate(parsed_date, currency_input)
    
    if rate is None:
        print("Could not fetch exchange rate. Exiting program.")
        return

    # 3. Calculate Values for Foreign Currency Order
    cad_value = round(value * rate, 2)
    order_re_eval = round(cad_value - value, 2)

    # 4. Calculate Values for Foreign Currency Transaction Fee
    fee_cad = round(fee_foreign * rate, 2)
    fee_re_eval = round(fee_cad - fee_foreign, 2)

    # 5. Output aligned tables with the exchange rate obtained from the BoC
    print("\n")
    print("-" * 75)
    print(f"Foreign Currency Order on {actual_date:%d %B %Y} (Calculated at {rate} {currency_input}/CAD)")
    print("-" * 75)
    print(f"{'Account':<35} | {'Debit (DR)':<15} | {'Credit (CR)':<15}")
    print("-" * 75)
    print(f"{'Payment Account':<35} | {f'{value:.2f} {currency_input}':<15} | {'':<15}")
    print(f"{'Foreign Currency Re-evaluation':<35} | {f'{order_re_eval:.2f}':<15} | {'':<15}")
    print(f"{'Revenue Account':<35} | {'':<15} | {f'{cad_value:.2f} CAD':<15}")
    
    print("\n")
    print("-" * 75)
    print(f"Foreign Currency Fee on {actual_date:%d %B %Y} (Calculated at {rate} {currency_input}/CAD)")
    print("-" * 75)
    print(f"{'Account':<35} | {'Debit (DR)':<15} | {'Credit (CR)':<15}")
    print("-" * 75)
    print(f"{'Payment Processor fee':<35} | {f'{fee_cad:.2f} CAD':<15} | {'':<15}")
    print(f"{'Revenue Account':<35} | {'':<15} | {f'{fee_foreign:.2f} {currency_input}':<15}")
    print(f"{'Foreign Currency Re-evaluation':<35} | {'':<15} | {f'{fee_re_eval:.2f}':<15}")
    print("-" * 75)
    print("\n")

if __name__ == "__main__":
    while True:
        main()

        choice = input("Press 1 to restart with a new transaction or Enter to exit: ")
        if choice != "1":
            break