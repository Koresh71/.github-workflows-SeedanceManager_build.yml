# --- РАЗДЕЛ 1: ИМПОРТЫ И ПЛАТФОРМОЗАВИСИМЫЕ НАСТРОЙКИ --- # # 1
import tkinter as tk # 2
from tkinter import ttk, messagebox, scrolledtext, simpledialog # 3
import json, os, sys, hashlib, uuid, webbrowser, base64, glob, re, shutil, math, platform, time # 4
import threading, urllib.request, urllib.parse, subprocess # 5

# УМНАЯ ДИАГНОСТИКА ВИДЕО (OPENCV + PYGAME-CE ДЛЯ ЗВУКА) # 6
try: # 7
    import cv2 # 8
    from PIL import Image, ImageTk # 9
    import pygame # 10
    HAS_VIDEO = True # 11
    VIDEO_ERROR = "" # 12
except ImportError as e: # 13
    HAS_VIDEO = False # 14
    VIDEO_ERROR = str(e) # 15

# Кроссплатформенный импорт библиотек Windows # 16
if sys.platform == "win32": # 17
    if IS_WINDOWS: import ctypes # 18
    if IS_WINDOWS: import winreg # 19
    try: # 20
        from ctypes import windll # 21
        windll.shcore.SetProcessDpiAwareness(1) # 22
        myappid = 'ikdesigns.seedancemanager.1' # 23
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) # 24
    except: pass # 25

# --- РАЗДЕЛ 2: СИСТЕМНЫЕ ФУНКЦИИ --- # # 26
def resource_path(relative_path): # 27
    try: # 28
        base_path = sys._MEIPASS # 29
    except Exception: # 30
        base_path = os.path.abspath(".") # 31
    return os.path.join(base_path, relative_path) # 32

def get_base_dir(): # 33
    if getattr(sys, 'frozen', False): # 34
        return os.path.dirname(sys.executable) # 35
    return os.path.dirname(os.path.abspath(__file__)) # 36

# --- РАЗДЕЛ 3: ТЕХНИЧЕСКИЕ ДАННЫЕ И ЦВЕТОВАЯ СХЕМА --- # # 37
# Зашифрованная соль SEED-KEY-SECURE-88 # 38
ENCODED_SALT = "U0VFRC1LRVktU0VDVVJFLTg4" # 39
SECRET_SALT = base64.b64decode(ENCODED_SALT).decode('utf-8') # 40

# Настройки сервера IK Designs # 41
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxCoqjx-fV5a_dLUwTqyK_Jvt8wN9YxznUNZw1gUxGQhvZwOiNnQp6WAgvCS6YYXVN-/exec" # 42
PRODUCT_ID = "SEEDANCE" # 43
LICENSE_FILE_NAME = "seedance_license.ikd" # 44

# ПАЛИТРА "ГЛУБОКИЙ ОКЕАН" (Deep Ocean) - Доработанная версия # 45
BG_MAIN = "#030914"      # Темно-синий, уходящий в черноту # 46
BG_PANEL = "#0a1326"     # Глубокий синий для панелей # 47
BG_SIDEBAR = "#060d1c"   # Глубокий синий для бокового меню # 48
ACCENT_GREEN = "#10b981" # Базовый зеленый # 49
ACCENT_CYAN = "#8b5cf6"  # Насыщенный фиолетовый # 50
ACCENT_GOLD = "#38bdf8"  # Светло-голубой (выделение и активные вкладки) # 51
ACCENT_BLUE = "#00a2ff"  # Яркий светящийся синий (главный заголовок программы) # 52
TEXT_WHITE = "#f8fafc" # 53
TEXT_MUTED = "#64748b" # 54
BORDER_GLOW = "#1e293b" # 55
DANGER = "#f43f5e"       # Глубокий розово-красный (удаление) # 56
SUCCESS = "#059669"      # Изумрудный (сохранение) # 57

# --- РАЗДЕЛ 4: КАСТОМНЫЕ ВИДЖЕТЫ --- # # 58

class IKDVideoPlayer(tk.Canvas): # 59
    def __init__(self, master, video_path, on_finish): # 60
        super().__init__(master, bg="#000000", highlightthickness=0) # 61
        self.video_path = video_path # 62
        self.audio_path = video_path.replace('.mp4', '.mp3') # 63
        self.on_finish = on_finish # 64
        self.playing = False # 65
        self.cap = None # 66
        self.photo = None # 67
        self._canvas_w = 100 # 68
        self._canvas_h = 100 # 69
        self.has_audio = False # 70
        
        if os.path.exists(self.audio_path): # 71
            try: # 72
                import pygame # 73
                pygame.mixer.init() # 74
                pygame.mixer.music.load(self.audio_path) # 75
                self.has_audio = True # 76
            except: pass # 77

        self.bind("<Configure>", self._on_resize) # 78

    def play(self): # 79
        import cv2 # 80
        import time # 81
        self.cap = cv2.VideoCapture(self.video_path) # 82
        if not self.cap.isOpened(): # 83
            if self.on_finish: self.on_finish() # 84
            return # 85
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) # 86
        if self.fps <= 0: self.fps = 30 # 87
        self.playing = True # 88
        
        if self.has_audio: # 89
            try: # 90
                import pygame # 91
                pygame.mixer.music.play() # 92
            except: pass # 93
            
        self.start_time = time.time() # 94
        self.frame_count = 0 # 95
        self._update_frame() # 96

    def _on_resize(self, event): # 97
        self._canvas_w = event.width # 98
        self._canvas_h = event.height # 99

    def _update_frame(self): # 100
        if not self.playing: return # 101
        import cv2 # 102
        import time # 103
        from PIL import Image, ImageTk # 104
        
        elapsed = time.time() - self.start_time # 105
        expected_frame = int(elapsed * self.fps) # 106
        
        if self.frame_count > expected_frame: # 107
            delay = int(((self.frame_count / self.fps) - elapsed) * 1000) # 108
            self.after(max(1, delay), self._update_frame) # 109
            return # 110
            
        frames_to_advance = expected_frame - self.frame_count # 111
        ret = True # 112
        
        for _ in range(frames_to_advance - 1): # 113
            ret = self.cap.grab() # 114
            self.frame_count += 1 # 115
            if not ret: break # 116
            
        if ret: # 117
            ret, frame = self.cap.read() # 118
            self.frame_count += 1 # 119

        if not ret: # 120
            self.stop() # 121
            if self.on_finish: self.on_finish() # 122
            return # 123

        if self._canvas_w > 10 and self._canvas_h > 10: # 124
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # 125
            frame = cv2.resize(frame, (self._canvas_w, self._canvas_h), interpolation=cv2.INTER_LINEAR) # 126
            img = Image.fromarray(frame) # 127
            self.photo = ImageTk.PhotoImage(image=img) # 128
            self.delete("all") # 129
            self.create_image(0, 0, image=self.photo, anchor="nw") # 130

        self.after(1, self._update_frame) # 131

    def stop(self): # 132
        self.playing = False # 133
        if self.cap: # 134
            self.cap.release() # 135
        if self.has_audio: # 136
            try: # 137
                import pygame # 138
                pygame.mixer.music.stop() # 139
            except: pass # 140

class GlowButton(tk.Canvas): # 141
    def __init__(self, master, text, color, command=None, width=200, height=50, font_size=12, zoom=1.0, is_tab=False, **kwargs): # 142
        self.zoom = zoom # 143
        self.h = int(height * zoom) # 144
        self.req_w = int(width * zoom) # 145
        self.is_tab = is_tab # 146
        super().__init__(master, width=self.req_w, height=self.h+int(24*zoom), bg=master['bg'], highlightthickness=0, cursor="hand2", **kwargs) # 147
        self.command = command # 148
        self.color = color # 149
        self.text = text # 150
        self.font_size = int(font_size * zoom) # 151
        self.hover = False # 152
        self.current_width = self.req_w # 153
        self.is_active = False # 154
        self.pulse_val = 2 # 155
        self.pulse_dir = 1 # 156
        self.hover_step = 0 # 157
        self.hover_dir = 1 # 158
        self.tick = 0 # 159
        self.bind("<Button-1>", self._on_click) # 160
        self.bind("<Enter>", self._on_enter) # 161
        self.bind("<Leave>", self._on_leave) # 162
        self.bind("<Configure>", self._on_resize) # 163
        self._pulse_loop() # 164

    def set_active(self, state): # 165
        self.is_active = state # 166
        self.render() # 167

    def set_text(self, new_text): # 168
        self.text = new_text # 169
        self.render() # 170

    def _on_resize(self, event): # 171
        if event.width > 10: # 172
            self.current_width = event.width # 173
            self.render() # 174
            
    def _pulse_loop(self): # 175
        if not self.winfo_exists(): return # 176
        self.tick += 1 # 177
        needs_render = False # 178
        if self.is_active and not self.hover: # 179
            if self.tick % 12 == 0:  # 180
                self.pulse_val += self.pulse_dir # 181
                if self.pulse_val >= 8: self.pulse_dir = -1 # 182
                elif self.pulse_val <= 0: self.pulse_dir = 1 # 183
                needs_render = True # 184
        if self.hover: # 185
            self.hover_step += self.hover_dir # 186
            if self.hover_step >= 20: self.hover_dir = -1 # 187
            elif self.hover_step <= 0: self.hover_dir = 1 # 188
            needs_render = True # 189
        if needs_render: self.render() # 190
        self.after(40, self._pulse_loop) # 191

    def _mix_colors(self, c1, c2, ratio): # 192
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16) # 193
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16) # 194
        r = int(r1 * (1 - ratio) + r2 * ratio) # 195
        g = int(g1 * (1 - ratio) + g2 * ratio) # 196
        b = int(b1 * (1 - ratio) + b2 * ratio) # 197
        return f"#{r:02x}{g:02x}{b:02x}" # 198

    def render(self): # 199
        self.delete("all") # 200
        z = self.zoom # 201
        off = int(12 * z) # 202
        w = self.current_width - off*2 # 203
        if w < 10: w = 10 # 204
        is_hover = self.hover # 205
        is_active = self.is_active # 206
        render_color = self.color # 207
        if not is_active and is_hover: # 208
            render_color = ACCENT_CYAN if self.is_tab else self.color # 209
        intensity = 8 if is_hover else 3 # 210
        if intensity > 3: # 211
            for i in range(intensity, 0, -1): # 212
                self.draw_rounded_rect(off-i, off-i, w+off+i, self.h+off+i, radius=int(12*z), outline=render_color, width=1) # 213
        else: # 214
            self.draw_rounded_rect(off-3, off-3, w+off+3, self.h+off+3, radius=int(11*z), outline=render_color, width=1) # 215
        
        if is_hover: # 216
            ratio = 0.5 + (self.hover_step / 20.0) * 0.5  # 217
            fill_c = self._mix_colors(BG_PANEL, render_color, ratio) # 218
            text_c = BG_MAIN  # 219
        elif is_active: # 220
            ratio = 0.1 + (self.pulse_val / 8.0) * 0.3 # 221
            fill_c = self._mix_colors(BG_PANEL, render_color, ratio) # 222
            text_c = render_color # 223
        else: # 224
            fill_c = BG_PANEL if not self.is_tab else BG_SIDEBAR # 225
            text_c = TEXT_WHITE # 226

        self.draw_rounded_rect(off, off, w+off, self.h+off, radius=int(8*z), fill=fill_c, outline=render_color, width=2) # 227
        self.create_text(w/2 + off, self.h/2 + off, text=self.text, fill=text_c, font=("Segoe UI Bold", self.font_size)) # 228

    def draw_rounded_rect(self, x1, y1, x2, y2, radius=15, **kwargs): # 229
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1] # 230
        return self.create_polygon(points, **kwargs, smooth=True) # 231

    def _on_click(self, e): # 232
        if self.command: self.command() # 233
    def _on_enter(self, e): # 234
        self.hover = True; self.render() # 235
    def _on_leave(self, e): # 236
        self.hover = False; self.hover_step = 0; self.render() # 237

