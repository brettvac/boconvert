# boconvert

A Python script that uses the Valet API to obtain observation data from the Bank of Canada and shows how to record foreign currency transactions using double-entry accounting for a given date and amount.

## Boconvert.py

Boconvert is a Python script that allows you to easily and quickly record foreign currency transactions into your general ledger.

If you are operating a web based business in Canada, you may find it necessary to transact in a foreign currency, such as USD (US Dollars) or EUR (Euros).

When recording a transaction in these currencies, you will likely have accounts which are in a foreign currency, but you will need to report all your revenue in CAD (Canadian Dollars).

This script allows you to easily record foreign currency transactions by adding an extra line, represented by "Currency re-evaluation", to show the difference between the value in the foreign currency and the local one, CAD.

## Usage

Just run `python boconvert.py` or double-click on the icon, and follow the prompts. The program will then process your inputs, and will spit out a table based on the values given.

By default, it prompts for a transaction involving money entering the business, followed by a transaction for money leaving the business. 

If you just want one calculation, you can enter `0` as the amount.

## Disclaimer

This script is for educational purposes only. Consult a certfied accountant when preparing official documents.
