from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider

import random

class MainMenu(BoxLayout):
    def __init__(self, start_game_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20
        self.size_hint = (0.6, 0.6)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # เพิ่มชื่อเกม
        title = Label(
            text='Fish Game',
            font_size=60,
            size_hint_y=None,
            height=200
        )
        self.add_widget(title)
        
        # ปุ่มเริ่มเกม
        start_button = Button(
            text='Start Game',
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={'center_x': 0.5}
        )
        start_button.bind(on_press=start_game_callback)
        self.add_widget(start_button)

        # เพิ่มปุ่ม Settings
        settings_button = Button(
            text='Settings',
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={'center_x': 0.5}
        )
        settings_button.bind(on_press=self.show_settings)
        self.add_widget(settings_button)

    def show_settings(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label สำหรับแสดงข้อความ Volume
        content.add_widget(Label(text='Volume', font_size=20))
        
        # Slider สำหรับปรับเสียง
        slider = Slider(
            min=0,
            max=1,
            value=game.background_music.volume if game.background_music else 0.5,
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5}
        )
        slider.bind(value=self.on_volume_change)
        content.add_widget(slider)
        
        # ปุ่ม Close
        close_button = Button(
            text='Close',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5}
        )
        
        # สร้าง popup
        settings_popup = Popup(
            title='Settings',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True
        )
        
        # ผูกปุ่ม Close กับการปิด popup
        close_button.bind(on_press=settings_popup.dismiss)
        content.add_widget(close_button)
        
        settings_popup.open()

    def on_volume_change(self, instance, value):
        # ปรับเสียงของเพลงพื้นหลัง
        if game.background_music:
            game.background_music.volume = value

class GameWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.pressed_keys = set()
        self._score_label = CoreLabel(text="Score: ", font_size=20)
        self._lives_label = CoreLabel(text="Lives: 3", font_size=20)
        self._score_label.refresh()
        self._lives_label.refresh()
        self._score = 10
        self._lives = 3
        self._game_over_popup = None

        self.register_event_type("on_frame")
        self.register_event_type("on_score")

        with self.canvas:
            self._background = Rectangle(
                source="background_purple.png",
                pos=(0, 0),
                size=(Window.width, Window.height)
            )
            self._score_instruction = Rectangle(
                texture=self._score_label.texture,
                pos=(0, Window.height - 50),
                size=self._score_label.texture.size
            )
            self._lives_instruction = Rectangle(
                texture=self._lives_label.texture,
                pos=(200, Window.height - 50),
                size=self._lives_label.texture.size
            )

        Window.bind(on_resize=self._on_window_resize)

        self.keysPressed = set()
        self._entities = set()

        Clock.schedule_interval(self._on_frame,0)

        self.player = None  # เพิ่มตัวแปร player
        self.game_started = False
        
        # ย้าย background music ไปเล่นใน start_game แทน
        self.background_music = SoundLoader.load("Push.mp3")
        if self.background_music:
            self.background_music.volume = 0.5  # ตั้งค่าเริ่มต้นที่ 50%
        
        # ไม่ต้อง schedule spawn_enemies ตั้งแต่แรก
        # Clock.schedule_interval(self.spawn_enemies, 2)

    def _on_window_resize(self, instance, width, height):
        self._background.size = (width, height)
        self._score_instruction.pos = (0, height - 50)
        self._lives_instruction.pos = (200, height - 50)

    def spawn_enemies(self, dt):
        for i in range(5):
            random_y = random.randint(50, Window.height - 50)
            x = Window.width
            random_speed = random.randint(100, 300)
            self.add_entity(Enemy((x, random_y), random_speed))

    def _on_frame(self,dt):
        self.dispatch("on_frame",dt)

    def on_frame(self,dt):
        pass

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)
    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size
        self.dispatch("on_score", value)

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                result.add(e)
        return result

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        print('down', text)
        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        print('up', text)
        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            return True
        else:
            return False

    def move_step(self, dt):
        cur_x = self.pos[0]
        cur_y = self.pos[1]
        step = 200 * dt
        if 'w' in self.pressed_keys:
            cur_y += step
        if 's' in self.pressed_keys:
            cur_y -= step
        if 'a' in self.pressed_keys:
            cur_x -= step
        if 'd' in self.pressed_keys:
            cur_x += step
        self.pos = (cur_x, cur_y)

    @property
    def lives(self):
        return self._lives
        
    @lives.setter
    def lives(self, value):
        self._lives = value
        self._lives_label.text = "Lives: " + str(value)
        self._lives_label.refresh()
        self._lives_instruction.texture = self._lives_label.texture
        self._lives_instruction.size = self._lives_label.texture.size
        if value <= 0:
            self.show_game_over()
    
    def show_game_over(self):
        Clock.unschedule(self.spawn_enemies)
        
        if self.background_music:
            self.background_music.stop()
            
        for entity in self._entities:
            if hasattr(entity, 'stop_callbacks'):
                entity.stop_callbacks()
        
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # แสดงข้อความ Game Over และ Score
        content.add_widget(Label(text='Game Over!', font_size=30))
        content.add_widget(Label(text=f"Your Score: {self.score}", font_size=20))
        
        # สร้าง BoxLayout สำหรับปุ่ม
        button_layout = BoxLayout(
            orientation='horizontal', 
            spacing=20,
            size_hint_y=None,
            height=50,
            pos_hint={'center_x': 0.5}
        )
        
        # ปุ่ม Play Again
        restart_button = Button(
            text='Play Again',
            size_hint=(None, None),
            size=(150, 50)
        )
        restart_button.bind(on_press=self.restart_game)
        
        # ปุ่ม Exit
        exit_button = Button(
            text='Exit',
            size_hint=(None, None),
            size=(150, 50)
        )
        exit_button.bind(on_press=self.exit_game)
        
        # เพิ่มปุ่มทั้งสองเข้าไปใน button_layout
        button_layout.add_widget(restart_button)
        button_layout.add_widget(exit_button)
        
        # เพิ่ม button_layout เข้าไปใน content
        content.add_widget(button_layout)
        
        self._game_over_popup = Popup(
            title='Game Over',
            content=content,
            size_hint=(None, None),
            size=(400, 300),
            auto_dismiss=False
        )
        self._game_over_popup.open()
    
    def restart_game(self, instance):
        self._lives = 3
        self.score = 10
        self.pressed_keys = set()
        
        self._lives_label.text = "Lives: 3"
        self._lives_label.refresh()
        self._lives_instruction.texture = self._lives_label.texture
        self._lives_instruction.size = self._lives_label.texture.size
        
        if self.background_music:
            self.background_music.play()
        
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        
        # ลบ entities ทั้งหมด
        entities_to_remove = list(self._entities)
        for entity in entities_to_remove:
            self.remove_entity(entity)
        
        # สร้าง player ใหม่
        self.player = Player()
        self.player.pos = (Window.width / 2 - self.player.size[0] / 2,
                          Window.height / 2 - self.player.size[1] / 2)
        self.add_entity(self.player)
        
        Clock.schedule_interval(self.spawn_enemies, 2)
        
        if self._game_over_popup:
            self._game_over_popup.dismiss()

    def exit_game(self, instance):
        App.get_running_app().stop()  # ปิดแอพ

    def on_score(self, value):
        pass

    def start_game(self, instance):
        # ซ่อนเมนูหลัก
        self.menu.parent.remove_widget(self.menu)
        
        # เริ่มเกม
        self.game_started = True
        self.background_music.play()
        Clock.schedule_interval(self.spawn_enemies, 2)
        
        # เพิ่ม player
        self.player = Player()
        self.player.pos = (Window.width / 2 - self.player.size[0] / 2,
                          Window.height / 2 - self.player.size[1] / 2)
        self.add_entity(self.player)

class Entity(object):
    def __init__(self):
        self._pos = (0, 0)
        self._size = (50, 50)
        self._source = "bullshit.png"
        self._instruction = Rectangle(
            pos=self._pos, size=self._size, source=self._source)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source

