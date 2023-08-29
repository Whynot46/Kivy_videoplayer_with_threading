import cv2
import threading
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen


Window.maximize()
Builder.load_file('./kivy_videoplayer.kv')


class MainScreen(Screen):
    pass


class Main(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.urlRtsp = "URL_OR_LOCAL_PATH"
        self.frame_cap = None
        self.processed_frame = None
        self.capture = cv2.VideoCapture(self.urlRtsp)
        self.event = None
        self.st_art = False

    def build(self):
        sm = ScreenManager()
        self.main_screen = MainScreen()
        sm.add_widget(self.main_screen)
        return sm

    def start(self):
        if not self.st_art:
            self.st_art = True
            self.event = Clock.schedule_interval(self.update_frame, 1.0 / 30)
            self.th_read_frame = threading.Thread(target=self.read_capture, daemon=True)
            self.th_read_frame.start()
            self.main_screen.ids.start_button.disabled = True

    def stop(self):
        self.st_art = False
        try:
            self.th_read_frame.join()
            self.event.cancel()
            self.main_screen.ids.start_button.disabled = False
        except:
            pass

    def save_frame(self):
        date = datetime.now()
        str_date = date.strftime("%Y_%m_%d_%H_%M_%S")
        try:
            cv2.imwrite(f'/Frame_{str_date}.png', self.processed_frame)
            successfull_popup = Popup(title='Saving frame', content=Label(text='Save succesful'), size_hint=(None, None), size=(200, 100), auto_dismiss=True)
            successfull_popup.open()
        except: 
            error_popup = Popup(title='Saving frame', content=Label(text='Error while saving'), size_hint=(None, None), size=(200, 100), auto_dismiss=True)
            error_popup.open()

    def read_capture(self):
        i_errors_read = 0
        while self.st_art:
            try:
                self.ret, self.frame_cap = self.capture.read()
                if self.ret == False:
                    i_errors_read += 1
                    if i_errors_read >= 10:
                        self.capture = cv2.VideoCapture(self.urlRtsp)
                else:
                    i_errors_read = 0
            except:
                self.capture = cv2.VideoCapture(self.urlRtsp)

    def mute_switch(self):
        if self.mute_sound == False:
            self.main_screen.ids.sound_button.text = 'Sound on'
            self.main_screen.ids.sound_button.state = 'down'
            self.mute_sound = True
        else:
            self.main_screen.ids.sound_button.text = 'Sound off'
            self.main_screen.ids.sound_button.state = 'normal'
            self.mute_sound = False

    def frame_processing(self, frame):
        return frame

    def video_processing(self, frame):
        self.processed_frame = self.frame_processing(frame)

    def update_frame(self, dt):
        frame = self.frame_cap.copy()
        self.video_processing(frame)
        if self.ret:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.main_screen.ids.vid1.texture = texture


if __name__ == '__main__':
    Main().run()
