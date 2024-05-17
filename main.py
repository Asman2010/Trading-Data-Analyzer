import pandas as pd
from prettytable import PrettyTable
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap import icons
from tkinter import filedialog, messagebox, END, Menu
from fpdf import FPDF
from tkinter import Canvas

class RoundedButton(Canvas):
    def __init__(self, parent, text, command=None, radius=20, padding=10, color="#007BFF", text_color="white", min_width=100, font_size=12, *args, **kwargs):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, *args, **kwargs)
        self.command = command
        self.radius = radius
        self.padding = padding
        self.color = color
        self.text_color = text_color
        self.font_size = font_size

        # Measure the text and adjust the button size accordingly
        text_id = self.create_text(0, 0, text=text, font=("Helvetica", self.font_size, "bold"))
        bbox = self.bbox(text_id)
        self.delete(text_id)  # Remove the text_id after measuring
        text_width = bbox[2] - bbox[0]

        self.width = max(radius * 2 + padding * 2, text_width + padding * 2, min_width)
        self.height = radius * 2 + padding * 2

        self.create_rounded_button(text)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_button(self, text):
        self.configure(width=self.width, height=self.height)
        self.create_oval((self.padding, self.padding, self.padding + self.radius * 2, self.padding + self.radius * 2), fill=self.color, outline="")
        self.create_oval((self.width - self.padding - self.radius * 2, self.padding, self.width - self.padding, self.padding + self.radius * 2), fill=self.color, outline="")
        self.create_rectangle((self.padding + self.radius, self.padding, self.width - self.padding - self.radius, self.padding + self.radius * 2), fill=self.color, outline="")

        self.create_text((self.width // 2, self.height // 2), text=text, fill=self.text_color, font=("Times New Roman", self.font_size, "bold"))

    def on_click(self, event):
        if self.command:
            self.command()



    def on_click(self, event):
        if self.command:
            self.command()

def analyze_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the file: {e}")
        return

    required_columns = {'symbol', 'trade_type', 'quantity', 'price', 'trade_date', 'order_execution_time'}
    if not required_columns.issubset(df.columns):
        messagebox.showerror("Error", "CSV file must contain 'symbol', 'trade_type', 'quantity', 'price', 'trade_date', and 'order_execution_time' columns")
        return

    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df['order_execution_time'] = pd.to_datetime(df['order_execution_time'])

    text_widget.text.configure(state='normal')  # Make the widget editable
    text_widget.text.delete('1.0', END)
    analyze_profit_loss(df)
    text_widget.text.configure(state='disabled')  # Make the widget read-only

def center_table(table_str, width):
    lines = table_str.split('\n')
    centered_lines = [line.center(width) for line in lines]
    return '\n'.join(centered_lines)

def analyze_profit_loss(df):
    companies = df['symbol'].unique()
    text_widget.text.insert(END, "📊 Detailed Analysis\n\n", "header")

    global tables  # Make tables a global variable to use in save_as_pdf
    tables = []
    for symbol in companies:
        symbol_data = df[df['symbol'] == symbol]
        symbol_buy_data = symbol_data[symbol_data['trade_type'] == 'buy']
        symbol_sell_data = symbol_data[symbol_data['trade_type'] == 'sell']

        total_profit_loss = 0
        buy_quantities = []
        buy_prices = []
        buy_times = []
        sell_quantities = []
        sell_prices = []
        sell_times = []

        holding_duration_str = "N/A"
        if not symbol_buy_data.empty and not symbol_sell_data.empty:
            buy_index = 0
            sell_index = 0

            while buy_index < len(symbol_buy_data) and sell_index < len(symbol_sell_data):
                buy_row = symbol_buy_data.iloc[buy_index]
                sell_row = symbol_sell_data.iloc[sell_index]
                buy_quantity = buy_row['quantity']
                buy_price = buy_row['price']
                buy_time = buy_row['order_execution_time']
                buy_quantities.append(buy_quantity)
                buy_prices.append(buy_price)
                buy_times.append(buy_time.strftime('%Y-%m-%d %H:%M:%S'))

                remaining_buy_quantity = buy_quantity
                while remaining_buy_quantity > 0 and sell_index < len(symbol_sell_data):
                    sell_row = symbol_sell_data.iloc[sell_index]
                    sell_quantity = sell_row['quantity']
                    sell_price = sell_row['price']
                    sell_time = sell_row['order_execution_time']

                    if sell_quantity <= remaining_buy_quantity:
                        profit_loss = (sell_price - buy_price) * sell_quantity
                        total_profit_loss += profit_loss
                        remaining_buy_quantity -= sell_quantity
                        sell_quantities.append(sell_quantity)
                        sell_prices.append(sell_price)
                        sell_times.append(sell_time.strftime('%Y-%m-%d %H:%M:%S'))
                        sell_index += 1
                    else:
                        profit_loss = (sell_price - buy_price) * remaining_buy_quantity
                        total_profit_loss += profit_loss
                        sell_quantities.append(remaining_buy_quantity)
                        sell_prices.append(sell_price)
                        sell_times.append(sell_time.strftime('%d-%m-%Y %H:%M:%S'))
                        remaining_buy_quantity = 0

                buy_index += 1

            # Calculate holding duration
            first_buy_date = symbol_buy_data['trade_date'].min()
            last_sell_date = symbol_sell_data['trade_date'].max()
            holding_duration = last_sell_date - first_buy_date
            holding_duration_str = f"{holding_duration.days} days"

        elif not symbol_buy_data.empty:
            buy_quantities = symbol_buy_data['quantity'].tolist()
            buy_prices = symbol_buy_data['price'].tolist()
            buy_times = symbol_buy_data['order_execution_time'].apply(lambda x: x.strftime('%d-%m-%Y %H:%M:%S')).tolist()

        elif not symbol_sell_data.empty:
            sell_quantities = symbol_sell_data['quantity'].tolist()
            sell_prices = symbol_sell_data['price'].tolist()
            sell_times = symbol_sell_data['order_execution_time'].apply(lambda x: x.strftime('%d-%m-%Y %H:%M:%S')).tolist()

        money_spent = round(sum(qty * price for qty, price in zip(buy_quantities, buy_prices)), 2)
        money_gained = round(sum(qty * price for qty, price in zip(sell_quantities, sell_prices)), 2)

        table = PrettyTable()
        table.add_column("Description", ["Buy Quantities", "Price Bought ", "Date & Time of Buy", "Money Spent", "Sell Quantities",
                                         "Price Sold", "Date & Time of Sell", "Money Gained Back", "Total Profit/Loss", "Holding Duration"])
        table.add_column(f"{symbol}", [f"{buy_quantities}", f"{buy_prices}", f"{', '.join(buy_times)}",
                                       f"{money_spent}", f"{sell_quantities}",
                                       f"{sell_prices}", f"{', '.join(sell_times)}",
                                       f"{money_gained}", f"{round(total_profit_loss, 2)}", holding_duration_str])
        table.align = "l"
        tables.append(table)
        
    for i in range(len(tables)):
        table_str = str(tables[i])
        centered_table_str = center_table(table_str, 150)  
        text_widget.text.insert(END, centered_table_str + "\n\n", "center")

def save_as_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    col_widths = [50, 50, 60, 30, 50, 50, 60, 30, 40, 40]  # Adjust column widths as needed

    def add_table_headers(headers):
        pdf.set_font("Arial", 'B', 12)
        for idx, header in enumerate(headers):
            pdf.cell(col_widths[idx], 10, header, border=1)
        pdf.ln(10)
        pdf.set_font("Arial", size=12)

    for table in tables:
        # Extract headers and rows from the PrettyTable object
        headers = table.field_names
        rows = table._rows

        # Write headers to the PDF
        add_table_headers(headers)

        # Write each row to the PDF
        for row in rows:
            if pdf.get_y() > 270:  # Adjust the value as needed to fit your page size
                pdf.add_page()
                add_table_headers(headers)
            for idx, data in enumerate(row):
                pdf.cell(col_widths[idx], 10, str(data), border=1)
            pdf.ln(10)
        pdf.ln(10)  # Add extra space between tables

    try:
        pdf.output(file_path)
        messagebox.showinfo("Success", "PDF file saved successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save PDF file: {e}")

def clear_screen():
    text_widget.text.configure(state='normal')  # Make the widget editable
    text_widget.text.delete('1.0', END)
    text_widget.text.configure(state='disabled')  # Make the widget read-only

def set_theme(theme_name):
    root.style.theme_use(theme_name)

def show_about():
    messagebox.showinfo("About Me", "This is a Trading Data Analyzer a Python-based application designed to help users analyze their " 
                        "trading data from CSV files. The application calculates profits and losses for each trade symbol, "
                        "and displays detailed analyses. Additionally, it allows users to save the analysis as a PDF file.\n\nMade With ❤️ By Asman ")

# Create main window
root = ttk.Window(themename="united")
root.iconbitmap("logo.ico")
root.title("Trading Data Analyzer 📈")
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")


# Add a menubar
menubar = Menu(root, background='blue', foreground='white')
root.config(menu=menubar)

# Add themes menu
themes_menu = Menu(menubar, tearoff=0, background='blue', foreground='white')
menubar.add_cascade(label="Themes", menu=themes_menu)

# Add available themes to the themes menu
available_themes = ttk.Style().theme_names()
for theme in available_themes:
    themes_menu.add_command(label=theme.capitalize(), command=lambda t=theme: set_theme(t))

# Add "About Me" menu
about_menu = Menu(menubar, tearoff=0, background='blue', foreground='white')
menubar.add_cascade(label="About Me", menu=about_menu)
about_menu.add_command(label="About", command=show_about)

frame = ttk.Frame(root, padding=10)
frame.pack(fill=BOTH, expand=True)

label = ttk.Label(frame, text="📂 Upload CSV File for Trading Data Analysis", font=("Times New Roman", 20))
label.pack(pady=10)

button_frame = ttk.Frame(frame)
button_frame.pack(pady=10)

select_csv_button = RoundedButton(button_frame, text=r"📄 Select CSV File", command=analyze_file, color="#007BFF", min_width=150, font_size=14)
select_csv_button.pack(side=LEFT, padx=15)

clear_button = RoundedButton(button_frame, text=r"🧹 Clear", command=clear_screen, color="#007BFF", min_width=150, font_size=14)
clear_button.pack(side=LEFT, padx=15)

save_pdf_button = RoundedButton(button_frame, text=r"💾 Save as PDF", command=save_as_pdf, color="#007BFF", min_width=200, font_size=14)
save_pdf_button.pack(side=LEFT, padx=15)

separator = ttk.Separator(frame, orient='horizontal')
separator.pack(fill='x', pady=15)

output_text = ScrolledText(frame, wrap='word', width=100, height=30, font=("Courier", 10))
output_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
text_widget = output_text  # Use the ScrolledText widget directly
text_widget.text.tag_configure("header", justify='center', font=("Arial", 16, "bold"))
text_widget.text.tag_configure("center", justify='center')  # Add this line
text_widget.text.configure(state='disabled')  # Make the widget read-only initially

root.mainloop()