class Enemy(Entity):
    def __init__(self, pos, speed=100):
        super().__init__()
        self._speed = speed
        self.pos = pos
        
        self.enemy_types = [
            {"source": "enemy1.png", "size": (281, 94), "score": 8},
            {"source": "enemy2.png", "size": (282, 200), "score": 8},
            {"source": "enemy3.png", "size": (63, 45), "score": 8},
            {"source": "enemy4.png", "size": (80, 37), "score": 8},
            {"source": "enemy5.png", "size": (73, 60), "score": 8},
            {"source": "enemy6.png", "size": (602, 268), "score": 8},
            {"source": "enemy7.png", "size": (90, 45), "score": 8},
            {"source": "enemy8.png", "size": (100, 54), "score": 8},
            {"source": "enemy9.png", "size": (135, 100), "score": 1999}
        ]
        
        enemy_type = random.choice(self.enemy_types)
        self.source = enemy_type["source"]
        self.size = enemy_type["size"]
        self.required_score = enemy_type["score"]
        
        
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        if self.pos[0] < 0:
            self.stop_callbacks()
            game.remove_entity(self)
            return
            
        for e in game.colliding_entities(self):
            if e == game.player and game.player is not None:
                game.add_entity(Explosion(self.pos, self.size))
                self.stop_callbacks()
                game.remove_entity(self)
                
                if game.score >= self.required_score:
                    game.score += self.required_score
                else:
                    game.lives -= 1
                return

        step_size = self._speed * dt
        new_x = self.pos[0] - step_size
        self.pos = (new_x, self.pos[1])
        
        game.bind(on_frame=self.move_step)

class Explosion(Entity):
    def __init__(self, pos, entity_size=(50, 50)):
        super().__init__()
        center_x = pos[0] + entity_size[0] / 2
        center_y = pos[1] + entity_size[1] / 2
        
        explosion_size = (entity_size[0] * 0.5, entity_size[1] * 0.5)
        self.size = explosion_size
        
        explosion_x = center_x - explosion_size[0] / 2
        explosion_y = center_y - explosion_size[1] / 2
        self.pos = (explosion_x, explosion_y)
        
        self.source = "explosion.png"
        sound = SoundLoader.load("eatsound.mp3")
        if sound:
            sound.volume = game.background_music.volume if game.background_music else 0.5
            sound.play()
        Clock.schedule_once(self._remove_me, 0.1)

    def _remove_me(self, dt):
        game.remove_entity(self)

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.source = "playerfish.png"
        self.fish_right = "playerfish.png"
        self.fish_left = "playerfish_left.png"
        self.base_size = (50, 50)  # ขนาดเริ่มต้น
        self.size = self.base_size  # กำหนดขนาดเริ่มต้น
        game.bind(on_frame=self.move_step)
        game.bind(on_score=self.update_size)  # ผูก event เมื่อ score เปลี่ยน

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)
        game.unbind(on_score=self.update_size)

    def update_size(self, instance, value):
        # คำนวณขนาดใหม่ตาม score
        scale = 1 + (value / 100)  # เพิ่มขนาด 1% ต่อทุกๆ score 1 point
        new_width = self.base_size[0] * scale
        new_height = self.base_size[1] * scale
        self.size = (new_width, new_height)

    def move_step(self, sender, dt):
        cur_x = self.pos[0]
        cur_y = self.pos[1]
        step = 200 * dt

        # เก็บตำแหน่งเดิมไว้ก่อน
        new_x = cur_x
        new_y = cur_y

        if 'w' in game.pressed_keys:
            new_y += step
        if 's' in game.pressed_keys:
            new_y -= step
        if 'a' in game.pressed_keys:
            new_x -= step
            self.source = self.fish_left
        if 'd' in game.pressed_keys:
            new_x += step
            self.source = self.fish_right

        # ตรวจสอบขอบเขต window
        # ขอบซ้าย
        if new_x < 0:
            new_x = 0
        # ขอบขวา
        if new_x > Window.width - self.size[0]:
            new_x = Window.width - self.size[0]
        # ขอบล่าง
        if new_y < 0:
            new_y = 0
        # ขอบบน
        if new_y > Window.height - self.size[1]:
            new_y = Window.height - self.size[1]

        self.pos = (new_x, new_y)

done = False
game = GameWidget()
game.player = Player()
game.player.pos = (Window.width / 2 - game.player.size[0] / 2,
                  Window.height / 2 - game.player.size[1] / 2)
game.add_entity(game.player)

class MyApp(App):
    def build(self):
        root = FloatLayout()
        
        global game
        game = GameWidget()
        game.size_hint = (1, 1)
        
        menu = MainMenu(game.start_game)
        game.menu = menu
        
        root.add_widget(game)
        root.add_widget(menu)
        
        return root

if __name__ == '__main__':
    app = MyApp()
    app.run()