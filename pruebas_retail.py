#importaciones necesarias para el correcto funcionamiento del código
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import pygetwindow as gw
import threading
import subprocess
import time
import os



class Pruebas_retail(unittest.TestCase):
    output_folder = "" #Carpeta de salida para guardar los videos
    CHROME_DRIVER_PATH = "" #Ruta del driver de Chrome

    CREDENTIALS = {'email': '', 'password': '',  'rut': ''}

    urls = ['https://www.falabella.com/falabella-cl',
            'https://www.paris.cl',
            'https://simple.ripley.cl/']
    
    FFmpeg_COMMANDS = []

    @classmethod
    def setUpClass(cls):
        # Configuración Inicial
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')  # Desactivar GPU
        chrome_options.add_argument('--disable-software-rasterizer')
        service = Service(executable_path="chromedriver.exe")
        


        # Archivo de log de tiempos y texto para FFmpeg
        cls.log_file = f"performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        cls.overlay_text_file = "overlay_text.txt"

        with open(cls.log_file, 'w') as f:
            f.write("Registro de tiempos de carga\n" + "=" * 50 + "\n")
        with open(cls.overlay_text_file, 'w') as f:
            f.write("")


        # Carpeta para guardar los videos
        cls.test_timestamp = time.strftime('%Y%m%d_%H%M%S')
        cls.output_dir = os.path.join(cls.output_folder, f"grabacion_{cls.test_timestamp}")
        os.makedirs(cls.output_dir, exist_ok=True)  # Crear la carpeta si no existe

        #Primera Ventana

        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.get(cls.urls[0])

        #Segunda Ventana
        cls.driver2 = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver2.get(cls.urls[1])

        #Tercera Ventana
        cls.driver3 = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver3.get(cls.urls[2])  


        # Iniciar grabación para cada ventana en un hilo
        cls.grabar_multiples_ventanas()


    #Función para grabar multiples ventanas
    @classmethod
    def grabar_multiples_ventanas(cls):
        #Titulos de las ventanas
        windows_titles = ["Falabella", "Paris", "Ripley"] #Agregar títulos de ventanas aqui
        for i, title in enumerate(windows_titles):
            output_file = os.path.join(cls.output_dir, f"grabacion_{title}_{cls.test_timestamp}.mp4") #Archivo de salida
            record_thread = threading.Thread(target=cls.iniciar_ffmpeg, args=(i, title, output_file)) #Iniciar FFmpeg en un hilo separado
            record_thread.daemon = True #Hacer que el hilo termine automáticamente cuando termine el proceso principal
            record_thread.start() #Iniciar el hilo

    
    #Función para iniciar FFmpeg
    @classmethod
    def iniciar_ffmpeg(cls, i, windows_titles, output_file):
        """Inicia FFmpeg para grabar una ventana específica utilizando FFmpeg"""
        windows = gw.getWindowsWithTitle(windows_titles) #Obtener la ventana por título
        if not windows:
            print(f"No se encontró la ventana {windows_titles}")
            return
        
        windows = windows[0] #Obtener la primera ventana
        hwnd = windows._hWnd #Obtener el HWND de la ventana

        #Comandos FFmpeg
        ffmpeg_cmd = [
            "C:/webm/bin/ffmpeg", #Ruta de FFmpeg
            "-f", "gdigrab", #Formato de captura
            "-i", f"hwnd={hwnd}", #Pasar el HWND como entrada
            "-framerate", "30", #Framerate
            "-vf", (
                f"drawtext=textfile={cls.overlay_text_file}:"
                f"x='main_w-text_w-10':y='main_h-text_h-50':"  # Texto en esquina inferior derecha
                f"fontsize=32:fontcolor=red:box=1:boxcolor=black@0.2:reload=1,"
                f"drawtext=fontfile=/path/to/font.ttf:"
                f"text='%{{pts\\:hms}}':"
                f"x='main_w-text_w-10':y='main_h-text_h-80':"  # Cronómetro justo encima del texto
                f"fontsize=32:fontcolor=red:box=1:boxcolor=black@0.2"  # Cronómetro con fondo
        ),
            "-c:v", "libx264", #Codec de video
            "-preset", "ultrafast", #Velocidad de compresión
            "-crf", "28", #Calidad de compresión (Con valores más altos menor calidad de video)
            "-c:a", "aac", #Codec de audio
            "-y", #Sobreescribir el archivo de salida si ya existe
            output_file #Archivo de salida
        ]

        #Ejecutar FFmpeg en un proceso separado
        subprocess.run(ffmpeg_cmd) #Iniciar el proceso
        print(f"Iniciando grabacion de: {windows_titles}") 
        process = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate() #Obtener la salida del proceso

        print("FFmpeg stdout:", stdout.decode())
        print("FFmpeg stderr:", stderr.decode())
        cls.FFmpeg_COMMANDS.append(process)

    #Función para detener FFmpeg
    @classmethod
    def detener_ffmpeg(cls):
        for process in cls.FFmpeg_COMMANDS:
            try:
                process.terminate()
                process.wait()
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
            except Exception as e:
                print(f"Error al detener FFmpeg: {e}")
        cls.FFmpeg_COMMANDS.clear()



    def log_performance(self, action_name, start_time, end_time):
        duration = end_time - start_time
        message = f"{action_name}: {duration:.2f} segundos"

        # Log a archivo
        with open(self.log_file, 'a') as f:
            f.write(message + "\n")

        # **Sobrescribir el texto en overlay_text.txt**
        with open(self.overlay_text_file, 'w') as f:
            f.write(message)  # **Elimina "\\n" para evitar errores de codificación en FFmpeg**

        print(message)



    def test_01_carga_pagina_falabella(self):
        print("Test_01")
        print("Falabella")
        print("-" * 50)

        inicio_carga = time.time()
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete" #Esperar a que la página se cargue completamente
            )
            print("Pagina cargada completamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
            
        fin_carga = time.time()
        carga = fin_carga - inicio_carga

        time.sleep(5)

        #Imprimir el tiempo de carga
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")
        #Almacenar el tiempo de carga en el archivo log
        self.log_performance("Carga de pagina principal - Falabella", inicio_carga, fin_carga)


    def test_02_boton_login(self):
        print("Test_02")
        print("Falabella")
        print("-" * 50)

        #Buscar el botón de inicio de sesión

        try:
            boton_login = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/header/div[2]/div/div[4]/ul/li[1]/div/div[1]/div/div[2]/p'))
            )
        except Exception as e:
            print(f"Error al buscar el botón de inicio de sesion - Falabella: {e}")


        actions = ActionChains(self.driver)

        actions.move_to_element(boton_login).perform()

        
        try:
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="testId-loggedout-item-0"]'))
            )
            print("Botón de inicio de sesion encontrado")
        except Exception as e:
            print(f"Error al buscar el boton de inicio de sesion - Falabella: {e}")
            return
        
        login_button.click()

        time.sleep(3)

    def test_03_iniciar_sesion_falabella(self):
        print("Test_03")
        print("Falabella")
        print("-" * 50)

        #Ingresar email
        try:
            ingresar_email = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="testId-cc-login-form-email-input"]'))
            )
            ingresar_email.send_keys(self.CREDENTIALS['email'])
            print("El email se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar el email: {e}")

        #Ingresar contraseña
        try:
            ingresar_contrasena = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="testId-cc-login-form-password-input"]'))
            )
            ingresar_contrasena.send_keys(self.CREDENTIALS['password2'])
            print("La contraseña se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar la contraseña: {e}")

        #Presionar botón Iniciar sesión
        try:
            boton_iniciar_sesion = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'testId-cc-login-form-submit'))
            )
            inicio_carga = time.time()
            boton_iniciar_sesion.click()
            print("El boton de iniciar sesion se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el botón de iniciar sesion: {e}")

        #Esperar a que cambie la url
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.current_url != self.urls[0]
            )
            print("Redirección detectada")
        except Exception as e:
            print(f"Error al detectar la redirección: {e}")

        #Medir tiempo de carga de la página
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")

        except Exception as e:
            print(f"Error al cargar la pagina: {e}")
        
        fin_carga = time.time()
        carga = fin_carga - inicio_carga
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")

        #Almacenar el tiempo de carga en el archivo log
        self.log_performance("Carga de pagina luego de presionar el boton de inicio de sesion - Falabella", inicio_carga, fin_carga)

        time.sleep(3)

    
    def test_04_busqueda_producto(self):
        print("Test_04")
        print("Falabella")
        print("-" * 50)

        #Buscar producto
        try:
            buscar_producto = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="testId-SearchBar-Input"]'))
            )
            buscar_producto.send_keys("Playstation 5")
            buscar_producto.send_keys(Keys.ENTER)
            print("Producto encontrado")
        except Exception as e:
            print(f"Error al buscar el producto: {e}")

        time.sleep(2)




    def test_05_carga_pagina_paris(self):
        print("Test_01")
        print("Paris")
        print("-" * 50)

        inicio_carga = time.time()
        try:
            WebDriverWait(self.driver2, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete" #Esperar a que la página se cargue completamente
            )
            print("Página cargada completamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
            
        fin_carga = time.time()
        carga = fin_carga - inicio_carga

        #Imprimir el tiempo de carga
        print(f"El tiempo de carga de la pagina de Paris.cl es de: {carga:.2f} segundos")
        #Almacenar el tiempo de carga en el archivo log
        self.log_performance("Carga de pagina principal - Paris.cl", inicio_carga, fin_carga)

        time.sleep(3)



    def test_06_boton_login_paris(self):
        print("Test_02")
        print("Paris")
        print("-" * 50)

        #Buscar el botón de inicio de sesión

        try:
            boton_login = WebDriverWait(self.driver2, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/header/div[2]/div/nav/div[4]/div/div[1]/div/button/div[2]/div[2]'))
            )
        except Exception as e:
            print(f"Error al buscar el botón de inicio de sesion - Paris.cl: {e}")


        actions = ActionChains(self.driver2)

        actions.move_to_element(boton_login).perform()

        
        try:
            login_button = WebDriverWait(self.driver2, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/header/div[2]/div/nav/div[4]/div/div[1]/div/div/div/div/div/div[1]/button'))
            )
            print("Botón de inicio de sesión encontrado")
        except Exception as e:
            print(f"Error al buscar el botón de inicio de sesion - Paris.cl: {e}")
            return
        
        login_button.click()

        time.sleep(3)


    def test_07_iniciar_sesion_paris(self):

        print("Test_03")
        print("Paris")
        print("-" * 50)

        #Ingresar email
        try:
            ingresar_email = WebDriverWait(self.driver2, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dwfrm_login_username"]'))
            )
            ingresar_email.send_keys(self.CREDENTIALS['email'])
            print("El email se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar el email: {e}")

        #Ingresar contraseña
        try:
            ingresar_contrasena = WebDriverWait(self.driver2, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dwfrm_login_password"]'))
            )
            ingresar_contrasena.send_keys(self.CREDENTIALS['password'])
            print("La contraseña se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar la contraseña: {e}")

        #Presionar botón Iniciar sesión
        try:
            boton_iniciar_sesion = WebDriverWait(self.driver2, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[17]/div[2]/div/form/div[4]'))
            )
            inicio_carga = time.time()
            boton_iniciar_sesion.click()
            print("El botón de iniciar sesion se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el boton de iniciar sesion: {e}")

        #Esperar a que cambie la url
        try:
            WebDriverWait(self.driver2, 10).until(
                lambda d: d.current_url != self.urls[1]
            )
            print("Redirección detectada")
        except Exception as e:
            print(f"Error al detectar la redirección: {e}")

        #Medir tiempo de carga de la página
        try:
            WebDriverWait(self.driver2, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")

        fin_carga = time.time()
        carga = fin_carga - inicio_carga
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")

        #Almacenar el tiempo de carga en el archivo log
        self.log_performance("Carga de pagina luego de presionar el botón de inicio de sesion - Paris.cl", inicio_carga, fin_carga)

        time.sleep(3)
        

    def test_08_busqueda_producto(self):
        print("Test_04")
        print("Paris")
        print("-" * 50)

        #Buscar producto

        try:
            buscar_producto = WebDriverWait(self.driver2, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="desktop-search__form-input"]'))
            )
            buscar_producto.send_keys("Audifonos Bluetooth")
            buscar_producto.send_keys(Keys.ENTER)
            print("Producto encontrado")
        except Exception as e:
            print(f"Error al buscar el producto: {e}")

        time.sleep(2)

        


    def test_09_carga_pagina_ripley(self):
        print("Test_01")
        print("Ripley")
        print("-" * 50)

        inicio_carga = time.time()
        try:
            WebDriverWait(self.driver3, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete" #Esperar a que la página se cargue completamente
            )
            print("Página cargada completamente")
        except Exception as e:
            print(f"Error al cargar la pagina - Ripley.cl: {e}")
            
        fin_carga = time.time()
        carga = fin_carga - inicio_carga

        #Imprimir el tiempo de carga
        print(f"El tiempo de carga de la pagina es de: {carga:.2f} segundos")
        #Almacenar el tiempo de carga en el archivo log
        self.log_performance("Carga de pagina principal - Ripley.cl", inicio_carga, fin_carga)


        time.sleep(3)

    def test_10_iniciar_sesion(self):
        
        
        print("Test_02")
        print("*" * 50)
        inicio_boton = time.time()
        #presionar botón iniciar sesión
        try:
            presionar_boton = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/nav/main/nav/section[2]/div[1]/section/button"))
            )
            presionar_boton.click()
            print("El botón se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el botón: {e}")



        fin_boton = time.time()
        carga_boton = fin_boton - inicio_boton
        print(f"El tiempo de carga luego de presionar el boton de inicio de sesion hasta el formulario es de: {carga_boton:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de pagina luego de presionar el boton de inicio de sesion hasta el formulario - Ripley.cl", inicio_boton, fin_boton)


        time.sleep(2)


        #Ingresar rut
        try:
            ingresar_rut = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="identifier"]'))
            )
            ingresar_rut.send_keys(self.CREDENTIALS['rut']) 
            ingresar_rut.send_keys(Keys.TAB)
            print("El rut se ha ingresado correctamente")
            time.sleep(2)
        except Exception as e:
            print(f"Error al ingresar el rut: {e}")

        #Ingresar contraseña
        try:
            ingresar_contrasena = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
            )
            ingresar_contrasena.send_keys(self.CREDENTIALS['password'])
            print("La contraseña se ha ingresado correctamente")

        except Exception as e:
            print(f"Error al ingresar la contraseña: {e}")

        #Presionar botón Iniciar sesión

        try:
            boton_iniciar_sesión = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="login"]'))
            )
            inicio_carga = time.time()  
            boton_iniciar_sesión.click()
            print(f"El boton de iniciar sesion se ha presionado correctamente")
            

        except Exception as e:
            print(f"Error al presionar el boton de iniciar sesion: {e}")
            
        

        #Esperar a que cambie la url

        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.current_url != self.urls[2]
            )
            print("Redirección detectada")
        except Exception as e:
            print(f"Error al detectar la redirección: {e}")
            
        
        #Medir tiempo de carga de la pagina

        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente - Ripley.cl")
        except Exception as e:
            print(f"Error al cargar la pagina: {e}")
            

        fin_carga = time.time()
        carga = fin_carga - inicio_carga
        print(f"El tiempo de carga de la pagina luego de presionar el boton de inicio de sesion es de: {carga:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de pagina luego de presionar el boton de inicio de sesion", inicio_carga, fin_carga)

        time.sleep(3)

    def test_11_buscar_producto(self):

        
        print("Test_03")
        print("*" * 50)
        #Presionar barra de busqueda
        try:
            presionar_barra = WebDriverWait(self.driver3,  30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            presionar_barra.click()
            print("Se ha presionado correctamente la barra de búsqueda")
            time.sleep(2)
        except Exception as e:
            print(f"Error al presionar la barra de búsqueda: {e}")

        #Ingresar datos o producto a buscar

        try:
            buscar_producto = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/section/nav/main/nav/div/form/input'))
            )
            buscar_producto.send_keys("Layton Parfums de Marly")
            time.sleep(2)
            inicio_busqueda = time.time()
            buscar_producto.send_keys(Keys.ENTER)
            print("El producto a buscar se ha ingresado correctamente")
        except Exception as e:
            print(f"Error al ingresar el producto a buscar: {e}")

        fin_busqueda = time.time()
        carga_busqueda = fin_busqueda - inicio_busqueda
        print(f"La carga de la búsqueda es de: {carga_busqueda:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de pagina al realizar busqueda", inicio_busqueda, fin_busqueda)


        time.sleep(2)