class FutureArtCanvas(tk.Canvas): # 238
    def __init__(self, master, zoom=1.0, **kwargs): # 239
        super().__init__(master, bg=BG_PANEL, highlightthickness=0, **kwargs) # 240
        self.zoom = zoom # 241
        self.bind("<Configure>", self._on_resize) # 242
        self.image_ref = None  # 243
        self.angle_offset = 0 # 244
        self._animate_art() # 245

    def _animate_art(self): # 246
        if not self.winfo_exists(): return # 247
        self.angle_offset += 0.015 # 248
        self.render() # 249
        self.after(40, self._animate_art) # 250

    def _on_resize(self, event): # 251
        self.render() # 252

    def render(self): # 253
        self.delete("all") # 254
        w, h = self.winfo_width(), self.winfo_height() # 255
        if w < 10 or h < 10: return # 256
        cx, cy, z = w / 2, h / 2, self.zoom # 257
        has_image, img_y_bottom = False, 0 # 258
        try: # 259
            img_path = resource_path("art.png") # 260
            if os.path.exists(img_path): # 261
                if not self.image_ref: # 262
                    img = tk.PhotoImage(file=img_path) # 263
                    if z <= 0.75: img = img.zoom(3).subsample(4) # 264
                    self.image_ref = img # 265
                self.create_image(cx, int(20 * z), image=self.image_ref, anchor="n") # 266
                has_image, img_y_bottom = True, int(20 * z) + self.image_ref.height() # 267
        except: pass # 268
            
        if has_image: # 269
            remaining_h = h - img_y_bottom # 270
            if remaining_h > int(100 * z): # 271
                cy = img_y_bottom + (remaining_h / 2) + int(10 * z) # 272
                scale_mod = 0.95  # 273
            else: # 274
                scale_mod = 0.75; cy = h - int(90 * z) # 275
        else: scale_mod = 1.1  # 276

        max_radius = int(120 * z * scale_mod) # 277
        if max_radius > (w / 2) - 10: scale_mod = scale_mod * ((w / 2 - 10) / max_radius) # 278

        r1, r2, r3 = int(120 * z * scale_mod), int(95 * z * scale_mod), int(65 * z * scale_mod) # 279
        self.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline=BORDER_GLOW, width=int(2*z), dash=(int(10*z), int(10*z))) # 280
        self.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, outline=ACCENT_CYAN, width=int(1*z)) # 281
        
        points = [] # 282
        for i in range(6): # 283
            angle = i * (math.pi / 3) + self.angle_offset # 284
            points.append(cx + math.cos(angle) * r3); points.append(cy + math.sin(angle) * r3) # 285
        
        for i in range(6, 0, -1): self.create_polygon(points, outline=ACCENT_GREEN, fill="", width=1) # 286
        self.create_polygon(points, outline=ACCENT_GREEN, fill=BG_MAIN, width=max(1, int(2*z))) # 287
        
        pulse = math.sin(self.angle_offset * 3) * 5 * z * scale_mod # 288
        r4 = int(15 * z * scale_mod) + pulse # 289
        self.create_oval(cx-r4, cy-r4, cx+r4, cy+r4, fill=ACCENT_BLUE, outline=ACCENT_BLUE) # 290
        
        for i in range(6): # 291
            angle = i * (math.pi / 3) + self.angle_offset # 292
            x1, y1 = cx + math.cos(angle) * r4, cy + math.sin(angle) * r4 # 293
            x2, y2 = cx + math.cos(angle) * r3, cy + math.sin(angle) * r3 # 294
            self.create_line(x1, y1, x2, y2, fill=ACCENT_BLUE, width=max(1, int(2*z))) # 295
            
        self.create_text(cx, cy+r1+int(35*z*scale_mod), text="SEEDANCE ENGINE :: ACTIVE", fill=ACCENT_CYAN, font=("Consolas", int(12*z*scale_mod), "bold")) # 296

class NeuralNetworkCanvas(tk.Canvas): # 297
    def __init__(self, master, zoom=1.0, **kwargs): # 298
        super().__init__(master, bg=BG_MAIN, highlightthickness=0, **kwargs) # 299
        self.zoom = zoom # 300
        self.nodes = [] # 301
        self.num_nodes = 60 # 302
        self.bind("<Configure>", self._on_resize) # 303
        self._animate() # 304

    def _mix_colors(self, c1, c2, ratio): # 305
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16) # 306
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16) # 307
        r = int(r1 * (1 - ratio) + r2 * ratio) # 308
        g = int(r1 * (1 - ratio) + r2 * ratio) # 309
        b = int(b1 * (1 - ratio) + b2 * ratio) # 310
        return f"#{r:02x}{g:02x}{b:02x}" # 311

    def _on_resize(self, event): # 312
        self.w = event.width # 313
        self.h = event.height # 314
        if not self.nodes and self.w > 10: # 315
            import random # 316
            for _ in range(self.num_nodes): # 317
                x = random.randint(0, self.w) # 318
                y = random.randint(0, self.h) # 319
                dx = (random.random() - 0.5) * 1.5 * self.zoom # 320
                dy = (random.random() - 0.5) * 1.5 * self.zoom # 321
                self.nodes.append([x, y, dx, dy]) # 322

    def _animate(self): # 323
        if not self.winfo_exists(): return # 324
        if hasattr(self, 'w') and self.nodes: # 325
            self.delete("all") # 326
            import math # 327
            for node in self.nodes: # 328
                node[0] += node[2] # 329
                node[1] += node[3] # 330
                if node[0] < 0 or node[0] > self.w: node[2] *= -1 # 331
                if node[1] < 0 or node[1] > self.h: node[3] *= -1 # 332

            max_dist = 120 * self.zoom # 333
            for i in range(len(self.nodes)): # 334
                x1, y1 = self.nodes[i][0], self.nodes[i][1] # 335
                for j in range(i + 1, len(self.nodes)): # 336
                    x2, y2 = self.nodes[j][0], self.nodes[j][1] # 337
                    dist = math.hypot(x2 - x1, y2 - y1) # 338
                    if dist < max_dist: # 339
                        ratio = 1.0 - (dist / max_dist) # 340
                        if ratio > 0.15: # 341
                            line_color = self._mix_colors(BG_MAIN, ACCENT_BLUE, ratio) # 342
                            self.create_line(x1, y1, x2, y2, fill=line_color, width=max(1, int(1.5 * self.zoom))) # 343

            r = max(2, int(2.5 * self.zoom)) # 344
            for node in self.nodes: # 345
                self.create_oval(node[0]-r, node[1]-r, node[0]+r, node[1]+r, fill=ACCENT_CYAN, outline=ACCENT_CYAN) # 346

        self.after(40, self._animate) # 347

# --- ФУНКЦИЯ ДЛЯ СКРЫТОГО СБОРА ТЕЛЕМЕТРИИ --- # # 348
def get_telemetry(): # 349
    """Собирает ОС, IP, Город и Имя пользователя""" # 350
    try: # 351
        os_info = f"{platform.system()} {platform.release()}" # 352
    except: # 353
        os_info = "Unknown" # 354
        
    try: # 355
        username = os.getlogin() # 356
    except: # 357
        username = "Unknown" # 358
        
    ip, loc = "Unknown", "Unknown" # 359
    try: # 360
        req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'}) # 361
        with urllib.request.urlopen(req, timeout=5) as r: # 362
            data = json.loads(r.read().decode('utf-8')) # 363
            ip = data.get('query', 'Unknown') # 364
            loc = f"{data.get('country', '')}, {data.get('city', '')}".strip(', ') # 365
    except: # 366
        pass # 367
    return os_info, ip, loc, username # 368

# --- РАЗДЕЛ 5: СТАТИЧЕСКИЕ ТЕКСТОВЫЕ ДАННЫЕ И ЛОКАЛИЗАЦИЯ --- # # 369
INFO_RU = """Seedance 2.0 работает по принципу «Покажи и расскажи». Чтобы промты из нашей базы сработали идеально, следуй этим правилам: # 370

Шаг 1. Загрузка исходников и магия тегов «@» В Seedance 2.0 ты можешь загружать картинки и видео в качестве референсов. Когда ты загружаешь файл, система присваивает ему тег (например, @Image1,@Video1). Вставляя наш промт, убедись, что номера тегов в тексте совпадают с загруженными тобой файлами. # 371
·        Например: Если в промте написано «Replace the main product with @Image1», убедись, что под @Image1 загружено фото твоего товара. # 372

Шаг 2. Разделяй и властвуй (Уточнение референсов) Seedance 2.0 гениален тем, что может брать разные элементы из разных файлов. Промты в нашей базе уже настроены на это, но помни логику: # 373
·        Нужно движение камеры? Пиши: Reference @Video1 for camera movement. # 374
·        Нужна внешность героя? Пиши: Use @Image1 for character appearance. # 375
·        Нужен голос имимика? Пиши: Reference @Video1 for lip-sync and audio. # 376

Шаг 3. Идеальная формула промта Даже при использовании исходников текстовое описание должно быть полным. Наши промты построены по формуле, которую требует разработчик (SJinn): 👉 [Субъект] + [Действие] + [Локация] + [Освещение] + [Камера] + [Стиль] + [Качество] + [Ограничения] # 377

Шаг 4. Заклинания качества (Ограничения) Seedance 2.0 иногда может искажать лица или фон, если ему не запретить это делать. Обрати внимание, что в конце каждого нашего промта стоит блок с техническими требованиями. Никогда не удаляй их! # 378
·        Примеры защитных фраз: 4K, ultra-high definition, cinematic quality, completely stable camera, no deformation, clear facial features, silky smooth footage. # 379

Шаг 5. Аудио и Голос В Seedance 2.0 аудио генерируется на основе видео-референса. Если в промте есть фраза Voice and timbre reference @Video1, нейросеть извлечет голос из твоего исходного видео, скопирует его тембр и заставит персонажа из @Image1 говорить так же, синхронизируя губы. # 380

Итог: Загружаешь свои фото/видео -> меняешь теги @ в нашем шаблоне под свои файлы -> нажимаешь "Generate" -> получаешь профессиональный кинокадр!""" # 381

INFO_EN = """Seedance 2.0 works on the "Show and Tell" principle. To make the prompts from our database work perfectly, follow these rules: # 382

Step 1. Uploading sources and the magic of "@" tags In Seedance 2.0 you can upload images and videos as references. When you upload a file, the system assigns a tag to it (for example, @Image1, @Video1). When inserting our prompt, make sure that the tag numbers in the text match the files you uploaded. # 383
· For example: If the prompt says "Replace the main product with @Image1", make sure that a photo of your product is uploaded under @Image1. # 384

Step 2. Divide and conquer (Refining references) Seedance 2.0 is brilliant because it can take different elements from different files. The prompts in our database are already configured for this, but remember the logic: # 385
· Need camera movement? Write: Reference @Video1 for camera movement. # 386
· Need the character's appearance? Write: Use @Image1 for character appearance. # 387
· Need voice and mimicry? Write: Reference @Video1 for lip-sync and audio. # 388

Step 3. The perfect prompt formula Even when using sources, the text description must be complete. Our prompts are built according to the formula required by the developer (SJinn): 👉 [Subject] + [Action] + [Location] + [Lighting] + [Camera] + [Style] + [Quality] + [Constraints] # 389

Step 4. Quality Spells (Constraints) Seedance 2.0 can sometimes distort faces or backgrounds unless it is forbidden to do so. Please note that at the end of each of our prompts there is a block with technical requirements. Never delete them! # 390
· Examples of protective phrases: 4K, ultra-high definition, cinematic quality, completely stable camera, no deformation, clear facial features, silky smooth footage. # 391

Step 5. Audio and Voice In Seedance 2.0, audio is generated based on a video reference. If the prompt contains the phrase Voice and timbre reference @Video1, the neural network will extract the voice from your source video, copy its timbre and make the character from @Image1 speak the same way, synchronizing the lips. # 392

Bottom line: You upload your photos/videos -> change the @ tags in our template to match your files -> press "Generate" -> get a professional movie frame!""" # 393

