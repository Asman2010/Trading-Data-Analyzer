# Trading-Data-Analyzer
Trading Data Analyzer is a Python-based application designed to help users analyze their trading data from CSV files. The application reads a CSV file containing trading transactions, calculates profit and loss, and displays detailed analyses. Additionally, it allows users to save the analysis as a PDF file. 

**Note: The CSV file format provided in this application is specifically tailored for Zerodha, a popular Indian stock broker. If you are using a different broker, you may need to modify the code to match the column names and data structure of the CSV file provided by your broker.**

## 1. Features

1. **CSV File Selection**: Users can select a CSV file to analyze. The CSV must contain the following columns:
   - `symbol`
   - `trade_type`
   - `quantity`
   - `price`
   - `trade_date`
   - `order_execution_time`

2. **Data Analysis**: The application performs a detailed analysis of the trading data, including:
   - Calculating the total profit or loss for each symbol.
   - Displaying buy and sell quantities, prices, and times.
   - Calculating money spent on buys and money gained from sells.
   - Determining the holding duration for each symbol.

3. **Text Output**: The analysis results are displayed in a scrollable text widget within the application. The output is formatted using `PrettyTable` for better readability.

4. **PDF Export**: Users can save the analysis as a PDF file. The PDF includes all the details shown in the text widget.

5. **Clear Screen**: Users can clear the analysis results from the text widget.


## 2. Customizable Themes : User can choose from a variety of dark and light, themes include:
![image](https://github.com/Asman2010/Trading-Data-Analyzer/assets/142419243/a13f2262-eae8-4a10-91f9-70614a9fd7bc)

## 3. Screenshot's
![image](https://github.com/Asman2010/Trading-Data-Analyzer/assets/142419243/6fe4c27a-89ba-49d6-bebf-d19f9f6fe32a)
-----
![image](https://github.com/Asman2010/Trading-Data-Analyzer/assets/142419243/92e75596-39f5-4292-8439-a06969e867c9)

## 4. Dependencies

The following Python packages are required:
- pandas
- prettytable
- ttkbootstrap
- tkinter
- fpdf

You can install these dependencies using the following command:
```sh
pip install pandas prettytable ttkbootstrap fpdf
```

## 5. License

This project is licensed under the MIT License.
