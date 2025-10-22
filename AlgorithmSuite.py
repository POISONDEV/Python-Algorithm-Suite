import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk
import random
import sys, os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# คลาสสำหรับแต่ละ "หน้า"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.canvas = tk.Canvas(self, width=800, height=800, borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            self.gif_file = Image.open(resource_path("./images/background.gif"))
            self.frame_count = self.gif_file.n_frames
            
            original_width, original_height = self.gif_file.size
            canvas_width = 800
            canvas_height = 800
            ratio = max(canvas_width / original_width, canvas_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            self.gif_frames = []

            if self.frame_count > 1:
                for i in range(self.frame_count) :
                    self.gif_file.seek(i)
                    frame_image = self.gif_file.copy().resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.gif_frames.append(ImageTk.PhotoImage(frame_image))

                self.current_frame = 0
                self.bg_image_on_canvas = self.canvas.create_image(400, 400, image = self.gif_frames[0], anchor = "center")
                self.update_animation() # เริ่มแอนิเมชัน
            else:
                frame_image = self.gif_file.copy().resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.static_bg_image = ImageTk.PhotoImage(frame_image) 
                self.bg_image_on_canvas = self.canvas.create_image(400, 400, image = self.static_bg_image, anchor = "center")

            logo_img_pil = Image.open(resource_path("./images/logo_program.png"))
            self.logo_photo = ImageTk.PhotoImage(logo_img_pil)
            
            self.canvas.create_image(400, 180, image=self.logo_photo, anchor="center")

        except FileNotFoundError as e:
            print(f"ไม่พบไฟล์ภาพ: {e}")
            self.canvas.config(bg="black")
            self.canvas.create_text(400, 150, text="Algorithms Visualizer", font=("TA 16 Bit", 30, "bold"), fill="white", anchor="center")

        startBtn = tk.Button(self, text="เริ่มใช้งาน", font=("IBM Plex Sans Thai Regular", 15, "bold"), bg="#979797", fg="#FFFFFF", command=self.start_action)
        startBtn.place(x=340, y=300)

        creditBtn = tk.Button(self, text="ผู้จัดทำ", font=("IBM Plex Sans Thai Regular", 15, "bold"), bg="#979797", fg="#FFFFFF", command=lambda: controller.show_frame("CreditPage"))
        creditBtn.place(x=350, y=400)

        exitBtn = tk.Button(self, text="ออก", font=("IBM Plex Sans Thai Regular", 15, "bold"), bg="#979797", fg="#FFFFFF", command=self.exit_action)
        exitBtn.place(x=360, y=500)

        all_buttons = [startBtn, creditBtn, exitBtn]
        for button in all_buttons:
            button.bind("<Enter>", lambda event: self.controller.play_hover())

    def update_animation(self) :
        self.canvas.itemconfig(self.bg_image_on_canvas, image = self.gif_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.after(100, self.update_animation)      

    def start_action(self):
        self.controller.play_start()
        self.controller.show_frame("VisualizerPage")

    def exit_action(self):
        self.controller.play_click()
        if messagebox.askyesno("ออกจากโปรแกรม", "คุณต้องการออกจากโปรแกรมใช่หรือไม่"):
            self.controller.destroy()

class VisualizerPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#000000")
        self.controller = controller
        
        self.data = []
        self.algorithm_generator = None
        
        self.bar_rects = []
        self.bar_texts = []

        ui_frame = tk.Frame(self, bg="#000000")
        ui_frame.pack(side="top", fill="x", pady=10)

        tk.Label(ui_frame, text="อัลกอริทึม: ", font=("IBM Plex Sans Thai Regular", 14), bg="#000000", fg="white").pack(side="left", padx=5)

        self.algo_list = [
            "Bubble Sort", "Insertion Sort", "Selection Sort",
            "Merge Sort", "Sequential Search", "Binary Search"
        ]
        self.algo_menu = ttk.Combobox(ui_frame, values=self.algo_list, font=("IBM Plex Sans Thai Regular", 12), width=12)
        self.algo_menu.pack(side="left", padx=5)
        self.algo_menu["state"] = "readonly"
        self.algo_menu.set("Bubble Sort")

        random_btn = tk.Button(ui_frame, text="สุ่มข้อมูล", font=("IBM Plex Sans Thai Regular", 12, "bold"), bg="#979797", fg="#000000", command=self.generate_data)
        random_btn.pack(side="left", padx=5)

        tk.Label(ui_frame, text="ความเร็ว:", font=("IBM Plex Sans Thai Regular", 14), bg="#000000", fg="white").pack(side="left", padx=(10,0))
        self.speed_scale = ttk.Scale(ui_frame, from_=0.1, to=2.0, length=120, orient="horizontal")
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left", padx=5)
        
        self.start_button = tk.Button(ui_frame, text="เริ่มทำงาน", font=("IBM Plex Sans Thai Regular", 12, "bold"), bg="#5cb85c", fg="white", command=self.start_algorithm)
        self.start_button.pack(side="left", padx=5)
        
        self.search_frame = tk.Frame(ui_frame, bg="#000000")
        tk.Label(self.search_frame, text="เป้าหมาย:", font=("IBM Plex Sans Thai Regular", 14), bg="#000000", fg="white").pack(side="left", padx=(10,0))
        self.target_entry = tk.Entry(self.search_frame, font=("IBM Plex Sans Thai Regular", 12), width=5)
        self.target_entry.pack(side="left", padx=5)

        self.algo_menu.bind("<<ComboboxSelected>>", self.on_algo_select)
        self.on_algo_select(None)

        self.canvas = tk.Canvas(self, width=680, height=500, bg="#222222")
        self.canvas.pack(pady=20)
        
        backBtn = tk.Button(self, text="กลับไปหน้าหลัก", font=("IBM Plex Sans Thai Regular", 15, "bold"), bg="#979797", fg="#000000", command=self.back_action)
        backBtn.pack(pady=20)
        backBtn.bind("<Enter>", lambda event: self.controller.play_hover())

        self.generate_data()

    def back_action(self):
        self.controller.play_start()
        self.controller.show_frame("StartPage")

    def generate_data(self):
        """สุ่มข้อมูลตัวเลขขึ้นมาใหม่ และสร้าง/รีเซ็ต Canvas objects"""
        
        for item_id in self.bar_rects:
            self.canvas.delete(item_id)
        for item_id in self.bar_texts:
            self.canvas.delete(item_id)
        
        self.bar_rects = []
        self.bar_texts = []
        
        self.data = random.sample(range(1, 101), 50)
        
        for i in range(len(self.data)):
            rect_id = self.canvas.create_rectangle(0, 0, 0, 0, fill="white", outline="") # outline="" สะอาดตากว่า
            text_id = self.canvas.create_text(0, 0, text=str(self.data[i]), font=("Arial", 8), fill="white")
            
            self.bar_rects.append(rect_id)
            self.bar_texts.append(text_id)

        self.draw_data({})

    def draw_data(self, color_map):
        
        canvas_height = 500
        canvas_width = 680
        bar_width = canvas_width / (len(self.data) + 1)
        offset = 10
        spacing = 4

        if not self.data:
            return
            
        normalized_data = [i / max(self.data) for i in self.data]

        for i, height in enumerate(normalized_data):
            x0 = i * bar_width + offset + spacing
            y0 = canvas_height - height * (canvas_height - 20)
            x1 = (i + 1) * bar_width + offset
            y1 = canvas_height
            
            color = self.get_color(i, color_map)
            
            rect_id = self.bar_rects[i]
            text_id = self.bar_texts[i]
            
            # 1. ย้ายตำแหน่งสี่เหลี่ยม
            self.canvas.coords(rect_id, x0, y0, x1, y1)
            # 2. เปลี่ยนสีสี่เหลี่ยม
            self.canvas.itemconfig(rect_id, fill=color)
            
            # 3. ย้ายตำแหน่งข้อความ
            self.canvas.coords(text_id, (x0 + x1) / 2, y0 - 10)
            # 4. อัปเดตข้อความ (เผื่อมีการ swap ข้อมูล)
            self.canvas.itemconfig(text_id, text=str(self.data[i])) 
            
        self.controller.update_idletasks()

    def get_color(self, index, color_map):
        """กำหนดสีให้กับแท่งข้อมูล"""
        if index in color_map.get('found', []): return '#00FFFF'
        if index in color_map.get('pivots', []): return 'red'
        if index in color_map.get('actives', []): return '#ffb366'
        if index in color_map.get('low_ptr', []): return '#add8e6'
        if index in color_map.get('high_ptr', []): return '#ffb6c1'
        if index in color_map.get('merging', []): return '#8e44ad'
        if index in color_map.get('left_sub', []): return '#4a90e2'
        if index in color_map.get('right_sub', []): return '#f5a623'
        if color_map.get('sorted', False) and index in color_map.get('sorted_indices', []): return '#a6ff4d'
        return 'white'
    
    def start_algorithm(self):
        """เริ่มการทำงานของอัลกอริทึมที่เลือก"""
        selected_algo = self.algo_menu.get()
        
        if "Sort" in selected_algo:
            self.generate_data() 

        if selected_algo == "Bubble Sort":
            self.algorithm_generator = self.bubble_sort_generator()
            self.run_visualizer()
        elif selected_algo == "Insertion Sort":
            self.algorithm_generator = self.insertion_sort()
            self.run_visualizer()
        elif selected_algo == "Selection Sort":
            self.algorithm_generator = self.selection_sort_generator()
            self.run_visualizer()
        elif selected_algo == "Merge Sort":
            self.algorithm_generator = self.merge_sort_generator()
            self.run_visualizer()
        elif selected_algo == "Sequential Search":
            self.algorithm_generator = self.sequential_search_generator()
            self.run_visualizer()
        elif selected_algo == "Binary Search":
            self.algorithm_generator = self.binary_search_generator()
            self.run_visualizer()
        else:
            pass

    def on_algo_select(self, event):
        """ถูกเรียกใช้เมื่อมีการเลือกอัลกอริทึมใหม่ใน ComboBox"""
        selected_algo = self.algo_menu.get()

        if "Search" in selected_algo:
            self.search_frame.pack(side="left", padx=5)
            self.start_button.config(text="ค้นหา")
        else:
            self.search_frame.pack_forget()
            self.start_button.config(text="จัดเรียง")

    def bubble_sort_generator(self):
        """Bubble Sort Algorithm"""
        data = self.data
        n = len(data)
        
        for i in range(n - 1, 0, -1):
            for j in range(i):
                yield {'pivots': [j, j + 1]}
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
                    yield {'actives': [j, j + 1]}
        yield {'sorted': True, 'sorted_indices': list(range(n))}

    def insertion_sort(self):
        """Insertion Sort Algorithm"""
        data = self.data
        for i in range(1, len(data)):
            key = data[i]
            j = i - 1
            yield {'actives': [i], 'pivots': list(range(j + 1))}
            while j >= 0 and key < data[j]:
                yield {'actives': [i], 'pivots': [j]}
                data[j + 1] = data[j]
                j -= 1
                yield {'actives': [j+1], 'pivots': [i]} # ส่ง state ออกไปแทน
            data[j + 1] = key
        yield {'sorted': True, 'sorted_indices': list(range(len(data)))}

    def selection_sort_generator(self):
        """Selection Sort Algorithm"""
        data = self.data
        n = len(data)

        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                yield {'pivots': [min_idx], 'actives': [j]}
                if data[j] < data[min_idx]:
                    min_idx = j
            data[i], data[min_idx] = data[min_idx], data[i]
            yield {'sorted': True, 'sorted_indices': list(range(i + 1))}
        yield {'sorted': True, 'sorted_indices': list(range(n))}
    
    def merge_sort_generator(self):
        """Merge Sort"""
        yield from self._merge_sort_recursive(self.data, 0)
        yield {'sorted': True, 'sorted_indices': list(range(len(self.data)))}

    def _merge_sort_recursive(self, data, start_index):
        """ฟังก์ชัน Recursive ของ Merge Sort"""
        if len(data) > 1:
            mid = len(data) // 2
            left_half = data[:mid]
            right_half = data[mid:]

            yield {
                'left_sub': list(range(start_index, start_index + len(left_half))),
                'right_sub': list(range(start_index + len(left_half), start_index + len(data)))
            }

            yield from self._merge_sort_recursive(left_half, start_index)
            yield from self._merge_sort_recursive(right_half, start_index + mid)

            left_half = self.data[start_index : start_index + mid]
            right_half = self.data[start_index + mid : start_index + len(data)]

            i = j = k = 0
            
            while i < len(left_half) and j < len(right_half):
                yield {
                    'pivots': [start_index + k],
                    'merging': [start_index + i, start_index + mid + j]
                }
                
                if left_half[i] < right_half[j]:
                    data[k] = left_half[i]
                    i += 1
                else:
                    data[k] = right_half[j]
                    j += 1
                k += 1

            while i < len(left_half):
                data[k] = left_half[i]
                i += 1
                k += 1

            while j < len(right_half):
                data[k] = right_half[j]
                j += 1
                k += 1
            
            for idx in range(len(data)):
                self.data[start_index + idx] = data[idx]

            yield {'actives': list(range(start_index, start_index + len(data)))}

    def sequential_search_generator(self):
        """Sequential Search Algorithm"""
        try:
            target = int(self.target_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "กรุณาป้อนค่า Target เป็นตัวเลข")
            return

        found_index = -1
        for i in range(len(self.data)):
            yield {'actives': [i]}
            
            if self.data[i] == target:
                found_index = i
                yield {'found': [i]}
                messagebox.showinfo("ค้นหาสำเร็จ", f"พบค่า {target} ที่ตำแหน่งข้อมูล: {i}")
                break
        
        if found_index == -1:
            yield {'actives': [len(self.data)-1]}
            messagebox.showinfo("ไม่พบข้อมูล", f"ไม่พบค่า {target} ในชุดข้อมูล")

    def binary_search_generator(self):
        """Binary Search Algorithm"""
        try:
            target = int(self.target_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("กรอกค่าผิด", "กรุณาป้อนค่า Target เป็นตัวเลข")
            return

        self.data.sort()
        yield {'sorted': True, 'sorted_indices': list(range(len(self.data)))}

        low = 0
        high = len(self.data) - 1
        found = False

        while low <= high:
            mid = (low + high) // 2
            
            yield {
                'low_ptr': [low],
                'high_ptr': [high],
                'pivots': [mid]
            }

            if self.data[mid] == target:
                yield {'found': [mid]}
                messagebox.showinfo("ค้นหาสำเร็จ", f"พบค่า {target} ที่ตำแหน่งข้อมูล: {mid}")
                found = True
                break
            elif self.data[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        
        if not found:
            yield {'low_ptr': [low], 'high_ptr': [high]}
            messagebox.showinfo("ไม่พบข้อมูล", f"ไม่พบค่า {target} ในชุดข้อมูล")

    def run_visualizer(self):
        """ฟังก์ชันสำหรับแสดงการทำงานทีละขั้นตอน"""
        try:
            color_map = next(self.algorithm_generator)
            self.draw_data(color_map)
            speed = self.speed_scale.get()
            self.after(int(speed * 100), self.run_visualizer)
        except StopIteration:
            self.draw_data({'sorted': True, 'sorted_indices': list(range(len(self.data)))})
        except Exception as e:
            pass


class CreditPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.controller = controller

        self.canvas = tk.Canvas(self, width=800, height=800, borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        try:
            self.gif_file = Image.open(resource_path("./images/bg.png"))
            
            self.frame_count = self.gif_file.n_frames

            original_width, original_height = self.gif_file.size
            canvas_width = 800
            canvas_height = 800
            ratio = max(canvas_width / original_width, canvas_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            self.gif_frames = []

            if self.frame_count > 1:
                for i in range(self.frame_count) :
                    self.gif_file.seek(i)
                    frame_image = self.gif_file.copy().resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.gif_frames.append(ImageTk.PhotoImage(frame_image))
                
                self.current_frame = 0
                self.bg_image_on_canvas = self.canvas.create_image(400, 400, image = self.gif_frames[0], anchor = "center")
                self.update_animation() # เริ่มแอนิเมชัน
            else:
                frame_image = self.gif_file.copy().resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.static_bg_image = ImageTk.PhotoImage(frame_image) 
                self.bg_image_on_canvas = self.canvas.create_image(400, 400, image = self.static_bg_image, anchor = "center")

        except FileNotFoundError as e:
            print(f"ไม่พบไฟล์ภาพพื้นหลัง GIF: {e}")
            self.canvas.config(bg="black")
            self.canvas.create_rectangle(0, 0, 800, 800, fill="black", outline="black")
        
        # --- ส่วน Label และ Button ---
        creditTitle = tk.Label(self, text="รายชื่อผู้จัดทำ", font=("TH Sarabun New Bold", 22, "bold"), bg="#000000", fg="#FFFFFF")
        creditText0 = tk.Label(self, text="1. นายกรวิทย์ เหมหมิ 674234001", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")
        creditText1 = tk.Label(self, text="2. นายทองเจริญ โชติรัตน์ 674234007", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")
        creditText2 = tk.Label(self, text="3. นายธนพนธ์ เพ็งชัย 674234008", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")
        creditText3 = tk.Label(self, text="4. นายพงศกร อินชุม 674234009", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")
        creditText4 = tk.Label(self, text="5. นางสาวอารียา ศาลาแดง 674234019", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")
        creditText5 = tk.Label(self, text="6. นางสาวมธุรส บุญรอด 674234037", font=("TH Sarabun New Bold", 16, "bold"), bg="#000000", fg="#FFFFFF")

        self.canvas.create_window(400, 100, window=creditTitle, anchor="center")
        self.canvas.create_window(400, 220, window=creditText0, anchor="center")
        self.canvas.create_window(400, 260, window=creditText1, anchor="center")
        self.canvas.create_window(400, 300, window=creditText2, anchor="center")
        self.canvas.create_window(400, 340, window=creditText3, anchor="center")
        self.canvas.create_window(400, 380, window=creditText4, anchor="center")
        self.canvas.create_window(400, 420, window=creditText5, anchor="center")
        
        backBtn = tk.Button(self, text="กลับไปหน้าหลัก", font=("IBM Plex Sans Thai Regular", 15, "bold"), bg="#979797", fg="#000000", command=lambda: controller.show_frame("StartPage"))
        backBtn.bind("<Enter>", lambda event: self.controller.play_hover())
        
        self.canvas.create_window(400, 520, window=backBtn, anchor="center")

    def update_animation(self) :
        self.canvas.itemconfig(self.bg_image_on_canvas, image = self.gif_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.after(100, self.update_animation)

# คลาสสำหรับแอปพลิเคชันหลัก

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("800x800+650+100")
        self.title("Sorting & Searching Algorithms Visualizer")
        
        self.attributes('-alpha', 0.0)
        
        self.current_frame = None
        
        pygame.mixer.init()
        try:
            self.click_sound = pygame.mixer.Sound(resource_path("./sounds/click_sound.mp3"))
            self.hover_sound = pygame.mixer.Sound(resource_path("./sounds/hover_sound.mp3"))
            self.start_sound = pygame.mixer.Sound(resource_path("./sounds/start_sound.mp3"))

        except pygame.error as e:
            print(f"ไม่สามารถโหลดไฟล์เสียงได้: {e}")
            self.click_sound = None
            self.hover_sound = None
            self.start_sound = None
            
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, VisualizerPage, CreditPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage") 

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha = min(alpha + 0.1, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self.fade_in)

    def fade_out(self, page_name):
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha = max(alpha - 0.1, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, lambda: self.fade_out(page_name))
        else:
            frame = self.frames[page_name]
            self.current_frame = frame
            frame.tkraise()
            self.fade_in()

    def show_frame(self, page_name):
        """ฟังก์ชันสำหรับสลับหน้า (เอาเสียงคลิกออก)"""
        if page_name == "StartPage" :
            self.play_start_page_music()
        elif page_name == "VisualizerPage" :
            self.play_visualizer_music()
        else :
            self.stop_background_music()

        if self.current_frame is None:
            self.current_frame = self.frames[page_name]
            self.current_frame.tkraise()
            self.fade_in()
        elif self.current_frame is not self.frames[page_name]:
            self.fade_out(page_name)

    # --- ส่วนเพลงพื้นหลัง ---
    def play_start_page_music(self) :
        try :
            pygame.mixer.music.load(resource_path("./sounds/bg_Titlesound.flac"))
            pygame.mixer.music.play(loops = -1)
            pygame.mixer.music.set_volume(0.5)
        except pygame.error as e :
            print(f"ไม่สามารถเล่นเพลงพื้นหลังได้: {e}")

    def play_visualizer_music(self) :
        try :
            pygame.mixer.music.load(resource_path("./sounds/bg_Algosound.flac"))
            pygame.mixer.music.play(loops = -1)
            pygame.mixer.music.set_volume(0.2)
        except pygame.error as e :
            print(f"ไม่สามารถเล่นเพลงพื้นหลังได้: {e}")

    def stop_background_music(self) :
        try :
            pygame.mixer.music.stop()
        except pygame.error as e :
            print(f"ไม่สามารถหยุดเพลงพื้นหลังได้ : {e}")

    # --- ส่วนเสียง Sound Effect ---
    def play_click(self):
        if self.click_sound:
            self.click_sound.play()
            
    def play_hover(self):
        if self.hover_sound:
            self.hover_sound.play()
    def play_start(self):
        if self.start_sound:
            self.start_sound.play()

# --- รันโปรแกรม ---
if __name__ == "__main__":
    app = App()
    app.mainloop()