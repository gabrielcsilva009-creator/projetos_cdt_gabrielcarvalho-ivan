from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def preencher_matricula(dados: dict):
    URL_SITE = "http://localhost:5000"  # Substitua pela URL/IP do site do seu colega
    
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico)
    
    try:
        driver.get(URL_SITE)
        wait = WebDriverWait(driver, 10)
        
        # Ajuste os IDs abaixo conforme o HTML do site
        wait.until(EC.presence_of_element_located((By.ID, "nome"))).send_keys(dados['nome'])
        driver.find_element(By.ID, "cpf").send_keys(dados['cpf'])
        driver.find_element(By.ID, "email").send_keys(dados['email'])
        
        # Clica no botão de envio
        driver.find_element(By.ID, "btn-cadastrar").click()
        return True
    finally:
        driver.quit()