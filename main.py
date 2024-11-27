import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from queue import Queue
from tkinter import messagebox
from tkinter import ttk
from typing import List, Dict

import pandas as pd
from PIL import Image, ImageTk
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds

current_dir = os.path.dirname(os.path.abspath(__file__))
imgdir = os.path.join(current_dir, "images")
datadir = os.path.join(current_dir, "data")


class EEGDataCollector:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.is_collecting = False
        self.all_data = []

        # Initialize MindRove board
        BoardShim.enable_dev_board_logger()
        params = MindRoveInputParams()
        board_id = BoardIds.MINDROVE_WIFI_BOARD
        self.board_shim = BoardShim(board_id, params)

        # Get channel information
        self.eeg_channels = BoardShim.get_eeg_channels(board_id)
        self.accel_channels = BoardShim.get_accel_channels(board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(board_id)

    def start_collection(self):
        self.board_shim.prepare_session()
        self.board_shim.start_stream()
        self.is_collecting = True
        threading.Thread(target=self.collect_data, daemon=True).start()

    def collect_data(self):
        while self.is_collecting:
            if self.board_shim.get_board_data_count() > 0:
                data = self.board_shim.get_current_board_data(1)  # Get one sample at a time
                timestamp = time.time()
                eeg_data = data[self.eeg_channels]
                accel_data = data[self.accel_channels]

                # Combine data with timestamp
                combined_data = {
                    'timestamp': timestamp,
                    **{f'CH{i + 1}': eeg_data[i][0] for i in range(len(self.eeg_channels))},
                    'ACCx': accel_data[0][0],
                    'ACCy': accel_data[1][0],
                    'ACCz': accel_data[2][0]
                }

                self.all_data.append(combined_data)
                self.data_queue.put(combined_data)

            time.sleep(1 / self.sampling_rate)  # Control sampling rate

    def stop_collection(self):
        self.is_collecting = False
        self.board_shim.stop_stream()
        self.board_shim.release_session()

    def get_all_data(self):
        return pd.DataFrame(self.all_data)


class ModernEntry(ttk.Frame):
    def __init__(self, parent, label_text, default_value=""):
        super().__init__(parent)

        # Configure style
        self.columnconfigure(1, weight=1)

        # Create and pack the label
        self.label = ttk.Label(
            self,
            text=label_text,
            style='Modern.TLabel'
        )
        self.label.grid(row=0, column=0, padx=(0, 10), pady=(0, 5), sticky='w')

        # Create and pack the entry
        self.entry = ttk.Entry(
            self,
            style='Modern.TEntry'
        )
        self.entry.insert(0, str(default_value))
        self.entry.grid(row=0, column=1, sticky='ew', pady=(0, 5))

    def get(self):
        return self.entry.get()


class SlideShow:
    def __init__(self, root: tk.Tk, slides: List[Dict[str, str]], data_dir: str = None):
        self.root = root
        self.slides = slides
        self.current_slide = 0
        self.current_repeat = 0
        self.data_queue = Queue()
        self.eeg_collector = EEGDataCollector(self.data_queue)
        self.subject_name = "unnamed"

        # Create data directory
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize trigger logging
        self.triggers = []

        # Initialize window
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        # Create canvas for displaying content
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)

        # Load and resize images
        self.images = {}
        for slide in slides:
            image = Image.open(slide['image'])
            image.thumbnail((400, 400))
            self.images[slide['image']] = ImageTk.PhotoImage(image)

        # Get user inputs
        self.setup_styles()
        self.get_parameters()

    def log_trigger(self, stage, slide_info=None):
        timestamp = time.time()
        trigger_data = {
            'timestamp': timestamp,
            'stage': stage,
            'slide_number': self.current_slide if slide_info else None,
            'slide_text': self.slides[self.current_slide]['text'] if slide_info else None,
            'slide_image': self.slides[self.current_slide]['image'] if slide_info else None,
            'repeat_number': self.current_repeat
        }
        self.triggers.append(trigger_data)

    def setup_styles(self):
        # Configure the style for the modern UI
        style = ttk.Style()
        style.configure('Modern.TFrame', background='#f0f0f0')
        style.configure('Modern.TLabel',
                        font=('Helvetica', 11),
                        background='#f0f0f0',
                        foreground='#333333')
        style.configure('Modern.TEntry',
                        fieldbackground='white',
                        font=('Helvetica', 11))
        style.configure('Modern.TButton',
                        font=('Helvetica', 12, 'bold'),
                        padding=10)
        style.configure('Title.TLabel',
                        font=('Helvetica', 16, 'bold'),
                        background='#f0f0f0',
                        foreground='#2c3e50',
                        padding=(0, 10))
        style.configure('Subtitle.TLabel',
                        font=('Helvetica', 10),
                        background='#f0f0f0',
                        foreground='#7f8c8d',
                        padding=(0, 0, 0, 20))

    def get_parameters(self):
        self.root.withdraw()

        # Create input window
        input_window = tk.Toplevel()
        input_window.title("EEG Data Collection Setup")

        # Calculate window size and position
        window_width = 500
        window_height = 600
        screen_width = input_window.winfo_screenwidth()
        screen_height = input_window.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        input_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        input_window.configure(bg='#f0f0f0')
        input_window.resizable(False, False)

        # Create main frame
        main_frame = ttk.Frame(input_window, style='Modern.TFrame', padding="30 20 30 20")
        main_frame.pack(fill='both', expand=True)

        # Title and description
        title = ttk.Label(
            main_frame,
            text="EEG Data Collection Setup",
            style='Title.TLabel'
        )
        title.pack(fill='x')

        subtitle = ttk.Label(
            main_frame,
            text="Configure the parameters for the slideshow and data collection",
            style='Subtitle.TLabel',
            wraplength=440
        )
        subtitle.pack(fill='x')

        # Create separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(0, 20))

        # Create form frame
        form_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        form_frame.pack(fill='both', expand=True)

        # Subject Information Section
        subject_section = ttk.LabelFrame(
            form_frame,
            text="Subject Information",
            style='Modern.TFrame',
            padding="10"
        )
        subject_section.pack(fill='x', pady=(0, 20))

        self.subject_entry = ModernEntry(subject_section, "Subject Name:", "unnamed")
        self.subject_entry.pack(fill='x')

        # Timing Parameters Section
        timing_section = ttk.LabelFrame(
            form_frame,
            text="Timing Parameters",
            style='Modern.TFrame',
            padding="10"
        )
        timing_section.pack(fill='x')

        params = {
            'concentration_duration': ('Concentration Duration (ms)', 500),
            'image_duration': ('Image Duration (ms)', 1000),
            'action_duration': ('Action Duration (ms)', 2500),
            'relax_duration': ('Relax Duration (ms)', 1000),
            'rest_duration': ('Rest Duration (ms)', 1000),
        }

        self.durations = {}
        for key, (label, default) in params.items():
            self.durations[key] = ModernEntry(timing_section, label, default)
            self.durations[key].pack(fill='x')

        # Repetition Section
        repeat_section = ttk.LabelFrame(
            form_frame,
            text="Repetition",
            style='Modern.TFrame',
            padding="10"
        )
        repeat_section.pack(fill='x', pady=(20, 0))

        self.durations['repeats'] = ModernEntry(repeat_section, "Number of Repeats:", 1)
        self.durations['repeats'].pack(fill='x')

        # Add some spacing
        ttk.Frame(main_frame, style='Modern.TFrame', height=20).pack()

        # Start button
        start_button = ttk.Button(
            main_frame,
            text="Start Collection",
            command=lambda: self.start_slideshow(input_window, self.subject_entry.entry),
            style='Modern.TButton'
        )
        start_button.pack(fill='x', pady=(20, 0))

        input_window.mainloop()

    def start_slideshow(self, input_window, subject_entry):
        # Store the subject name before destroying the window
        self.subject_name = subject_entry.get() or "unnamed"

        try:
            self.action_duration = int(self.durations['action_duration'].get())
            self.concentration_duration = int(self.durations['concentration_duration'].get())
            self.image_duration = int(self.durations['image_duration'].get())
            self.relax_duration = int(self.durations['relax_duration'].get())
            self.rest_duration = int(self.durations['rest_duration'].get())
            self.total_repeats = int(
                self.durations['repeats'].get()) - 1  # Subtract 1 since we start from 0
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numbers")
            return

        input_window.destroy()
        self.root.deiconify()

        # Start EEG data collection
        self.eeg_collector.start_collection()

        # Start the slideshow after 5000ms delay
        self.root.after(5000, self.show_next_state)

    def clear_canvas(self):
        self.canvas.delete('all')

    def draw_circle(self, color):
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        circle_radius = 50
        self.canvas.create_oval(
            width / 2 - circle_radius,
            height / 2 - circle_radius,
            width / 2 + circle_radius,
            height / 2 + circle_radius,
            fill=color,
            outline=color
        )

    def show_slide(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        current_slide = self.slides[self.current_slide]
        image = self.images[current_slide['image']]
        image_height = image.height()

        image_y = height / 2 - image_height / 2 - 50
        self.canvas.create_image(
            width / 2,
            image_y,
            image=image,
            anchor='n'
        )

        text_y = image_y + image_height + 50
        self.canvas.create_text(
            width / 2,
            text_y,
            text=current_slide['text'],
            fill='white',
            font=('Arial', 24),
            anchor='n'
        )

    def save_data(self):
        # Generate timestamp string for filenames
        timestamp = datetime.now().strftime("%d_%m_%y_%H_%M_%S")

        # Save EEG data
        eeg_filename = os.path.join(self.data_dir, f"{self.subject_name}_{timestamp}.csv")
        df = self.eeg_collector.get_all_data()
        df.to_csv(eeg_filename, index=False)

        # Save triggers data
        triggers_filename = os.path.join(self.data_dir,
                                         f"{self.subject_name}_triggers_{timestamp}.csv")
        triggers_df = pd.DataFrame(self.triggers)
        triggers_df.to_csv(triggers_filename, index=False)

        # Exit program
        self.root.quit()
        self.root.destroy()
        sys.exit()

    def show_next_state(self):
        self.clear_canvas()

        if not hasattr(self, 'current_state'):
            self.current_state = 0

        if self.current_state == 0:  # Concentration
            self.log_trigger('concentration')
            self.draw_circle('green')
            self.root.after(self.concentration_duration, self.show_next_state)

        elif self.current_state == 1:  # Image
            self.log_trigger('image', slide_info=True)
            self.show_slide()
            self.root.after(self.image_duration, self.show_next_state)

        elif self.current_state == 2:  # Action
            self.log_trigger('action')
            self.draw_circle('white')
            self.root.after(self.action_duration, self.show_next_state)

        elif self.current_state == 3:  # Relax
            self.log_trigger('relax')
            self.draw_circle('red')
            self.root.after(self.relax_duration, self.show_next_state)

        elif self.current_state == 4:  # Rest
            self.log_trigger('rest')
            self.root.after(self.rest_duration, self.show_next_state)

        self.current_state = (self.current_state + 1) % 5

        if self.current_state == 0:
            self.current_slide = (self.current_slide + 1) % len(self.slides)
            if self.current_slide == 0:
                if self.current_repeat >= self.total_repeats:
                    self.eeg_collector.stop_collection()
                    self.save_data()
                    return
                self.current_repeat += 1


def main():
    slides = [
        {"text": "فوق", "image": os.path.join(imgdir, "up.webp")},
        {"text": "تحت", "image": os.path.join(imgdir, "down.webp")},
        {"text": "اختيار", "image": os.path.join(imgdir, "select.webp")},
        {"text": "إلغاء", "image": os.path.join(imgdir, "cancel.webp")},
    ]

    root = tk.Tk()
    app = SlideShow(root, slides, datadir)
    root.mainloop()


if __name__ == "__main__":
    main()