#Testeo para seleccionar producto y cuanto se demora en transición de paginas

    def test_12_seleccionar_producto(self):

        print("Test_04")
        print("*" * 50)


        try:
            seleccionar_producto = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[9]/div[1]/div/div[1]/div[3]/section/div/div/div[1]/div/a/div[3]'))
            )
            inicio_seleccion = time.time()
            seleccionar_producto.click()
            print("Se seleccionó el producto correctamente")
        except Exception as e:
            print(f"No se pudo seleccionar el producto: {e}")


        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La pagina se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
            

        fin_seleccion = time.time()
        carga = fin_seleccion - inicio_seleccion
        print(f"El tiempo de carga de la pagina luego de seleccionar el producto y cargar la pagina: {carga:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de pagina luego de presionar el producto y cargar la pagina", inicio_seleccion, fin_seleccion)

        time.sleep(2)

    #Testep para agregar productos al carrito

    def test_13_agregar_carrito(self):

        print("Test_05")
        print("*" * 50)

        try:

            agregar_producto = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="buy-button"]'))
            )
            agregar_producto.click()
            print("Se agregó el producto al carrito")
            time.sleep(3)

        except Exception as e:
            print(f"No se pudo agregar el producto al carrito: {e}")
    

    # Testeo para ver el perfil y cuanto se demora cada componente dentro de la pagina

    def test_14_ver_perfil(self):

        print("Test_06")
        print("*" * 50)

        time.sleep(5)

        #Click en botón de cuenta
        try:
            presionar_boton = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/header/section/nav/div/div[2]/div[1]/div/div/a/div'))
            )
            presionar_boton.click()
            print("El boton de cuenta se ha presionado correctamente")
        except Exception as e:
            print(f"Error al presionar el boton: {e}")


        #Click para redirigir a la cuenta

        try:
            presionar_cuenta = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, "//li[@class='credentials__my-account-link']/a[text()='Mi cuenta']"))
            )
            inicio_cuenta = time.time()
            presionar_cuenta.click()
            print("Se ha presionado la cuenta correctamente")
        except Exception as e:
            print(f"Error al presionar la cuenta: {e}")
        

        #Carga componente Mis datos personales
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div"))
            )
            print("El componente 'Mis datos personales' se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar el componente 'Mis datos personales': {e}")


        fin_datos = time.time()
        carga_datos = fin_datos - inicio_cuenta


        #Carga componente contenedor izquierdo
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div'))
            )
            print("El contenedor izquierdo se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar el contenedor: {e}")

        fin_contenedor = time.time()
        carga_contenedor = fin_contenedor - inicio_cuenta


        #Carga ripley puntos
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div[1]/a/div'))
            )
        except Exception as e:
            print(f"Error al cargar el contenedor de ripley puntos: {e}")

        fin_puntos = time.time()
        carga_puntos = fin_puntos - inicio_cuenta


        #Carga página completa
        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La pagina se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la pagina: {e}")
        

        fin_cuenta = time.time()
        tiempo_carga = fin_cuenta - inicio_cuenta
        

        #Imprimir resultados
        print(f"El tiempo de carga del componente 'Mis datos personales' es de: {carga_datos:.2f} segundos")
        print(f"El tiempo de carga del contenedor izquierdo es de: {carga_contenedor:.2f} segundos")
        print(f"El tiempo de carga del contenedor de ripley puntos es de: {carga_puntos:.2f} segundos")
        print(f"El tiempo de carga despues de presionar el boton de cuenta es de: {tiempo_carga:.2f} segundos")

        #Almacenar resultados
        self.log_performance("El tiempo de carga del componente 'Mis datos personales'", inicio_cuenta, fin_datos)
        self.log_performance("El tiempo de carga del contenedor izquierdo", inicio_cuenta, fin_contenedor)
        self.log_performance("El tiempo de carga del contenedor de ripley puntos", inicio_cuenta, fin_puntos)
        self.log_performance("Carga de pagina luego de presionar el boton de cuenta", inicio_cuenta, fin_cuenta)

        time.sleep(2)


    # Testeos de los tiempos de carga para los elementos de la barra lateral

    def test_15_click_elemento_compras(self):

        print("Test_07")
        print("*" * 50)
        
        #Click en compras realizadas
        try:
            presionar_compras = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[1]/a/span[1]'))
            )
            inicio_compras = time.time()
            presionar_compras.click()
            print("Se ha presionado compras realizadas correctamente")
        except Exception as e:
            print(f"Error al presionar compras realizadas: {e}")



        #Carga contenedores de productos comprados
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div'))
            )
        except Exception as e:
            print(f"Error al cargar el contenedor de productos comprados : {e}")

        fin_compras = time.time()
        carga_compras = fin_compras - inicio_compras

        print(f"El tiempo de carga de productos comprados es de: {carga_compras:.2f} segundos")

        

        #Carga de elementos dentro del contenedor de productos comprados
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/div/div/div/div[3]')) #contenedor de datos (fecha retiro, direccion y quien retira)
            )

        except Exception as e:
            print(f"Error al cargar los elementos dentro del contenedor de productos comprados : {e}")

        fin_elementos = time.time()
        carga_elementos = fin_elementos - inicio_compras

        print(f"El tiempo de carga de los elementos dentro del contenedor de productos comprados es de: {carga_elementos:.2f} segundos")

        


        #Carga página completa
        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")

        fin_carga_seccion_compras = time.time()
        carga_seccion_compras = fin_carga_seccion_compras - inicio_compras

        print(f"El tiempo de carga de la seccion de compras es de: {carga_seccion_compras:.2f} segundos")



        #Almacenar resultados
        self.log_performance("Carga de productos comprados", inicio_compras, fin_compras)
        self.log_performance("Carga de elementos dentro del contenedor de productos comprados", inicio_compras, fin_elementos)
        self.log_performance("Carga de la seccion de compras", inicio_compras, fin_carga_seccion_compras)

        time.sleep(2)

    def test_16_click_solicitudes(self):


        print("Test_08")
        print("*" * 50)

        #click en solicitudes de atención
        try:
            presionar_solicitudes = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[2]/a[1]/span[1]'))
            )
            inicio_solicitudes = time.time()
            presionar_solicitudes.click()
            print("Se ha presionado solicitudes de atencion correctamente")
        except Exception as e:
            print(f"Error al presionar solicitudes de atencion: {e}")


        #Carga contenedores de solicitudes de atención

        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div'))
            )
        except Exception as e:
            print(f"Error al cargar el contenedor de solicitudes de atención : {e}") 

        fin_carga_cont_solicitudes = time.time()
        carga_cont_solicitudes = fin_carga_cont_solicitudes - inicio_solicitudes

        print(f"El tiempo de carga de solicitudes de atencion es de: {carga_cont_solicitudes:.2f} segundos")


        #Carga completa de la pagina
        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")

        fin_solicitudes = time.time()
        carga_solicitudes = fin_solicitudes - inicio_solicitudes

        print(f"El tiempo de carga de la página luego de presionar solicitudes de atencion es de: {carga_solicitudes:.2f} segundos")


        #Almacenar Resultados
        self.log_performance("Carga de solicitudes de atencion", inicio_solicitudes, fin_carga_cont_solicitudes)
        self.log_performance("Carga de la página luego de presionar solicitudes de atencion", inicio_solicitudes, fin_solicitudes)


        time.sleep(2)
            


    def test_17_click_ripley_puntos(self):
        
        print("Test_09")
        print("*" * 50)



        #Click en ripley puntos Go

        try:
            presionar_ripley_puntos = WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[4]/a[1]/span[1]'))
            )
            inicio_ripley_puntos = time.time()
            presionar_ripley_puntos.click()
            print("Se ha presionado ripley puntos correctamente")

        except Exception as e:
            print(f"Error al presionar ripley puntos: {e}")


        #Carga contenedores de ripley puntos

        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]'))
            )
        except Exception as e:
            print(f"Error al cargar el contenedor de ripley puntos : {e}")

        fin_carga_cont_ripley_puntos = time.time()
        carga_cont_ripley_puntos = fin_carga_cont_ripley_puntos - inicio_ripley_puntos

        print(f"El tiempo de carga de ripley puntos es de: {carga_cont_ripley_puntos:.2f} segundos")


        #Carga de canjeo ripley puntos
        try:
            WebDriverWait(self.driver3, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[2]'))
            )
        except Exception as e:
            print(f"Error al cargar el contenedor de ripley puntos : {e}")

        fin_canjeo_ripley_puntos = time.time()
        carga_cont_ripley_puntos = fin_canjeo_ripley_puntos - inicio_ripley_puntos

        print(f"El tiempo de carga de ripley puntos es de: {carga_cont_ripley_puntos:.2f} segundos")




        #Carga completa de la pagina
        try:
            WebDriverWait(self.driver3, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("La página se ha cargado correctamente")
        except Exception as e:
            print(f"Error al cargar la página: {e}")

        fin_ripley_puntos = time.time()
        carga_ripley_puntos = fin_ripley_puntos - inicio_ripley_puntos

        print(f"El tiempo de carga de la pagina luego de presionar ripley puntos es de: {carga_ripley_puntos:.2f} segundos")

        #Almacenar resultados
        self.log_performance("Carga de ripley puntos", inicio_ripley_puntos, fin_carga_cont_ripley_puntos)
        self.log_performance("Carga de contenedor de ripley puntos", inicio_ripley_puntos, fin_canjeo_ripley_puntos)
        self.log_performance("Carga de la pagina luego de presionar ripley puntos Go", inicio_ripley_puntos, fin_ripley_puntos)


        time.sleep(2)




    @classmethod
    def tearDownClass(cls):
        cls.detener_ffmpeg()
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()

        
        