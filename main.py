from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time

driver = webdriver.Chrome()
driver.get("https://postakodu.ptt.gov.tr/")
wait = WebDriverWait(driver, 10)

crashes = []
provinces = []
districts = []
neighborhoods = []

province_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList1"))))
provinces_options = [(opt.get_attribute("value") ,opt.text.strip()) for opt in province_dropdown.options
                     if opt.get_attribute("value") != "-1"]

district_id = 1
neighborhood_id = 1

for province_code, province_name in provinces_options:
    provinces.append({
        "province_code": province_code,
        "province_name": province_name,
    })

    province_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList1"))))
    province_dropdown.select_by_value(province_code)
    time.sleep(1)

    try:
        districts_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList2"))))
        districts_options = [(opt.get_attribute("value"), opt.text.strip()) for opt in districts_dropdown.options
                             if opt.get_attribute("value") != "-1"]
    except Exception as e:
        print(f"No districts found {e}")
        crashes.append({
            "province_code": province_code,
            "province_name": province_name,
            "error": "{0} No districts found".format(str(e))
        })
        continue

    for district_code, district_name in districts_options:
        districts.append({
            "district_id": district_id,
            "district_code": district_code,
            "district_name": district_name,
            "province_code": province_code,
        })

        district_id += 1

        districts_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList2"))))
        districts_dropdown.select_by_value(district_code)
        time.sleep(1)

        try:
            neighborhoods_dropdown = Select(
                wait.until(EC.presence_of_element_located((By.ID, "MainContent_DropDownList3"))))
            time.sleep(1)
            for opt in neighborhoods_dropdown.options:
                if opt.get_attribute("value") != "-1":
                    parts = [p.strip() for p in opt.text.split("/")]

                    if len(parts) == 3:
                        neighborhood_name, town_name, neighborhood_pc = parts
                        neighborhoods.append({
                            "neighborhood_id": neighborhood_id,
                            "neighborhood_value": opt.get_attribute("value"),
                            "neighborhood_postalcode": neighborhood_pc,
                            "neighborhood_name": neighborhood_name,
                            "town_name": town_name,
                            "district_id": district_id
                        })
                    elif len(parts) == 4:
                        neighborhood_name = f"{parts[0]} {parts[1]}"
                        town_name, neighborhood_pc = parts[2], parts[3]
                        neighborhoods.append({
                            "neighborhood_id": neighborhood_id,
                            "neighborhood_value": opt.get_attribute("value"),
                            "neighborhood_postalcode": neighborhood_pc,
                            "neighborhood_name": neighborhood_name,
                            "town_name": town_name,
                            "district_id": district_id
                        })
                    else:
                        print(f"Unexpected format: {opt.text} (split into {len(parts)} parts)")
                        neighborhoods.append({
                            "neighborhood_id": neighborhood_id,
                            "opt_text": opt.text,
                            "district_id": district_id - 1
                        })

                    neighborhood_id += 1
        except Exception as e:
            print(f"No neighborhoods found {e}")
            crashes.append({
                "province_code": province_code,
                "province_name": province_name,
                "district_name": district_name,
                "error": "{0} No neighborhoods found".format(str(e))
            })
            continue


pd.DataFrame(provinces).to_csv("data/provinces.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(districts).to_csv("data/districts.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(neighborhoods).to_csv("data/neighborhoods.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(crashes).to_csv("crashes.csv", index=False, encoding="utf-8-sig")

print("All CSV files have been saved.")
driver.quit()