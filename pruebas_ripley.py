#Importaciones necesarias para el correcto funcionamiento del código
#Ejecutar en consola pip install selenium
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
from datetime import datetime
import os
import threading





class Pruebas_Ripley(unittest.TestCase):

    BASE_URL = "https://simple.ripley.cl/"

    #Ruta para guardar capturas

    OUTPUT_BASE_PATH = ''

    #Definir intervalos de capturas

    SCREENSHOT_INTERVAL = 0.1




    @classmethod
    def setUpClass(cls):
        #Configuración Inicial
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)


        # Archivo para guardar los tiempos de carga
        cls.log_file = f"ripley_performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(cls.log_file, 'w') as f:
            f.write("Registro de tiempos de carga - Ripley.cl\n")
            f.write("=" * 50 + "\n")

        # Crear directorios para screenshots y logs
        cls.test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        

        # Usar la ruta base, si no existe, crear una
        if not os.path.exists(cls.OUTPUT_BASE_PATH):
            os.makedirs(cls.OUTPUT_BASE_PATH)
            
        cls.screenshot_dir = os.path.join(cls.OUTPUT_BASE_PATH, f"grabacion_{cls.test_timestamp}")
        os.makedirs(cls.screenshot_dir, exist_ok=True)
        

        # Iniciar grabación continua
        cls.frame_count = 0
        cls.recording = True
        cls.recording_thread = threading.Thread(target=cls.continuous_recording)
        cls.recording_thread.daemon = True
        cls.recording_thread.start()

    @classmethod
    def continuous_recording(cls):
        """Método que graba continuamente la pantalla"""
        while cls.recording:
            try:
                timestamp = time.time()
                filename = os.path.join(
                    cls.screenshot_dir, 
                    f'frame_{cls.frame_count:06d}_{timestamp:.3f}.png'
                )
                cls.driver.save_screenshot(filename)
                cls.frame_count += 1
                time.sleep(cls.SCREENSHOT_INTERVAL)
            except Exception as e:
                print(f"Error en grabación: {e}")
                time.sleep(cls.SCREENSHOT_INTERVAL)


    def log_performance(self, action_name, start_time, end_time):
        """Registra los tiempos de carga en el archivo de log"""
        duration = end_time - start_time
        message = f"{action_name}: {duration:.2f} segundos"
        print(message)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


    def test_01_carga_pagina(self):
        
        inicio = time.time()
        self.driver.get(self.BASE_URL)

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            print(f"Error al cargar la página: {e}")
        fin = time.time()
        carga = fin - inicio
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")

        self.log_performance("Carga de página principal", inicio, fin)

        time.sleep(2)
        

    def test_02_iniciar_sesion(self):
        
        #Agregar credenciales aquí
        credentials={
            'rut': '',
            'contrasena': ''
        }

        inicio_boton = time.time()
        #presionar botón iniciar sesión
        try:
            presionar_boton = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/nav/main/nav/section[2]/div[1]/section/button"))
            )
            presionar_boton.click()
            print("El botón se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el botón: {e}")



        fin_boton = time.time()
        carga_boton = fin_boton - inicio_boton
        print(f"El tiempo de carga luego de presionar el botón de inicio de sesión hasta el formulario es de: {carga_boton:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de página luego de presionar el botón de inicio de sesión hasta el formulario", inicio_boton, fin_boton)


        time.sleep(2)


        #Ingresar rut
        try:
            ingresar_rut = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="identifier"]'))
            )
            ingresar_rut.send_keys(credentials['rut']) 
            ingresar_rut.send_keys(Keys.TAB)
            print("El rut se ha ingresado correctamente")
            time.sleep(2)
        except Exception as e:
            print(f"Error al ingresar el rut: {e}")

        #Ingresar contraseña
        try:
            ingresar_contrasena = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
            )
            ingresar_contrasena.send_keys(credentials['contrasena'])
            print("La contraseña se ha ingresado correctamente")

        except Exception as e:
            print(f"Error al ingresar la contraseña: {e}")

        #Presionar botón Iniciar sesión

        try:
            boton_iniciar_sesión = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="login"]'))
            )
            inicio_carga = time.time()  
            boton_iniciar_sesión.click()
            print(f"El botón de iniciar sesión se ha presionado correctamente")
            

        except Exception as e:
            print(f"Error al presionar el botón de iniciar sesión: {e}")
            
        

        #Esperar a que cambie la url

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.current_url != self.BASE_URL
            )
            print("Redirección detectada")
        except Exception as e:
            print(f"Error al detectar la redirección: {e}")
            
        

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
            

        fin_carga = time.time()
        carga = fin_carga - inicio_carga
        print(f"El tiempo de carga de la pagina luego de presionar el botón de inicio de sesión es de: {carga:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de página luego de presionar el botón de inicio de sesión", inicio_carga, fin_carga)

        time.sleep(3)
    
    def test_03_buscar_producto(self):

        

        #Presionar barra de busqueda
        try:
            presionar_barra = WebDriverWait(self.driver,  30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            presionar_barra.click()
            print("Se ha presionado correctamente la barra de búsqueda")
            time.sleep(2)
        except Exception as e:
            print(f"Error al presionar la barra de búsqueda: {e}")

        #Ingresar datos o producto a buscar

        try:
            buscar_producto = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            buscar_producto.send_keys("Layton Parfums de Marly")
            inicio_busqueda = time.time()
            buscar_producto.send_keys(Keys.ENTER)
            print("El producto a buscar se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar el producto a buscar: {e}")

        fin_busqueda = time.time()
        carga_busqueda = fin_busqueda - inicio_busqueda
        print(f"La carga de la búsqueda es de: {carga_busqueda:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de página al realizar búsqueda", inicio_busqueda, fin_busqueda)


        time.sleep(2)

    #Testeo para seleccionar producto

    def test_04_seleccionar_producto(self):


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
            print(f"Error al cargar la página: {e}")
            

        fin_seleccion = time.time()
        carga = fin_seleccion - inicio_seleccion
        print(f"El tiempo de carga de la pagina luego de presionar el botón de inicio de sesión es de: {carga:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de página luego de presionar el botón de inicio de sesión", inicio_seleccion, fin_seleccion)

        time.sleep(2)

    #Testep para agregar productos al carrito

    def test_05_agregar_carrito(self):

        try:

            agregar_producto = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="buy-button"]'))
            )
            agregar_producto.click()
            print("Se agregó el producto al carrito")
            time.sleep(3)

        except Exception as e:
            print(f"No se pudo agregar el producto al carrito: {e}")
    

    # Testeo para ver el perfil
    def test_06_ver_perfil(self):

        time.sleep(5)

        #Click en botón de cuenta
        try:
            presionar_boton = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/header/section/nav/div/div[2]/div[1]/div/div/a/div'))
            )
            presionar_boton.click()
            print("El botón de cuenta se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el botón: {e}")


        #Click para redirigir a la cuenta

        try:
            presionar_cuenta = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//li[@class='credentials__my-account-link']/a[text()='Mi cuenta']"))
            )
            inicio_cuenta = time.time()
            presionar_cuenta.click()
            print("Se ha presionado la cuenta correctamente")
        except Exception as e:
            print(f"Error al presionar la cuenta: {e}")

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div"))
            )
            print("El componente 'Mis datos personales' se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar el componente 'Mis datos personales': {e}")

        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
        

        fin_cuenta = time.time()
        tiempo_carga = fin_cuenta - inicio_cuenta
        self.log_performance("El tiempo de carga del componente 'Mis datos personales'", inicio_cuenta, fin_cuenta)
        print(f"El tiempo de carga del componente 'Mis datos personales' es de: {tiempo_carga:.2f} segundos")
        print(f"El tiempo de carga despúes de presionar el botón de cuenta es de: {tiempo_carga:.2f} segundos")

        self.log_performance("Carga de página luego de presionar el botón de cuenta", inicio_cuenta, fin_cuenta)

        time.sleep(2)
            

        



    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
