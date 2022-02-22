import random
from time import sleep
from selenium import webdriver

driver = webdriver.Edge('./msedgedriver.exe')
options = webdriver.EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(options=options)
driver.get('https://www.carrefour.es/bodega/vinos-tintos/vinos-tintos-nacionales/ver-todos/N-1dxafdm/c?No=0&Nr%3DAND%28product.salepointWithActivePrice_004583%3A1%2Cproduct.shopCodes%3A004583%2COR%28product.siteId%3AbodegaSite%29%29OR%29')

print(driver.title)
print(driver.current_url)

driver.quit()