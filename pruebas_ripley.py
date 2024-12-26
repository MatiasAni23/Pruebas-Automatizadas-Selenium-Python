import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time



class Pruebas_Ripley(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Configuración Inicial
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)

    def test_01_carga_pagina(self):
        
        url = "https://simple.ripley.cl/"
        inicio = time.time()
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            print("Error al cargar la página: {e}")
        fin = time.time()
        carga = fin - inicio
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")

        time.sleep(2)
        

    def test_02_iniciar_sesion(self):
        
        url = "https://simple.ripley.cl/"
        inicio_boton = time.time()
        #presionar botón iniciar sesión
        try:
            presionar_boton = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/nav/main/nav/section[2]/div[1]/section/button"))
            )
            presionar_boton.click()
            print("El botón se ha presionado correctamente")
        except Exception as e:
            print("Error al presionar el botón")



        fin_boton = time.time()
        carga_boton = fin_boton - inicio_boton
        print(f"El tiempo de carga luego de presionar el botón de inicio de sesión hasta el formulario es de: {carga_boton:.2f} segundos")
        time.sleep(2)


        #Ingresar rut
        try:
            ingresar_rut = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="identifier"]'))
            )
            ingresar_rut.send_keys("") #Agregar credenciales
            ingresar_rut.send_keys(Keys.TAB)
            print("El rut se ha ingresado correctamente")
            time.sleep(2)
        except Exception as e:
            print("Error al ingresar el rut")

        #Ingresar contraseña
        try:
            ingresar_contrasena = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
            )
            ingresar_contrasena.send_keys("") #Agregar credenciales
            print("La contraseña se ha ingresado correctamente")

        except Exception as e:
            print(f"Error al ingresar la contraseña")

        #Presionar botón Iniciar sesión

        try:
            boton_iniciar_sesión = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="login"]'))
            )
            inicio_carga = time.time()  
            boton_iniciar_sesión.click()
            print(f"El botón de iniciar sesión se ha presionado correctamente")
            

        except Exception as e:
            print(f"Error al presionar el botón de iniciar sesión {e}")
            
        

        #Esperar a que cambie la url

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.current_url != url
            )
            print("Redirección detectada")
        except Exception as e:
            print(f"Error al detectar la redirección {e}")
            
        

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print("Error al cargar la página: {e}")
            

        fin_carga = time.time()
        carga = fin_carga - inicio_carga
        print(f"El tiempo de carga de la pagina luego de presionar el botón de inicio de sesión es de: {carga:.2f} segundos")

        time.sleep(5)
    
    def test_buscar_producto(self):

        

        #Presionar barra de busqueda
        try:
            presionar_barra = WebDriverWait(self.driver,  30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            presionar_barra.click()
            print("Se ha presionado correctamente la barra de búsqueda")
            time.sleep(2)
        except Exception as e:
            print("Error al presionar la barra de búsqueda")

        #Ingresar datos o producto a buscar

        try:
            buscar_producto = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            buscar_producto.send_keys("Perfume Stronger With You")
            inicio_busqueda = time.time()
            buscar_producto.send_keys(Keys.ENTER)
            print("El producto a buscar se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar el producto a buscar")

        fin_busqueda = time.time()
        carga_busqueda = fin_busqueda - inicio_busqueda
        print(f"La carga de la búsqueda es de: {carga_busqueda:.2f} segundos")
        time.sleep(5)


    def test_seleccionar_producto(self):


        try:
            seleccionar_producto = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[9]/div[1]/div/div[1]/div[3]/section/div/div/div[1]/div/a/div[3]'))
            )
            inicio_seleccion = time.time()
            seleccionar_producto.click()
            print("Se seleccionó el producto correctamente")
        except Exception as e:
            print(f"No se pudo seleccionar el producto: {e}")


        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print("Error al cargar la página: {e}")
            

        fin_seleccion = time.time()
        carga = fin_seleccion - inicio_seleccion
        print(f"El tiempo de carga de la pagina luego de presionar el botón de inicio de sesión es de: {carga:.2f} segundos")
        time.sleep(5)


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()