HELP_RU = """📝 ДОБРО ПОЖАЛОВАТЬ В SEEDANCE PROMPT MANAGER! # 394

Этот инструмент создан для удобного хранения, редактирования и быстрого использования ваших лучших текстовых запросов (промптов) для нейросети Seedance. # 395

🔍 ПОИСК И НАВИГАЦИЯ # 396
• Используйте выпадающий список в левом меню для фильтрации промптов по категориям. # 397
• Нажмите на название эффекта в списке, чтобы загрузить его в главное окно. # 398
• В левой панели отображаются только названия, чтобы вы могли быстро ориентироваться в базе. # 399

🚀 ИСПОЛЬЗОВАНИЕ БАЗЫ # 400
• В главном окне вы увидите подробное описание и сам промпт (на английском, оптимизированном для Seedance). # 401
• Нажмите светящуюся кнопку «КОПИРОВАТЬ ПРОМПТ» — текст автоматически скопируется в буфер обмена компьютера. # 402
• Перейдите в Seedance и вставьте текст (Ctrl+V) для генерации. # 403

⚙️ УПРАВЛЕНИЕ БАЗОЙ (АДМИНКА) # 404
• Перейдите во вкладку «Управление», чтобы добавить свои собственные наработки или отредактировать существующие. # 405
• Чтобы создать новую категорию, нажмите кнопку «+» рядом с выбором категорий. # 406
• Если вы хотите удалить ненужную категорию, выберите её и нажмите «-». Внимание: при этом удалятся и все промпты из этой категории! # 407
• Чтобы создать новый промпт, нажмите «ДОБАВИТЬ НОВЫЙ ПРОМПТ», заполните все поля и нажмите «СОХРАНИТЬ». # 408
• Для изменения существующего промпта просто выберите его в списке, внесите правки и сохраните. Программа умная: она предложит вам выбор — перезаписать старый или сохранить как новый. # 409

💾 ФАЙЛЫ И ДАННЫЕ # 410
• Программа автоматически сканирует свою папку на наличие файлов с расширением *.ikd (например, user_seedance_prompts.ikd). # 411
• Все ваши данные надежно зашифрованы и хранятся локально. Вы можете переносить этот файл на другие устройства для синхронизации вашей личной базы.""" # 412

HELP_EN = """📝 WELCOME TO SEEDANCE PROMPT MANAGER! # 413

This tool is designed to conveniently store, edit, and quickly use your best text queries (prompts) for the Seedance AI. # 414

🔍 SEARCH AND NAVIGATION # 415
• Use the drop-down list in the left menu to filter prompts by categories. # 416
• Click on the effect name in the list to load it into the main window. # 417
• The left panel displays only titles so you can quickly navigate the database. # 418

🚀 USING THE DATABASE # 419
• In the main window, you will see a detailed description and the prompt itself (in English, optimized for Seedance). # 420
• Click the glowing "COPY PROMPT" button — the text will automatically be copied to your computer's clipboard. # 421
• Go to Seedance and paste the text (Ctrl+V) to generate. # 422

⚙️ DATABASE MANAGEMENT (ADMIN) # 423
• Go to the "Management" tab to add your own developments or edit existing ones. # 424
• To create a new category, click the "+" button next to the category selection. # 425
• If you want to delete an unnecessary category, select it and click "-". Warning: this will also delete all prompts from this category! # 426
• To create a new prompt, click "ADD NEW PROMPT", fill in all the fields, and click "SAVE". # 427
• To change an existing prompt, simply select it in the list, make edits, and save. The program is smart: it will offer you a choice — overwrite the old one or save it as a new one. # 428

💾 FILES AND DATA # 429
• Программа автоматически сканирует свою папку на наличие файлов с расширением *.ikd (например, user_seedance_prompts.ikd). # 430
• All your data is securely encrypted and stored locally. You can transfer this file to other devices to synchronize your personal database.""" # 431

LANG_DATA = { # 432
    "RU": { # 433
        "title": "Seedance Prompt Manager", "tab_main": "💻 База Промптов",  # 434
        "tab_admin": "⚙ Управление",  # 435
        "tab_trans": "🌍 Переводчик",  # 436
        "tab_video": "🎬 Генерация",  # 437
        "tab_info": "📖 Информация", "tab_help": "📝 Инструкция",  # 438
        "nav": "🧭 НАВИГАЦИЯ", "all_cats": "Все категории", # 439
        "copy_btn": "🚀 КОПИРОВАТЬ ПРОМПТ", "save_btn": "💾 СОХРАНИТЬ", "del_btn": "🗑 УДАЛИТЬ", # 440
        "add_new": "➕ ДОБАВИТЬ НОВЫЙ ПРОМТ", "cat_label": "1. КАТЕГОРИЯ:", "name_label": "2. НАЗВАНИЕ ЭФФЕКТА:", # 441
        "desc_label": "3. ОПИСАНИЕ:", "prompt_label": "4. ПРОМПТ:", "main_cat_head": "Категория:", # 442
        "main_desc_head": "ОПИСАНИЕ:", "main_prompt_head": "ПРОМПТ:", "lang_btn": "Language: EN", "zoom_btn": "🔍 МАСШТАБ", # 443
        "about_btn": "ℹ О программе",  # 444
        "demo_btn": "📺 Демо-ролик", # 445
        "about_msg": "🧠 Seedance Prompt Manager\n\nВерсия: V 1.0\nЛицензия: АКТИВИРОВАНА ✅\nID: {hwid}\nРазработчик: IK Designs\n\nПрограмма предназначена для управления и быстрой генерации промптов для нейросети Seedance. Все права защищены.", # 446
        "confirm_del": "Подтверждение", "ask_del": "Вы уверены, что хотите удалить этот элемент?", # 447
        "copy_ok": "Промпт скопирован!", # 448
        "video_title": "ГЕНЕРАТОР ВИДЕО (SYNTX.AI)", # 449
        "video_desc": "Syntx.ai — это универсальная ИИ-платформа «всё-в-одно», которая объединяет в себе сразу несколько передовых нейросетей.\nОна позволяет не только генерировать крутые видеоролики и изображения по вашим промптам, но и работать с текстом, аудио, сценариями и музыкой в едином интерфейсе.\n\nНажмите на кнопку ниже, чтобы открыть платформу и применить ваши скопированные промпты на практике!", # 450
        "video_btn": "🌐 ОТКРЫТЬ SYNTX",  # 451
        "promo_btn": "🎁 ПРОМОКОД", # 452
        "promo_msg": "Промокод SYNTX-IKDESIGNS успешно скопирован в буфер обмена!\nИспользуйте его при регистрации на Syntx.ai для получения бонусов." # 453
    }, # 454
    "EN": { # 455
        "title": "Seedance Prompt Manager", "tab_main": "💻 Prompt Database",  # 456
        "tab_admin": "⚙ Manage", # 457
        "tab_trans": "🌍 Translator",  # 458
        "tab_video": "🎬 Generate",  # 459
        "tab_info": "📖 Information", "tab_help": "📝 Instruction",  # 460
        "nav": "🧭 NAVIGATION", "all_cats": "All Categories", # 461
        "copy_btn": "🚀 COPY PROMPT", "save_btn": "💾 SAVE CHANGES", "del_btn": "🗑 DELETE", # 462
        "add_new": "➕ ADD NEW PROMPT", "cat_label": "1. CATEGORY:", "name_label": "2. EFFECT NAME:", # 463
        "desc_label": "3. DESCRIPTION:", "prompt_label": "4. PROMPT:", "main_cat_head": "Category:", # 464
        "main_desc_head": "DESCRIPTION:", "main_prompt_head": "PROMPT:", "lang_btn": "Язык: RU", "zoom_btn": "🔍 ZOOM", # 465
        "about_btn": "ℹ About",  # 466
        "demo_btn": "📺 Demo video", # 467
        "about_msg": "🧠 Seedance Prompt Manager\n\nVersion: V 1.0\nLicense: ACTIVATED ✅\nID: {hwid}\nDeveloper: IK Designs\n\nThe program is designed for managing and quickly generating prompts for the Seedance AI. All rights reserved.", # 468
        "confirm_del": "Confirmation", "ask_del": "Are you sure you want to delete this item?", # 469
        "copy_ok": "Copied!", # 470
        "video_title": "VIDEO GENERATOR (SYNTX.AI)", # 471
        "video_desc": "Syntx.ai is a universal all-in-one AI platform that combines multiple cutting-edge neural networks.\nIt allows you not only to generate awesome videos and images from your prompts, but also to work with text, audio, scripts, and music in a single interface.\n\nClick the button below to open the platform and put your copied prompts into practice!", # 472
        "video_btn": "🌐 OPEN SYNTX", # 473
        "promo_btn": "🎁 PROMO CODE", # 474
        "promo_msg": "Promo code SYNTX-IKDESIGNS successfully copied to clipboard!\nUse it when registering on Syntx.ai to receive bonuses." # 475
    } # 476
} # 477

