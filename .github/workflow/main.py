import time
import collections
import random
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.app import App
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.core.window import Window
from jnius import autoclass

# Importa las clases y funciones necesarias de pyjnius
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')

# Define plot axis limits and data deque
muestraD = 60
xmin = 0
xmax = muestraD
ymin = 32
ymax = 42
data = collections.deque([0] * muestraD, maxlen=muestraD)

# Create a Graph instance
graph = Graph(xlabel='Tiempo (s)', ylabel='Temperatura (°C)', x_ticks_minor=5,
              x_ticks_major=10, y_ticks_major=1, y_grid_label=True,
              x_grid_label=True, padding=5, x_grid=True, y_grid=True,
              xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

plot = MeshLinePlot(color=[0, 0, 1, 1])  # Blue color
plot.points = [(i, j) for i, j in enumerate(data)]
graph.add_plot(plot)

# Define the Kivy layout
KV = '''
<MainLayout>:
    orientation: 'vertical'
    label_text: ""

    BoxLayout:
        size_hint_y: None
        height: dp(50)
        Button:
            text: 'Conectar'
            on_press: root.connect_bluetooth()
        Button:
            text: 'Desconectar'
            on_press: root.disconnect_bluetooth()

    BoxLayout:
        size_hint_y: None
        height: dp(50)
        Label:
            text: "DISEÑO DE PROTOTIPO DE BAJO COSTO, PARA CONTROL Y MONITOREO DE TEMPERATURA DE NEONATOS"
            font_size: '16sp'

    BoxLayout:
        size_hint_y: None
        height: dp(50)
        Label:
            text: root.label_text
        Button:
            text: 'Iniciar'
            on_release: root.iniciar()
        Button:
            text: 'Reiniciar'
            on_release: root.reiniciar()
        Button:
            text: 'Salir'
            on_release: root.salir()
'''

Builder.load_string(KV)


class MainLayout(BoxLayout):
    label_text = StringProperty()

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.add_widget(graph)

        #self.is_run = Event()
        #self.thread = Thread(target=self.datos_a)
        #self.is_started = False
        #self.sock = None  # Agrega esta línea para definir el atributo 'sock'

        self.anim = Clock.schedule_interval(self.plot_data, 0.1)

    def connect_bluetooth(self):
        devices = self.discover_devices()
        # Muestra los dispositivos disponibles para su conexión
        for device in devices:
            print(device)

        # Conectar al dispositivo Bluetooth seleccionado
        server_mac_address = '30:6A:85:39:5B:51'  # Reemplazar por la dirección MAC del dispositivo seleccionado
        uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
        self.bt_adapter = BluetoothAdapter.getDefaultAdapter()
        device = self.bt_adapter.getRemoteDevice(server_mac_address)
        #self.sock = device.createInsecureRfcommSocketToServiceRecord(uuid)
        self.sock = device.createRfcommSocketToServiceRecord(uuid)
        self.sock.connect()

    def disconnect_bluetooth(self):
        # Desconectar del dispositivo Bluetooth
        self.sock.close()
    
    def discover_devices(self):
        # Descubre dispositivos Bluetooth cercanos
        self.bt_adapter = BluetoothAdapter.getDefaultAdapter()
        paired_devices = self.bt_adapter.getBondedDevices().toArray()
        nearby_devices = [(device.getAddress(), device.getName()) for device in paired_devices]
        return nearby_devices
    
    def iniciar(self):
        if not self.is_started:
            self.is_started = True
            Clock.schedule_interval(self.datos_a, 0.1)  # Ajusta el intervalo según sea necesario


    def datos_a(self, dt):
        while self.is_run.is_set():
            try:
                # Recibe datos de temperatura por Bluetooth
                temp_data = self.sock.recv(1024)
                # Convierte los datos a un valor de temperatura
                datos = float(temp_data)
                # Actualiza los datos de temperatura
                self.update_data(datos)
            except Exception as e:
                print("Error al leer datos del socket Bluetooth:", e)

    def update_data(self, value):
        data.append(value)

    def plot_data(self, dt):
        plot.points = [(i, j) for i, j in enumerate(data)]
        self.label_text = "TEMP: " + str(data[-1])

    def reiniciar(self):
        global data
        data = collections.deque([0] * muestraD, maxlen=muestraD)

    def salir(self):
        self.is_run.clear()
        self.anim.cancel()
        App.get_running_app().stop()


class MyApp(App):
    def build(self):
        return MainLayout()

    def on_start(self):
        self.title = "Gráfico de temperatura"
        Window.top = 200
        Window.left = 600


if __name__ == "__main__":
    MyApp().run()
