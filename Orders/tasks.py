import tempfile
import time
import os
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import shutil
from pathlib import Path
import glob

@task
def order_robots_from_RobotSpareBin():
    open_robot_order_website()
    download_csv()
    loop_orders()

def open_robot_order_website():
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def download_csv():
    http = HTTP()
    http.download('https://robotsparebinindustries.com/orders.csv', overwrite=True)

def get_orders():
    files = Tables()
    orders = files.read_table_from_csv(path='orders.csv', header=True, dialect="excel")
    return orders

def loop_orders():
    orders = get_orders()
    for order in orders:
        print(order)
        close_annoying_modal()
        fill_the_form(order)
        archive_receipts()

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f"#id-body-{str(order['Body'])}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    page.click("#order")
    time.sleep(1)
    try:
        store_receipt_as_pdf(order["Order number"])
    except:
        page.click("#order")
        time.sleep(1)
        store_receipt_as_pdf(order["Order number"])
    embed_screenshot_to_receipt("output/temp.png", f"output/order_receipt_{str(order['Order number'])}.pdf")
    page.click("#order-another")
    time.sleep(1)

def store_receipt_as_pdf(order_number):
    page = browser.page()
    pdf = PDF()
    try:
        order_receipt_html = page.locator("#receipt").inner_html()
    except:
        page.click("#order")
        time.sleep(1)
        order_receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(order_receipt_html, f"output/order_receipt_{str(order_number)}.pdf")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    page = browser.page()
    page.screenshot(path=screenshot)
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)
    os.remove(screenshot)

def archive_receipts():
    source_directory = Path("output")
    pdf_files = glob.glob(str(source_directory / "*.pdf"))
    with tempfile.TemporaryDirectory() as temp_dir:
        for pdf in pdf_files:
            shutil.copy(pdf, temp_dir)
        shutil.make_archive("Robots", 'zip', temp_dir)