# --- РАЗДЕЛ 6: ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ --- # # 478
class SeedanceManager: # 479
    def __init__(self, root): # 480
        self.root = root # 481
        self.current_lang = "RU" # 482
        self.zoom_scale = 1.0 # 483
        self.root.configure(bg=BG_MAIN) # 484
        
        self.base_dir = get_base_dir() # 485
        self.lic_file = self.get_license_path() # 486
        self.user_data_file = os.path.join(self.base_dir, "user_seedance_prompts.ikd") # 487
        
        self.icon_main = resource_path("logo.ico") # 488
        self.icon_ikd = resource_path("ikd_logo.ico") # 489
        self.icon_mac = resource_path("logo.icns") # 490
        
        self.hwid = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:12].upper() # 491
        self.prompts, self.categories_data = [], {} # 492
        self.cur_adm_idx = None # 493
        self.style = ttk.Style() # 494
        
        self.set_window_icon() # 495
        self.center_window(1300, 850) # 496
        
        if sys.platform == "win32": # 497
            self.register_ikd_association() # 498

        if not self.check_license(): # 499
            self.show_language_selector() # 500
        else: # 501
            self.show_main_interface() # 502
            self.check_periodic_license() # 503

    def save_sync_data(self, pin): # 504
        try: # 505
            sync_file = self.lic_file.replace(LICENSE_FILE_NAME, "sync.ikd") # 506
            data = {"pin": pin, "time": time.time()} # 507
            with open(sync_file, "wb") as f: # 508
                f.write(base64.b64encode(self.xor_cipher(json.dumps(data).encode('utf-8')))) # 509
        except: pass # 510

    def check_periodic_license(self): # 511
        sync_file = self.lic_file.replace(LICENSE_FILE_NAME, "sync.ikd") # 512
        if not os.path.exists(sync_file): return # 513
        try: # 514
            with open(sync_file, "rb") as f: # 515
                data = json.loads(self.xor_cipher(base64.b64decode(f.read())).decode('utf-8')) # 516
            last_time = data.get("time", 0) # 517
            saved_pin = data.get("pin", "") # 518
            if time.time() - last_time > 1209600: # 519
                threading.Thread(target=self.bg_verify, args=(saved_pin,), daemon=True).start() # 520
        except: pass # 521

    def bg_verify(self, pin): # 522
        try: # 523
            params = urllib.parse.urlencode({'hwid': self.hwid, 'pin': pin, 'product': PRODUCT_ID}).encode() # 524
            req = urllib.request.Request(GOOGLE_SCRIPT_URL, data=params, method='POST') # 525
            with urllib.request.urlopen(req, timeout=10) as r: # 526
                res = json.loads(r.read().decode('utf-8')) # 527
                if res.get("success"): # 528
                    self.save_sync_data(pin)  # 529
                else: # 530
                    if os.path.exists(self.lic_file): os.remove(self.lic_file) # 531
                    sync_file = self.lic_file.replace(LICENSE_FILE_NAME, "sync.ikd") # 532
                    if os.path.exists(sync_file): os.remove(sync_file) # 533
                    os._exit(0)  # 534
        except: pass  # 535

    def get_license_path(self): # 536
        if getattr(sys, 'frozen', False): # 537
            appdata = os.environ.get('APPDATA') # 538
            path = os.path.join(appdata, "IK Designs", "Seedance Prompt Manager") # 539
            os.makedirs(path, exist_ok=True) # 540
            return os.path.join(path, LICENSE_FILE_NAME) # 541
        else: # 542
            return os.path.join(self.base_dir, LICENSE_FILE_NAME) # 543

    def set_window_icon(self): # 544
        try: # 545
            if sys.platform == "win32" and os.path.exists(self.icon_main): # 546
                if IS_WINDOWS: self.root.iconbitmap(resource_path("logo.ico")) # 547
            elif sys.platform == "darwin" and os.path.exists(self.icon_mac): # 548
                img = tk.Image("photo", file=self.icon_mac) # 549
                self.root.tk.call('wm', 'iconphoto', self.root._w, img) # 550
        except: pass # 551

    def register_ikd_association(self): # 552
        if sys.platform != "win32": return # 553
        try: # 554
            prog_id = "IKDesigns.IKDFile" # 555
            desired_name = "Файл данных IK Designs" # 556
            
            appdata_path = os.environ.get('APPDATA') # 557
            ikd_dir = os.path.join(appdata_path, "IK Designs") # 558
            os.makedirs(ikd_dir, exist_ok=True) # 559
            target_icon_path = os.path.join(ikd_dir, "ikd_file_icon.ico") # 560
            
            if not os.path.exists(target_icon_path) and os.path.exists(self.icon_ikd): # 561
                shutil.copy2(self.icon_ikd, target_icon_path) # 562

            try: # 563
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key: # 564
                    current_val, _ = winreg.QueryValueEx(key, "") # 565
                    if current_val == desired_name: return # 566
            except: pass # 567

            exe_path = f'"{sys.executable}"' # 568
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.ikd") as key: # 569
                winreg.SetValue(key, "", winreg.REG_SZ, prog_id) # 570
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key: # 571
                winreg.SetValue(key, "", winreg.REG_SZ, desired_name) # 572
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as key: # 573
                winreg.SetValue(key, "", winreg.REG_SZ, f'"{target_icon_path}"') # 574
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key: # 575
                winreg.SetValue(key, "", winreg.REG_SZ, f'{exe_path} "%1"') # 576
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None) # 577
        except: pass # 578

    def center_window(self, w, h): # 579
        width, height = int(w * self.zoom_scale), int(h * self.zoom_scale) # 580
        if not hasattr(self, 'window_centered'): # 581
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight() # 582
            x, y = (sw // 2) - (width // 2), (sh // 2) - (height // 2) # 583
            self.root.geometry(f"{width}x{height}+{x}+{y}") # 584
            self.window_centered = True # 585
        else: # 586
            self.root.geometry(f"{width}x{height}") # 587

    def apply_base_style(self): # 588
        s = self.zoom_scale # 589
        f_main = int(16 * s) # 590
        self.style.theme_use('default') # 591
        self.style.layout('TNotebook.Tab', []) # 592
        self.style.configure('TNotebook', background=BG_MAIN, borderwidth=0) # 593
        self.style.configure('TNotebook.Tab', padding=[20, 10], font=("Segoe UI Bold", 11)) # 594
        self.style.configure('TCombobox', font=('Segoe UI', f_main)) # 595

    def apply_zoom(self, scale): # 596
        self.zoom_scale = scale # 597
        try: current_tab = self.nb.index(self.nb.select()) # 598
        except: current_tab = 0 # 599
        self.show_main_interface(tab_index=current_tab) # 600

    def check_license(self): # 601
        if not os.path.exists(self.lic_file): return False # 602
        try: # 603
            with open(self.lic_file, "r") as f: # 604
                saved_key = f.read().strip() # 605
                hash_res = hashlib.sha256((self.hwid + SECRET_SALT).encode()).hexdigest().upper() # 606
                expected = f"{hash_res[0:6]}-{hash_res[6:12]}-{hash_res[12:18]}" # 607
                return saved_key == expected # 608
        except: return False # 609

    def xor_cipher(self, data): # 610
        key = SECRET_SALT # 611
        return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)]) # 612

    def encrypt_data(self, data): # 613
        return base64.b64encode(self.xor_cipher(json.dumps(data, ensure_ascii=False).encode('utf-8'))) # 614

    def decrypt_data(self, encrypted): # 615
        try: return json.loads(self.xor_cipher(base64.b64decode(encrypted)).decode('utf-8')) # 616
        except: return [] # 617

    def get_cat_display(self, cat_ru): # 618
        val = self.categories_data.get(cat_ru, cat_ru) # 619
        return self.get_loc_text(val) if self.current_lang == "EN" else self.get_loc_text(cat_ru) # 620

    def get_loc_text(self, text): # 621
        if not text or not isinstance(text, str): return "" # 622
        text = text.strip() # 623
        cleaned = re.sub(r'^\d+[\.\)\-]\s*', '', text) # 624
        if cleaned: text = cleaned # 625
        start_idx = text.rfind('(') # 626
        if start_idx != -1 and text.endswith(')'): # 627
            p1, p2 = text[:start_idx].strip(), text[start_idx+1:-1].strip() # 628
            if bool(re.search('[а-яА-ЯёЁ]', p2)) and not bool(re.search('[а-яА-ЯёЁ]', p1)): ru, en = p2, p1 # 629
            else: ru, en = p1, p2 # 630
            return en if self.current_lang == "EN" else ru # 631
        return text # 632

    def get_item_name(self, item): # 633
        if 'name' in item: # 634
            return self.get_loc_text(item['name']) # 635
        if self.current_lang == "EN": # 636
            return self.get_loc_text(item.get('name_en', item.get('name_ru', ''))) # 637
        return self.get_loc_text(item.get('name_ru', item.get('name_en', ''))) # 638

    def init_database(self): # 639
        for json_file in glob.glob(os.path.join(self.base_dir, "*.json")): # 640
            try: # 641
                with open(json_file, 'r', encoding='utf-8') as f: data = json.load(f) # 642
                counter = 1 # 643
                while os.path.exists(os.path.join(self.base_dir, f"{counter}_user_seedance_prompts.ikd")): counter += 1 # 644
                new_ikd_path = os.path.join(self.base_dir, f"{counter}_user_seedance_prompts.ikd") # 645
                with open(new_ikd_path, 'wb') as f: f.write(self.encrypt_data(data)) # 646
                os.remove(json_file) # 647
            except: pass # 648

        self.prompts, self.categories_data = [], {} # 649
        all_dat_files = [f for f in os.listdir(self.base_dir) if f.endswith(".ikd") and "seedance_prompts" in f.lower()] # 650
        for f_name in all_dat_files: # 651
            file_path = os.path.join(self.base_dir, f_name) # 652
            try: # 653
                with open(file_path, 'rb') as f: # 654
                    batch = self.decrypt_data(f.read()) # 655
                source_type = "user" if "user" in f_name else "system" # 656
                for item in batch: # 657
                    item["_source"] = source_type # 658
                    self.prompts.append(item) # 659
                    ru_cat = item.get("category", "Общее") # 660
                    self.categories_data[ru_cat] = item.get("category_en", ru_cat) # 661
            except: pass # 662
        if not self.categories_data: self.categories_data["Общее"] = "General" # 663

    def show_main_interface(self, tab_index=0): # 664
        s = self.zoom_scale # 665
        for w in self.root.winfo_children(): w.destroy() # 666
        self.init_database() # 667
        
        self.center_window(1300, 850) # 668
        self.apply_base_style() # 669
        l = LANG_DATA[self.current_lang] # 670
        self.root.title(l["title"]) # 671

        header = tk.Frame(self.root, bg=BG_MAIN, pady=int(10*s)); header.pack(fill="x") # 672
        
        # --- ГЛАВНЫЙ ЗАГОЛОВОК С ОБВОДКОЙ --- # 673
        cv_w_h = int(600 * s) # 674
        cv_h_h = int(70 * s) # 675
        title_cv_h = tk.Canvas(header, width=cv_w_h, height=cv_h_h, bg=BG_MAIN, highlightthickness=0) # 676
        title_cv_h.pack(side="left", padx=int(30*s)) # 677
        
        t_font_h = ("Segoe UI Black", int(26*s)) # 678
        t_text_h = "🌊 Seedance Prompt Manager" # 679
        # Исправлено: уменьшена толщина обводки для большей четкости текста # 680
        off_h = max(1, int(0.7 * s)) # 681
        
        # Рисуем белую обводку # 682
        for dx, dy in [(-off_h,-off_h), (-off_h,off_h), (off_h,-off_h), (off_h,off_h), (0,-off_h), (-off_h,0), (off_h,0), (0,off_h)]: # 683
            title_cv_h.create_text(off_h + dx, cv_h_h/2 + dy, text=t_text_h, font=t_font_h, fill="#ffffff", anchor="w") # 684
            
        # Рисуем основной синий текст # 685
        title_cv_h.create_text(off_h, cv_h_h/2, text=t_text_h, font=t_font_h, fill="#00a2ff", anchor="w") # 686
        
        # Кнопки в заголовке # 687
        self.btn_about = GlowButton(header, text=l["about_btn"], color=ACCENT_CYAN, command=lambda: messagebox.showinfo(l["about_btn"], l["about_msg"].format(hwid=self.hwid)), width=160, height=35, font_size=10, zoom=s) # 688
        self.btn_about.pack(side="right", padx=int(10*s)) # 689
        
        self.btn_lang = GlowButton(header, text=l["lang_btn"], color=ACCENT_GREEN, command=self.toggle_lang, width=160, height=35, font_size=10, zoom=s) # 690
        self.btn_lang.pack(side="right", padx=int(5*s)) # 691

        # НОВАЯ КНОПКА: ДЕМО-РОЛИК # 692
        self.btn_demo = GlowButton(header, text=l["demo_btn"], color=ACCENT_GOLD, command=lambda: webbrowser.open("https://youtu.be/JsS8JqLG6eY?si=Y09w_NNqFNToF8CX"), width=180, height=35, font_size=10, zoom=s) # 693
        self.btn_demo.pack(side="right", padx=int(5*s)) # 694
        
        zm = tk.Menubutton(header, text=l["zoom_btn"], bg=BG_PANEL, fg="white", font=("Segoe UI Bold", int(10*s)), relief="flat", padx=10) # 695
        zm.menu = tk.Menu(zm, tearoff=0, bg=BG_PANEL, fg="white", font=("Segoe UI", 12)) # 696
        zm["menu"] = zm.menu # 697
        for v in [1.0, 0.75, 0.5]: zm.menu.add_command(label=f"{int(v*100)}%", command=lambda val=v: self.apply_zoom(val)) # 698
        zm.pack(side="right", padx=int(5*s)) # 699

        nav_bar = tk.Frame(self.root, bg=BG_MAIN) # 700
        nav_bar.pack(fill="x", padx=int(25*s), pady=int(5*s)) # 701
        
        tabs_info = [(0, l["tab_main"]), (1, l["tab_admin"]), (2, l["tab_trans"]), (3, l["tab_video"]), (4, l["tab_info"]), (5, l["tab_help"])] # 702
        self.tab_buttons = [] # 703
        for idx, name in tabs_info: # 704
            is_active = (idx == tab_index) # 705
            btn_color = ACCENT_GOLD if is_active else BORDER_GLOW # 706
            btn = GlowButton(nav_bar, text=name, color=btn_color, command=lambda i=idx: self.switch_tab(i), width=190, height=45, font_size=12, zoom=s, is_tab=True) # 707
            btn.pack(side="left", padx=5) # 708
            btn.set_active(is_active) # 709
            self.tab_buttons.append(btn) # 710

        self.nb = ttk.Notebook(self.root) # 711
        self.nb.pack(fill="both", expand=True, padx=int(15*s), pady=int(10*s)) # 712
        t1, t2, t3, t4, t5, t6 = [tk.Frame(self.nb, bg=BG_MAIN) for _ in range(6)] # 713
        self.nb.add(t1, text="1"); self.nb.add(t2, text="2"); self.nb.add(t3, text="3") # 714
        self.nb.add(t4, text="4"); self.nb.add(t5, text="5"); self.nb.add(t6, text="6") # 715
        
        off_p = int(12*s) # 716

        # --- TAB 1: БАЗА ПРОМПТОВ --- # 717
        left = tk.Frame(t1, bg=BG_SIDEBAR, width=int(300*s)); left.pack(side="left", fill="y", pady=int(10*s)); left.pack_propagate(False) # 718
        tk.Label(left, text=l["nav"], font=("Segoe UI Bold", int(14*s)), bg=BG_PANEL, fg=TEXT_WHITE).pack(fill="x", pady=(0, int(10*s)), ipady=int(18*s)) # 719
        self.cat_var = tk.StringVar(value=l["all_cats"]) # 720
        # Исправлено: уменьшен шрифт и отступы, чтобы длинные названия категорий умещались в боковой рамке # 721
        self.main_cb = ttk.Combobox(left, textvariable=self.cat_var, state="readonly", font=("Segoe UI Bold", int(11*s)), justify="center") # 722
        self.main_cb.pack(fill="x", padx=int(3*s), pady=(0, int(10*s)), ipady=int(5*s)); self.main_cb.bind("<<ComboboxSelected>>", lambda e: self.update_list()) # 723
        self.main_cb['values'] = [l["all_cats"]] + sorted([self.get_cat_display(c) for c in self.categories_data.keys()]) # 724

        lb_f1 = tk.Frame(left, bg=BG_SIDEBAR); lb_f1.pack(fill="both", expand=True) # 725
        sb1 = tk.Scrollbar(lb_f1); sb1.pack(side="right", fill="y") # 726
        
        self.listbox = tk.Listbox(lb_f1, bg=BG_SIDEBAR, fg=TEXT_WHITE, bd=0, font=("Segoe UI Bold", int(15*s)), selectbackground=ACCENT_GOLD, selectforeground="#000000", highlightthickness=0, yscrollcommand=sb1.set) # 727
        self.listbox.pack(side="left", fill="both", expand=True) # 728
        sb1.config(command=self.listbox.yview); self.listbox.bind("<<ListboxSelect>>", self.on_select) # 729
        
        tk.Frame(t1, bg=BORDER_GLOW, width=int(2*s)).pack(side="left", fill="y", padx=int(10*s), pady=int(10*s)) # 730

        right = tk.Frame(t1, bg=BG_MAIN, padx=int(15*s)); right.pack(side="right", fill="both", expand=True, pady=int(10*s)) # 731
        
        self.btn_copy = GlowButton(right, text=l["copy_btn"], color=ACCENT_CYAN, command=self.copy_p, font_size=18, width=400, height=60, zoom=s)  # 732
        self.btn_copy.pack(side="bottom", fill="x", pady=(int(10*s), 0)) # 733
        
        header_f = tk.Frame(right, bg=BG_MAIN) # 734
        header_f.pack(fill="x", padx=off_p, pady=(0, int(10*s))) # 735
        
        text_f = tk.Frame(header_f, bg=BG_MAIN) # 736
        text_f.pack(side="left", fill="both", expand=True, anchor="n") # 737
        
        self.lbl_p_n = tk.Label(text_f, text="", font=("Segoe UI Black", int(28*s)), bg=BG_MAIN, fg=ACCENT_GOLD, anchor="nw", wraplength=int(650*s)) # 738
        self.lbl_p_n.pack(fill="x", pady=(0, int(5*s))) # 739
        
        self.lbl_main_cat = tk.Label(text_f, text="", font=("Segoe UI Bold", int(12*s)), bg=BG_MAIN, fg="#00d1ff", anchor="w") # 740
        self.lbl_main_cat.pack(fill="x") # 741
        
        self.lbl_logo = tk.Label(header_f, bg=BG_MAIN) # 742
        self.lbl_logo.pack(side="right", anchor="n", padx=(int(10*s), 0), pady=(int(8*s), 0)) # 743
        
        try: # 744
            logo_path = resource_path("logo.png") # 745
            if os.path.exists(logo_path): # 746
                img = tk.PhotoImage(file=logo_path) # 747
                if s <= 0.75: # 748
                    img = img.zoom(3).subsample(4) # 749
                self.main_logo_img = img # 750
                self.lbl_logo.config(image=self.main_logo_img) # 751
        except: pass # 752
        
        tk.Label(right, text=l["main_desc_head"], font=("Segoe UI Bold", int(10*s)), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", padx=off_p) # 753
        self.txt_desc_main = tk.Text(right, bg=BG_PANEL, fg=TEXT_WHITE, font=("Segoe UI", int(14*s)), bd=0, wrap="word", height=4, state="disabled", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 754
        self.txt_desc_main.pack(fill="x", padx=off_p, pady=(int(5*s), int(15*s))) # 755
        
        tk.Label(right, text=l["main_prompt_head"], font=("Segoe UI Bold", int(10*s)), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", padx=off_p) # 756
        self.txt_p_main = scrolledtext.ScrolledText(right, bg="#000000", fg=TEXT_WHITE, font=("Consolas", int(15*s)), bd=0, padx=int(15*s), pady=int(15*s), state="disabled", highlightthickness=2, highlightbackground=ACCENT_CYAN, highlightcolor=ACCENT_CYAN, height=18) # 757
        self.txt_p_main.pack(fill="both", expand=True, padx=off_p) # 758

        # --- TAB 2: УПРАВЛЕНИЕ (Админка) --- # 759
        f2 = tk.Frame(t2, bg=BG_MAIN, padx=20, pady=10); f2.pack(fill="both", expand=True) # 760
        la = tk.Frame(f2, bg=BG_SIDEBAR, width=int(300*s)); la.pack(side="left", fill="y"); la.pack_propagate(False) # 761
        self.afv = tk.StringVar(value=l["all_cats"]) # 762
        # Исправлено: уменьшен шрифт и отступы, чтобы длинные названия категорий умещались в боковой рамке # 763
        self.afc = ttk.Combobox(la, textvariable=self.afv, state="readonly", font=("Segoe UI Bold", int(11*s)), justify="center") # 764
        self.afc.pack(fill="x", padx=int(3*s), pady=int(15*s), ipady=int(5*s)); self.afc.bind("<<ComboboxSelected>>", lambda e: self.update_admin_list()) # 765
        self.afc['values'] = self.main_cb['values'] # 766

        lb_f2 = tk.Frame(la, bg=BG_SIDEBAR); lb_f2.pack(fill="both", expand=True) # 767
        sb2 = tk.Scrollbar(lb_f2); sb2.pack(side="right", fill="y") # 768
        self.alb = tk.Listbox(lb_f2, bg=BG_SIDEBAR, fg="white", bd=0, font=("Segoe UI Bold", int(15*s)), selectbackground=ACCENT_GOLD, selectforeground="#000000", highlightthickness=0, yscrollcommand=sb2.set) # 769
        self.alb.pack(side="left", fill="both", expand=True) # 770
        sb2.config(command=self.alb.yview); self.alb.bind("<<ListboxSelect>>", self.on_admin_select) # 771
        
        tk.Frame(f2, bg=BORDER_GLOW, width=int(2*s)).pack(side="left", fill="y", padx=int(10*s)) # 772

        ra = tk.Frame(f2, bg=BG_MAIN, padx=int(10*s)); ra.pack(side="right", fill="both", expand=True) # 773
        
        btn_container = tk.Frame(ra, bg=BG_MAIN) # 774
        btn_container.pack(side="bottom", fill="x", pady=(int(10*s), 0)) # 775
        
        self.b_d = GlowButton(btn_container, text=l["del_btn"], color=DANGER, font_size=14, width=300, height=50, zoom=s, command=self.del_adm)  # 776
        self.b_d.pack(side="left", fill="x", expand=True, padx=(0, int(10*s))) # 777
        
        self.b_s = GlowButton(btn_container, text=l["save_btn"], color=SUCCESS, font_size=14, width=300, height=50, zoom=s, command=self.save_adm) # 778
        self.b_s.pack(side="right", fill="x", expand=True, padx=(int(10*s), 0)) # 779
        
        tk.Label(ra, text=l["cat_label"], bg=BG_MAIN, fg=TEXT_WHITE, font=("Segoe UI Bold", int(14*s))).pack(anchor="w", padx=off_p) # 780
        cl = tk.Frame(ra, bg=BG_MAIN); cl.pack(fill="x", pady=2, padx=off_p) # 781
        self.ecc = ttk.Combobox(cl, state="readonly", font=("Segoe UI Bold", int(16*s))); self.ecc.pack(side="left", fill="x", expand=True, ipady=int(10*s)) # 782
        self.ecc['values'] = sorted([self.get_cat_display(c) for c in self.categories_data.keys()]) # 783
        
        self.b_add_c = GlowButton(cl, text="+", color=SUCCESS, width=50, height=40, font_size=18, zoom=s, command=self.add_cat) # 784
        self.b_add_c.pack(side="left", padx=int(5*s)) # 785
        self.b_del_c = GlowButton(cl, text="-", color=DANGER, width=50, height=40, font_size=18, zoom=s, command=self.del_cat) # 786
        self.b_del_c.pack(side="left") # 787
        
        self.b_new = GlowButton(ra, text=l["add_new"], color=ACCENT_CYAN, font_size=13, width=350, height=40, zoom=s, command=self.clear_adm) # 788
        self.b_new.pack(fill="x", pady=(int(8*s), int(10*s))) # 789
        
        tk.Label(ra, text=l["name_label"], bg=BG_MAIN, fg=TEXT_WHITE, font=("Segoe UI Bold", int(14*s))).pack(anchor="w", padx=off_p) # 790
        self.a_en = tk.Entry(ra, font=("Segoe UI Bold", int(15*s)), bg=BG_PANEL, fg="white", bd=0, insertbackground="white", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_GOLD) # 791
        self.a_en.pack(fill="x", pady=2, ipady=int(12*s), padx=off_p) # 792
        
        tk.Label(ra, text=l["desc_label"], bg=BG_MAIN, fg=TEXT_WHITE, font=("Segoe UI Bold", int(14*s))).pack(anchor="w", padx=off_p) # 793
        self.a_rd = tk.Text(ra, height=3, font=("Segoe UI Semibold", int(14*s)), bg=BG_PANEL, fg="white", bd=0, insertbackground="white", wrap="word", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_GOLD) # 794
        self.a_rd.pack(fill="x", pady=2, padx=off_p) # 795
        
        tk.Label(ra, text=l["prompt_label"], bg=BG_MAIN, fg=TEXT_WHITE, font=("Segoe UI Bold", int(14*s))).pack(anchor="w", padx=off_p) # 796
        self.a_tp = scrolledtext.ScrolledText(ra, height=20, font=("Consolas Bold", int(14*s)), bg="#000", fg=TEXT_WHITE, bd=0, insertbackground="white", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 797
        self.a_tp.pack(fill="both", expand=True, pady=2, padx=off_p) # 798

        # --- TAB 3: ПЕРЕВОДЧИК ОНЛАЙН --- # 799
        self.trans_langs_ru = { # 800
            "Автоопределение": "auto", "Русский": "ru", "Английский": "en",  # 801
            "Испанский": "es", "Немецкий": "de", "Французский": "fr",  # 802
            "Китайский": "zh-CN", "Японский": "ja", "Итальянский": "it",  # 803
            "Корейский": "ko", "Польский": "pl", "Турецкий": "tr",  # 804
            "Арабский": "ar", "Хинди": "hi" # 805
        } # 806
        self.trans_langs_en = { # 807
            "Auto Detect": "auto", "Russian": "ru", "English": "en",  # 808
            "Spanish": "es", "German": "de", "French": "fr",  # 809
            "Chinese": "zh-CN", "Japanese": "ja", "Italian": "it",  # 810
            "Korean": "ko", "Polish": "pl", "Turkish": "tr",  # 811
            "Arabic": "ar", "Hindi": "hi" # 812
        } # 813
        self.current_trans_langs = self.trans_langs_ru if self.current_lang == "RU" else self.trans_langs_en # 814
        lang_names = list(self.current_trans_langs.keys()) # 815

        trans_container = tk.Frame(t3, bg=BG_MAIN) # 816
        trans_container.pack(fill="both", expand=True, padx=int(15*s), pady=int(10*s)) # 817
        
        tk.Label(trans_container, text="🌍 ОНЛАЙН ПЕРЕВОДЧИК" if self.current_lang == "RU" else "🌍 ONLINE TRANSLATOR", font=("Segoe UI Black", int(20*s)), bg=BG_MAIN, fg=ACCENT_CYAN).pack(pady=(0, int(10*s))) # 818
        
        btn_f_tr = tk.Frame(trans_container, bg=BG_MAIN) # 819
        btn_f_tr.pack(side="bottom", pady=int(10*s)) # 820
        
        btn_swap = GlowButton(btn_f_tr, text="⇄", color=ACCENT_CYAN, command=self.swap_langs, font_size=20, width=80, height=50, zoom=s) # 821
        btn_swap.pack(side="left", padx=int(10*s)) # 822
        
        btn_tr_main = GlowButton(btn_f_tr, text="ПЕРЕВЕСТИ / TRANSLATE", color=SUCCESS, command=self.do_translate, font_size=14, width=400, height=50, zoom=s) # 823
        btn_tr_main.pack(side="left", padx=int(10*s)) # 824

        trans_content = tk.Frame(trans_container, bg=BG_MAIN) # 825
        trans_content.pack(side="top", fill="both", expand=True) # 826

        left_f = tk.Frame(trans_content, bg=BG_MAIN) # 827
        left_f.place(relx=0.0, rely=0.0, relwidth=0.48, relheight=1.0) # 828
        
        top_l = tk.Frame(left_f, bg=BG_MAIN) # 829
        top_l.pack(fill="x", pady=(0, int(5*s))) # 830
        
        self.cb_src = ttk.Combobox(top_l, values=lang_names, state="readonly", font=("Segoe UI Bold", int(12*s))) # 831
        self.cb_src.set(lang_names[0])  # 832
        self.cb_src.pack(side="left") # 833
        
        tk.Button(top_l, text="📋 ВСТАВИТЬ / PASTE", bg=BG_PANEL, fg=TEXT_WHITE, font=("Segoe UI Bold", int(10*s)), bd=0, cursor="hand2", command=self.paste_trans_src).pack(side="right") # 834
        
        self.txt_trans_src = scrolledtext.ScrolledText(left_f, bg=BG_PANEL, fg=TEXT_WHITE, font=("Consolas", int(14*s)), bd=0, insertbackground="white", insertwidth=3, highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 835
        self.txt_trans_src.pack(fill="both", expand=True) # 836

        right_f = tk.Frame(trans_content, bg=BG_MAIN) # 837
        right_f.place(relx=0.52, rely=0.0, relwidth=0.48, relheight=1.0) # 838
        
        top_r = tk.Frame(right_f, bg=BG_MAIN) # 839
        top_r.pack(fill="x", pady=(0, int(5*s))) # 840
        
        self.cb_tgt = ttk.Combobox(top_r, values=lang_names[1:], state="readonly", font=("Segoe UI Bold", int(12*s))) # 841
        self.cb_tgt.set(lang_names[2])  # 842
        self.cb_tgt.pack(side="left") # 843
        
        tk.Button(top_r, text="📋 КОПИРОВАТЬ / COPY", bg=BG_PANEL, fg=TEXT_WHITE, font=("Segoe UI Bold", int(10*s)), bd=0, cursor="hand2", command=self.copy_trans_tgt).pack(side="right") # 844
        
        self.txt_trans_tgt = scrolledtext.ScrolledText(right_f, bg=BG_PANEL, fg=ACCENT_GREEN, font=("Consolas", int(14*s)), bd=0, insertbackground="white", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 845
        self.txt_trans_tgt.pack(fill="both", expand=True) # 846

        # --- TAB 4: ЛАУНЧПАД ГЕНЕРАЦИИ ВИДЕО --- # 847
        bg_anim = NeuralNetworkCanvas(t4, zoom=s) # 848
        bg_anim.place(relx=0, rely=0, relwidth=1, relheight=1) # 849
        
        video_container = tk.Frame(t4, bg=BG_PANEL, highlightthickness=2, highlightbackground=BORDER_GLOW, padx=int(30*s), pady=int(30*s)) # 850
        video_container.place(relx=0.5, rely=0.45, anchor="center")  # 851
        
        cv_w = int(800 * s) # 852
        cv_h = int(60 * s) # 853
        title_cv = tk.Canvas(video_container, width=cv_w, height=cv_h, bg=BG_PANEL, highlightthickness=0) # 854
        title_cv.pack(pady=(0, int(15*s))) # 855
        
        t_font = ("Segoe UI Black", int(28*s)) # 856
        t_text = l["video_title"] # 857
        offset = max(1, int(1.5 * s))  # 858
        
        for dx, dy in [(-offset,-offset), (-offset,offset), (offset,-offset), (offset,offset), (0,-offset), (-offset,0), (offset,0), (0,offset)]: # 859
            title_cv.create_text(cv_w/2 + dx, cv_h/2 + dy, text=t_text, font=t_font, fill="#ffffff") # 860
            
        title_cv.create_text(cv_w/2, cv_h/2, text=t_text, font=t_font, fill=ACCENT_CYAN) # 861
        
        txt_desc = tk.Label(video_container, text=l["video_desc"], font=("Segoe UI Semibold", int(14*s)), bg=BG_PANEL, fg=TEXT_WHITE, justify="center", wraplength=int(800*s)) # 862
        txt_desc.pack(pady=(0, int(20*s))) # 863
        
        btn_launch = GlowButton(video_container, text=l["video_btn"], color=SUCCESS, command=lambda: webbrowser.open("https://syntx.ai/"), font_size=16, width=400, height=60, zoom=s) # 864
        btn_launch.pack(pady=int(10*s)) # 865
        
        btn_promo = GlowButton(video_container, text=l["promo_btn"], color=ACCENT_GOLD, command=self.copy_promo, font_size=13, width=300, height=45, zoom=s) # 866
        btn_promo.pack(pady=int(10*s)) # 867

        # --- TAB 5: ИНФОРМАЦИЯ --- # 868
        info_content = INFO_RU if self.current_lang == "RU" else INFO_EN # 869
        clean_info = re.sub(r'\s*#\s*\d+$', '', info_content, flags=re.MULTILINE) # 870
        st_info = scrolledtext.ScrolledText(t5, font=("Segoe UI Semibold", int(15*s)), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, padx=int(45*s), pady=int(45*s), wrap="word", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 871
        st_info.pack(fill="both", expand=True, padx=int(15*s), pady=int(15*s)) # 872
        st_info.insert("1.0", clean_info) # 873
        st_info.config(state="disabled") # 874

        # --- TAB 6: ИНСТРУКЦИЯ --- # 875
        help_container = tk.Frame(t6, bg=BG_MAIN) # 876
        help_container.pack(fill="both", expand=True, padx=int(15*s), pady=int(15*s)) # 877

        help_content = HELP_RU if self.current_lang == "RU" else HELP_EN # 878
        clean_help = re.sub(r'\s*#\s*\d+$', '', help_content, flags=re.MULTILINE) # 879
        
        art_frame = tk.Frame(help_container, bg=BG_PANEL, width=int(320*s), highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 880
        art_frame.pack(side="right", fill="y") # 881
        art_frame.pack_propagate(False) # 882

        art_canvas = FutureArtCanvas(art_frame, zoom=s) # 883
        art_canvas.pack(fill="both", expand=True) # 884

        st_help = scrolledtext.ScrolledText(help_container, font=("Segoe UI Semibold", int(14*s)), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, padx=int(30*s), pady=int(30*s), wrap="word", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 885
        st_help.pack(side="left", fill="both", expand=True, padx=(0, int(15*s))) # 886
        st_help.insert("1.0", clean_help) # 887
        st_help.config(state="disabled") # 888
            
        self.nb.select(tab_index) # 889
        self.update_list() # 890

    def paste_trans_src(self): # 891
        try: # 892
            self.txt_trans_src.delete("1.0", tk.END) # 893
            self.txt_trans_src.insert("1.0", self.root.clipboard_get()) # 894
        except: pass # 895

    def copy_trans_tgt(self): # 896
        txt = self.txt_trans_tgt.get("1.0", tk.END).strip() # 897
        if txt and not txt.startswith("Перевод..."): # 898
            self.root.clipboard_clear() # 899
            self.root.clipboard_append(txt) # 900
            messagebox.showinfo("IKD", "Текст скопирован!" if self.current_lang == "RU" else "Copied!") # 901

    def swap_langs(self): # 902
        src = self.cb_src.get() # 903
        tgt = self.cb_tgt.get() # 904
        
        if src != "Автоопределение" and src != "Auto Detect": # 905
            self.cb_src.set(tgt) # 906
            self.cb_tgt.set(src) # 907
            
        src_text = self.txt_trans_src.get("1.0", tk.END).strip() # 908
        tgt_text = self.txt_trans_tgt.get("1.0", tk.END).strip() # 909
        
        self.txt_trans_src.delete("1.0", tk.END) # 910
        if tgt_text and not tgt_text.startswith("Перевод..."): # 911
            self.txt_trans_src.insert("1.0", tgt_text) # 912
            
        self.txt_trans_tgt.delete("1.0", tk.END) # 913
        if src_text: # 914
            self.txt_trans_tgt.insert("1.0", src_text) # 915

    def do_translate(self): # 916
        sl_name = self.cb_src.get() # 917
        tl_name = self.cb_tgt.get() # 918
        sl = self.current_trans_langs.get(sl_name, 'auto') # 919
        tl = self.current_trans_langs.get(tl_name, 'en') # 920
        
        src_txt = self.txt_trans_src.get("1.0", tk.END).strip() # 921
        if not src_txt: return # 922
        
        self.txt_trans_tgt.delete("1.0", tk.END) # 923
        self.txt_trans_tgt.insert("1.0", "Перевод... Пожалуйста, подождите..." if self.current_lang == "RU" else "Translating... Please wait...") # 924
        self.root.update() # 925
        
        def fetch_translation(): # 926
            try: # 927
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={urllib.parse.quote(src_txt)}" # 928
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # 929
                with urllib.request.urlopen(req, timeout=5) as response: # 930
                    data = json.loads(response.read().decode('utf-8')) # 931
                    res = ''.join([part[0] for part in data[0] if part[0]]) # 932
            except Exception as e: # 933
                res = f"Ошибка сети / Network error: Проверьте подключение к интернету.\n({e})" # 934
            
            self.root.after(0, lambda text=res: (self.txt_trans_tgt.delete("1.0", tk.END), self.txt_trans_tgt.insert("1.0", text))) # 935

        threading.Thread(target=fetch_translation, daemon=True).start() # 936

    def copy_promo(self): # 937
        self.root.clipboard_clear() # 938
        self.root.clipboard_append("SYNTX-IKDESIGNS") # 939
        messagebox.showinfo("IKD", LANG_DATA[self.current_lang]["promo_msg"]) # 940

    def switch_tab(self, idx): # 941
        self.show_main_interface(tab_index=idx) # 942

    def toggle_lang(self): # 943
        self.current_lang = "EN" if self.current_lang == "RU" else "RU" # 944
        self.show_main_interface() # 945

    def update_list(self): # 946
        self.listbox.delete(0, tk.END); self.cur_map = [] # 947
        sel, all_l = self.cat_var.get(), LANG_DATA[self.current_lang]["all_cats"] # 948
        for i, p in enumerate(self.prompts): # 949
            c_disp = self.get_cat_display(p.get('category', 'Общее')) # 950
            if sel == all_l or c_disp == sel: # 951
                self.listbox.insert(tk.END, f"  {self.get_item_name(p)}")  # 952
                self.cur_map.append(i) # 953

    def on_select(self, e): # 954
        if not self.listbox.curselection(): return # 955
        item = self.prompts[self.cur_map[self.listbox.curselection()[0]]] # 956
        self.lbl_p_n.config(text=self.get_item_name(item))  # 957
        
        c_val = item.get('category', 'Общее') # 958
        if self.current_lang == 'EN': # 959
            d_cat = self.categories_data.get(c_val, c_val) # 960
        else: # 961
            d_cat = c_val # 962
        self.lbl_main_cat.config(text=f"{LANG_DATA[self.current_lang]['main_cat_head']} {self.get_loc_text(d_cat)}") # 963
        
        desc = item.get('desc_ru', '') if self.current_lang == "RU" else item.get('desc_en', item.get('desc_ru', '')) # 964
        for w, t in [(self.txt_desc_main, self.get_loc_text(desc)), (self.txt_p_main, item.get('prompt', ''))]: # 965
            w.config(state="normal"); w.delete("1.0", tk.END); w.insert("1.0", t); w.config(state="disabled") # 966

    def copy_p(self): # 967
        c = self.txt_p_main.get("1.0", tk.END).strip() # 968
        if c: # 969
            self.root.clipboard_clear(); self.root.clipboard_append(c) # 970
            messagebox.showinfo("OK", LANG_DATA[self.current_lang]["copy_ok"]) # 971

    def update_admin_list(self): # 972
        self.alb.delete(0, tk.END); self.adm_map = [] # 973
        sel, all_l = self.afv.get(), LANG_DATA[self.current_lang]["all_cats"] # 974
        for i, p in enumerate(self.prompts): # 975
            c_disp = self.get_cat_display(p.get('category', 'Общее')) # 976
            if sel == all_l or c_disp == sel: # 977
                self.alb.insert(tk.END, f"  {self.get_item_name(p)}") # 978
                self.adm_map.append(i) # 979

    def on_admin_select(self, e): # 980
        if not self.alb.curselection(): return # 981
        self.cur_adm_idx = self.adm_map[self.alb.curselection()[0]] # 982
        it = self.prompts[self.cur_adm_idx] # 983
        self.ecc.set(self.get_cat_display(it.get('category', 'Общее'))) # 984
        self.a_en.delete(0, tk.END) # 985
        self.a_en.insert(0, self.get_item_name(it)) # 986
        self.a_tp.delete("1.0", tk.END); self.a_tp.insert("1.0", it.get('prompt', '')) # 987
        
        desc_text = it.get('desc_en', it.get('desc_ru', '')) if self.current_lang == "EN" else it.get('desc_ru', '') # 988
        self.a_rd.delete("1.0", tk.END); self.a_rd.insert("1.0", desc_text) # 989

    def save_adm(self): # 990
        cat_display = self.ecc.get() # 991
        prompt_name = self.a_en.get().strip() # 992
        
        if not cat_display or not prompt_name: # 993
            messagebox.showwarning("Внимание", "Необходимо заполнить категорию и название эффекта.") # 994
            return # 995

        ru_cat = next((r for r, e in self.categories_data.items() if e == cat_display or r == cat_display), cat_display) # 996
        
        desc_input = self.a_rd.get("1.0", tk.END).strip() # 997
        new_item = { # 998
            "name": prompt_name, # 999
            "category": ru_cat, # 1000
            "category_en": self.categories_data.get(ru_cat, ru_cat), # 1001
            "prompt": self.a_tp.get("1.0", tk.END).strip() # 1002
        } # 1003
        
        if self.current_lang == "EN": # 1004
            new_item["desc_en"] = desc_input # 1005
            if self.cur_adm_idx is not None: # 1006
                new_item["desc_ru"] = self.prompts[self.cur_adm_idx].get("desc_ru", "") # 1007
        else: # 1008
            new_item["desc_ru"] = desc_input # 1009
            if self.cur_adm_idx is not None: # 1010
                new_item["desc_en"] = self.prompts[self.cur_adm_idx].get("desc_en", "") # 1011
        
        user_list = [] # 1012
        if os.path.exists(self.user_data_file): # 1013
            try: # 1014
                with open(self.user_data_file, 'rb') as f: # 1015
                    user_list = self.decrypt_data(f.read()) # 1016
            except Exception as e: pass # 1017

        existing_names = [self.get_item_name(p) for p in user_list] # 1018

        if self.cur_adm_idx is None: # 1019
            if prompt_name in existing_names: # 1020
                messagebox.showerror("Ошибка", f"Промпт с названием '{prompt_name}' уже существует!\nПожалуйста, измените название, чтобы не удалить старый промпт.") # 1021
                return # 1022
        else: # 1023
            old_name = self.get_item_name(self.prompts[self.cur_adm_idx]) # 1024
            
            if old_name != prompt_name: # 1025
                if prompt_name in existing_names: # 1026
                    messagebox.showerror("Ошибка", f"Промпт с названием '{prompt_name}' уже существует!") # 1027
                    return # 1028
                
                ans = messagebox.askyesno("Сохранение", "Вы изменили название эффекта.\nСохранить как новый промпт?\n\n(Да - создать новый, Нет - переименовать старый)") # 1029
                if ans: # 1030
                    self.cur_adm_idx = None # 1031
                else: # 1032
                    user_list = [p for p in user_list if self.get_item_name(p) != old_name] # 1033
            else: # 1034
                user_list = [p for p in user_list if self.get_item_name(p) != old_name] # 1035

        user_list = [p for p in user_list if self.get_item_name(p) != prompt_name] # 1036
        user_list.append(new_item) # 1037
        
        try: # 1038
            with open(self.user_data_file, 'wb') as f: # 1039
                f.write(self.encrypt_data(user_list)) # 1040
        except OSError as e: # 1041
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}") # 1042
            return # 1043

        self.cur_adm_idx = None # 1044
        self.show_main_interface(tab_index=1) # 1045
    
    def del_adm(self): # 1046
        l = LANG_DATA[self.current_lang] # 1047
        if self.cur_adm_idx is None or not messagebox.askyesno(l["confirm_del"], l["ask_del"]): return # 1048
        n_raw = self.prompts[self.cur_adm_idx].get('name', self.prompts[self.cur_adm_idx].get('name_ru', self.prompts[self.cur_adm_idx].get('name_en', ''))) # 1049
        
        all_dat_files = [f for f in os.listdir(self.base_dir) if f.endswith(".ikd") and "seedance_prompts" in f.lower()] # 1050
        for f_name in all_dat_files: # 1051
            path = os.path.join(self.base_dir, f_name) # 1052
            try: # 1053
                with open(path, 'rb') as f: data = self.decrypt_data(f.read()) # 1054
                
                new_data = [p for p in data if p.get('name', p.get('name_ru', p.get('name_en', ''))) != n_raw] # 1055
                
                if len(new_data) != len(data): # 1056
                    with open(path, 'wb') as f: f.write(self.encrypt_data(new_data)) # 1057
            except: pass # 1058
        self.cur_adm_idx = None # 1059
        self.show_main_interface(tab_index=1) # 1060

    def add_cat(self): # 1061
        top = tk.Toplevel(self.root) # 1062
        top.title("Новая категория") # 1063
        top.geometry(f"{int(500*self.zoom_scale)}x{int(250*self.zoom_scale)}") # 1064
        top.configure(bg=BG_PANEL) # 1065
        top.transient(self.root) # 1066
        top.grab_set() # 1067

        sw, sh = self.root.winfo_width(), self.root.winfo_height() # 1068
        sx, sy = self.root.winfo_x(), self.root.winfo_y() # 1069
        top.geometry(f"+{sx + sw//2 - int(250*self.zoom_scale)}+{sy + sh//2 - int(125*self.zoom_scale)}") # 1070

        tk.Label(top, text="Введите название новой категории:", font=("Segoe UI Bold", int(14*self.zoom_scale)), bg=BG_PANEL, fg=TEXT_WHITE).pack(pady=int(20*self.zoom_scale)) # 1071
        
        cat_var = tk.StringVar() # 1072
        entry = tk.Entry(top, textvariable=cat_var, font=("Segoe UI Bold", int(16*self.zoom_scale)), bg=BG_MAIN, fg=TEXT_WHITE, insertbackground="white", highlightthickness=2, highlightcolor=ACCENT_CYAN, highlightbackground=BORDER_GLOW) # 1073
        entry.pack(fill="x", padx=int(30*self.zoom_scale), ipady=int(8*self.zoom_scale)) # 1074
        entry.focus_set() # 1075

        def save_new_cat(event=None): # 1076
            n = cat_var.get().strip() # 1077
            if n: # 1078
                if n not in self.categories_data: # 1079
                    self.categories_data[n] = n # 1080
                    new_vals = [LANG_DATA[self.current_lang]["all_cats"]] + sorted([self.get_cat_display(c) for c in self.categories_data.keys()]) # 1081
                    self.main_cb['values'] = new_vals # 1082
                    self.afc['values'] = new_vals # 1083
                    self.ecc['values'] = sorted([self.get_cat_display(c) for c in self.categories_data.keys()]) # 1084
                    self.ecc.set(self.get_cat_display(n)) # 1085
                top.destroy() # 1086

        entry.bind("<Return>", save_new_cat) # 1087
        
        btn = GlowButton(top, text="СОХРАНИТЬ", color=SUCCESS, command=save_new_cat, width=250, height=45, font_size=13, zoom=self.zoom_scale) # 1088
        btn.pack(pady=int(25*self.zoom_scale)) # 1089

    def del_cat(self): # 1090
        l = LANG_DATA[self.current_lang]; cd = self.ecc.get() # 1091
        if cd and messagebox.askyesno(l["confirm_del"], l["ask_del"]): # 1092
            rc = next((r for r, e in self.categories_data.items() if e == cd or r == cd), cd) # 1093
            all_dat = [f for f in os.listdir(self.base_dir) if f.endswith(".ikd") and "seedance_prompts" in f.lower()] # 1094
            for f_name in all_dat: # 1095
                path = os.path.join(self.base_dir, f_name) # 1096
                try: # 1097
                    with open(path, 'rb') as f: data = self.decrypt_data(f.read()) # 1098
                    new_d = [p for p in data if p.get('category') != rc] # 1099
                    if len(new_d) != len(data): # 1100
                        with open(path, 'wb') as f: f.write(self.encrypt_data(new_d)) # 1101
                except: pass # 1102
            self.categories_data.pop(rc, None); self.show_main_interface(tab_index=1) # 1103

    def clear_adm(self): # 1104
        self.cur_adm_idx = None; self.a_en.delete(0, tk.END); self.a_tp.delete("1.0", tk.END); self.a_rd.delete("1.0", tk.END) # 1105

    def show_language_selector(self): # 1106
        for w in self.root.winfo_children(): w.destroy() # 1107
        self.center_window(1300, 850)  # 1108
        c = tk.Frame(self.root, bg=BG_MAIN); c.place(relx=0.5, rely=0.5, anchor="center") # 1109
        tk.Label(c, text="CHOOSE LANGUAGE / ВЫБЕРИТЕ ЯЗЫК", font=("Segoe UI Bold", 18), bg=BG_MAIN, fg=TEXT_WHITE).pack(pady=20) # 1110
        btn_f = tk.Frame(c, bg=BG_MAIN); btn_f.pack() # 1111
        
        GlowButton(btn_f, text="ENGLISH", color=ACCENT_CYAN, font_size=14, width=200, height=50, command=lambda: self.set_lang_and_auth("EN")).pack(side="left", padx=10) # 1112
        GlowButton(btn_f, text="РУССКИЙ", color=ACCENT_GREEN, font_size=14, width=200, height=50, command=lambda: self.set_lang_and_auth("RU")).pack(side="left", padx=10) # 1113

    def set_lang_and_auth(self, lang): self.current_lang = lang; self.show_auth_window() # 1114

    def show_auth_window(self): # 1115
        for widget in self.root.winfo_children(): widget.destroy() # 1116
        self.center_window(1300, 850)  # 1117
        
        txt = { # 1118
            "RU": { # 1119
                "head": "🌊 Seedance Prompt Manager", "id": f"ID устройства: {self.hwid}",  # 1120
                "copy": "📋 Копировать ID", "act": "ПОДТВЕРДИТЬ АКТИВАЦИЮ",  # 1121
                "msg": "Идентификатор скопирован!", "err": "Ошибка: Ключ лицензии не прошел проверку",  # 1122
                "back": "↩ НАЗАД", "paste": "📋 ВСТАВИТЬ ИЗ БУФЕРА",  # 1123
                "entry_hint": "Введите ваш Код Активации или Ключ Лицензии" # 1124
            }, # 1125
            "EN": { # 1126
                "head": "🌊 Seedance Prompt Manager", "id": f"Device ID: {self.hwid}",  # 1127
                "copy": "📋 Copy ID", "act": "CONFIRM ACTIVATION",  # 1128
                "msg": "Device ID copied!", "err": "Error: Invalid License Key",  # 1129
                "back": "↩ BACK", "paste": "📋 PASTE FROM CLIPBOARD", # 1130
                "entry_hint": "Enter your Activation Code or License Key" # 1131
            } # 1132
        }[self.current_lang] # 1133

        c = tk.Frame(self.root, bg=BG_MAIN); c.place(relx=0.5, rely=0.5, anchor="center") # 1134
        
        tk.Button(c, text=txt["back"], bg=BG_PANEL, fg=TEXT_MUTED, font=("Segoe UI Bold", 10), bd=0, padx=10, pady=5, command=self.show_language_selector).pack(anchor="nw", pady=(0, 20)) # 1135
        
        tk.Label(c, text=txt["head"], font=("Segoe UI Black", 42), bg=BG_MAIN, fg=ACCENT_BLUE).pack() # 1136
        
        idf = tk.Frame(c, bg=BG_MAIN, pady=15); idf.pack() # 1137
        tk.Label(idf, text=txt["id"], bg=BG_MAIN, fg=TEXT_MUTED, font=("Consolas", 14)).pack(side="left", padx=15) # 1138
        tk.Button(idf, text=txt["copy"], bg="#333", fg="white", font=("Segoe UI Bold", 10), command=lambda: (self.root.clipboard_clear(), self.root.clipboard_append(self.hwid), messagebox.showinfo("ОК", txt["msg"])), bd=0).pack(side="left") # 1139
        
        self.ki = tk.Entry(c, font=("Consolas", 20), justify="center", bg=BG_PANEL, fg="white", width=35, insertbackground="white", highlightthickness=2, highlightbackground=BORDER_GLOW, highlightcolor=ACCENT_CYAN) # 1140
        self.ki.pack(pady=10, ipady=12) # 1141
        
        tk.Label(c, text=txt["entry_hint"], font=("Segoe UI Italic", 10), bg=BG_MAIN, fg=TEXT_MUTED).pack() # 1142
        
        self.status_lbl = tk.Label(c, text="", font=("Segoe UI Bold", 11), bg=BG_MAIN, fg=ACCENT_CYAN) # 1143
        self.status_lbl.pack(pady=5) # 1144
        
        tk.Button(c, text=txt["paste"], bg="#475569", fg="white", font=("Segoe UI Bold", 10), command=lambda: (self.ki.delete(0, tk.END), self.ki.insert(0, self.root.clipboard_get())), bd=0).pack(pady=15) # 1145
        
        self.btn_act = GlowButton(c, text=txt["act"], color=ACCENT_GREEN, command=lambda: self.activate_now(self.ki.get().strip().upper(), txt["err"]), font_size=16, width=380, height=70, zoom=self.zoom_scale) # 1146
        self.btn_act.pack(pady=10, fill="x") # 1147

    def activate_now(self, user_key, error_msg): # 1148
        txt = {"RU": {"checking": "🔍 ПРОВЕРКА ЛИЦЕНЗИИ...", "wait": "Пожалуйста, подождите...", "act": "ПОДТВЕРДИТЬ АКТИВАЦИЮ"},  # 1149
               "EN": {"checking": "🔍 CHECKING LICENSE...", "wait": "Please wait...", "act": "CONFIRM ACTIVATION"}}[self.current_lang] # 1150
        
        self.btn_act.set_text(txt["checking"]) # 1151
        self.btn_act.set_active(True) # 1152
        self.status_lbl.config(text=txt["wait"], fg=ACCENT_GOLD) # 1153
        self.root.update() # 1154

        if user_key.startswith("SEE-"): # 1155
            threading.Thread(target=self.server_activation, args=(user_key,), daemon=True).start() # 1156
            return # 1157

        hash_res = hashlib.sha256((self.hwid + SECRET_SALT).encode()).hexdigest().upper() # 1158
        expected = f"{hash_res[0:6]}-{hash_res[6:12]}-{hash_res[12:18]}" # 1159
        
        if user_key == expected: # 1160
            with open(self.lic_file, "w") as f: f.write(user_key) # 1161
            self.root.after(500, self.show_success_and_proceed) # 1162
        else: # 1163
            self.btn_act.set_text(txt["act"]) # 1164
            self.btn_act.set_active(False) # 1165
            self.status_lbl.config(text="") # 1166
            messagebox.showerror("Ошибка" if self.current_lang == "RU" else "Error", error_msg) # 1167

    def server_activation(self, code): # 1168
        txt_act = "ПОДТВЕРДИТЬ АКТИВАЦИЮ" if self.current_lang == "RU" else "CONFIRM ACTIVATION" # 1169
        
        def reset_ui_with_error(title, msg): # 1170
            messagebox.showerror(title, msg) # 1171
            self.btn_act.set_text(txt_act) # 1172
            self.btn_act.set_active(False) # 1173
            self.status_lbl.config(text="") # 1174

        try: # 1175
            os_info, ip, loc, username = get_telemetry() # 1176
            params = urllib.parse.urlencode({'hwid': self.hwid, 'pin': code, 'product': PRODUCT_ID, 'os': os_info, 'ip': ip, 'location': loc, 'username': username}).encode() # 1177
            req = urllib.request.Request(GOOGLE_SCRIPT_URL, data=params, method='POST') # 1178
            with urllib.request.urlopen(req, timeout=15) as response: # 1179
                res_data = json.loads(response.read().decode('utf-8')) # 1180
            
            if res_data.get("success"): # 1181
                final_key = res_data.get("key") # 1182
                with open(self.lic_file, "w") as f: f.write(final_key) # 1183
                self.save_sync_data(code) # 1184
                self.root.after(0, self.show_success_and_proceed) # 1185
            else: # 1186
                msg = res_data.get("message", "Ошибка активации") # 1187
                title = "Сервер" if self.current_lang == "RU" else "Server" # 1188
                self.root.after(0, lambda t=title, m=msg: reset_ui_with_error(t, f"Отказ: {m}")) # 1189
                
        except Exception as e: # 1190
            title = "Сеть" if self.current_lang == "RU" else "Network" # 1191
            err_msg = str(e) # 1192
            self.root.after(0, lambda t=title, m=err_msg: reset_ui_with_error(t, f"Сбой связи: {m}")) # 1193

    def show_success_and_proceed(self): # 1194
        msg = "✅ ЛИЦЕНЗИЯ УСПЕШНО АКТИВИРОВАНА!" if self.current_lang == "RU" else "✅ LICENSE SUCCESSFULLY ACTIVATED!" # 1195
        self.status_lbl.config(text=msg, fg=ACCENT_GREEN) # 1196
        self.btn_act.set_text("OK!") # 1197
        self.root.update() # 1198
        messagebox.showinfo("IK DESIGNS", msg) # 1199
        self.proceed_to_app() # 1200

    def proceed_to_app(self): # 1201
        v_path = resource_path("intro.mp4") # 1202
        if os.path.exists(v_path): # 1203
            self.play_intro(v_path) # 1204
        else: # 1205
            self.show_main_interface() # 1206

    def play_intro(self, v_path): # 1207
        if not HAS_VIDEO: # 1208
            msg = ( # 1209
                f"Внимание!\nВаша операционная система запустила этот скрипт через:\n{sys.executable}\n\n" # 1210
                f"В этом окружении Питона не установлены библиотеки для видео!\n" # 1211
                f"Хотите, чтобы программа прямо сейчас сама автоматически скачала и установила их?" # 1212
            ) # 1213
            if messagebox.askyesno("Авто-настройка Питона", msg): # 1214
                self.root.withdraw() # 1215
                load_win = tk.Toplevel() # 1216
                load_win.title("IKD Auto Installer") # 1217
                load_win.geometry("450x150") # 1218
                load_win.configure(bg="#0a0b10") # 1219
                load_win.update_idletasks() # 1220
                x = (load_win.winfo_screenwidth() // 2) - (450 // 2) # 1221
                y = (load_win.winfo_screenheight() // 2) - (150 // 2) # 1222
                load_win.geometry(f"+{x}+{y}") # 1223
                load_win.overrideredirect(True) # 1224
                
                tk.Label(load_win, text="⏳ ПОЖАЛУЙСТА, ПОДОЖДИТЕ...\n\nИдет загрузка и установка (OpenCV + PyGame-CE)...\nЭто займет около 10-20 секунд.", font=("Segoe UI Bold", 12), bg="#0a0b10", fg="#00d1ff").pack(expand=True) # 1225
                load_win.update() # 1226

                try: # 1227
                    si = None # 1228
                    if sys.platform == "win32": # 1229
                        si = subprocess.STARTUPINFO() # 1230
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW # 1231
                        
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "pillow", "pygame-ce"], startupinfo=si) # 1232
                    
                    load_win.destroy() # 1233
                    messagebox.showinfo("ГОТОВО ✅", "Библиотеки для видео и звука успешно скачаны!\n\nПожалуйста, закройте это окно и запустите программу заново (видео заработает).") # 1234
                    sys.exit() # 1235
                except Exception as ex: # 1236
                    load_win.destroy() # 1237
                    messagebox.showerror("Ошибка", f"Не удалось установить автоматически. Ошибка:\\n{ex}") # 1238
                    self.root.deiconify() # 1239
                    self.show_main_interface() # 1240
                return # 1241
            else: # 1242
                self.show_main_interface() # 1243
                return # 1244

        for widget in self.root.winfo_children(): widget.destroy() # 1245
        
        self.center_window(1300, 850) # 1246
        self.root.configure(bg="#000000") # 1247
        
        def finish_intro(e=None): # 1248
            self.show_main_interface() # 1249

        try: # 1250
            player = IKDVideoPlayer(self.root, v_path, finish_intro) # 1251
            player.place(x=0, y=0, relwidth=1, relheight=1) # 1252
            player.play() # 1253
            
        except Exception as e: # 1254
            messagebox.showerror("Ошибка плеера", f"Сбой при запуске видео:\n{e}") # 1255
            finish_intro() # 1256

if __name__ == "__main__": # 1257
    root = tk.Tk() # 1258
    app = SeedanceManager(root) # 1259
    root.mainloop() # 1260