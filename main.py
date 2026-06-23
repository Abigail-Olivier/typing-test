import tkinter as tk
from text_generator import generate_typing_text

class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("750x600")

        # Clean minimalist layout spacing and canvas color
        self.root.config(padx=40, pady=40, bg="#F5F5F7")

        # Configuration menu variables
        self.mode_var = tk.StringVar(value="time")
        self.intensity_var = tk.StringVar(value="1")

        self.target_string = ""

        # Core application state variables
        self.timer_started = False
        self.time_left = 0
        self.elapsed_seconds = 0

        # Word tracking indexes for live highlight coloring
        self.current_word_index = 0
        self.target_words_list = []

        # Setup configuration frame container
        self.setup_frame = tk.Frame(self.root, bg="#F5F5F7")
        self.setup_frame.pack(fill="both", expand=True)

        self.test_frame = None

        self.create_setup_screen()

    def create_setup_screen(self):
        title_label = tk.Label(self.setup_frame, text="Typing Speed Test", font=("Helvetica", 24, "bold"), bg="#F5F5F7",
                               fg="#1D1D1F")
        title_label.pack(pady=(0, 30))

        mode_label = tk.Label(self.setup_frame, text="Select Test Type:", font=("Helvetica", 12), bg="#F5F5F7",
                              fg="#86868B")
        mode_label.pack(anchor="w", pady=(10, 2))
        mode_menu = tk.OptionMenu(self.setup_frame, self.mode_var, "time", "page")
        mode_menu.config(font=("Helvetica", 11), width=15)
        mode_menu.pack(anchor="w", pady=(0, 15))

        intensity_label = tk.Label(self.setup_frame, text="Select Duration / Length (1-3):", font=("Helvetica", 12),
                                   bg="#F5F5F7", fg="#86868B")
        intensity_label.pack(anchor="w", pady=(10, 2))
        intensity_menu = tk.OptionMenu(self.setup_frame, self.intensity_var, "1", "2", "3")
        intensity_menu.config(font=("Helvetica", 11), width=15)
        intensity_menu.pack(anchor="w", pady=(0, 30))

        start_button = tk.Button(self.setup_frame, text="Start Test", font=("Helvetica", 12, "bold"), bg="#0071E3",
                                 fg="white", activebackground="#005BB5", activeforeground="white", relief="flat",
                                 padx=20, pady=8, command=self.start_test)
        start_button.pack(pady=10)

    def start_test(self):
        chosen_mode = self.mode_var.get()
        chosen_intensity = int(self.intensity_var.get())

        # Generate sample text block
        self.target_string = generate_typing_text(chosen_mode, chosen_intensity)
        self.target_words_list = self.target_string.split()

        # Reset counters and state tracker flags
        self.timer_started = False
        self.elapsed_seconds = 0
        self.current_word_index = 0

        if chosen_mode == "time":
            self.time_left = chosen_intensity * 60
        else:
            self.time_left = 0

        self.setup_frame.pack_forget()

        self.test_frame = tk.Frame(self.root, bg="#F5F5F7")
        self.test_frame.pack(fill="both", expand=True)

        self.create_test_screen()

    def create_test_screen(self):
        stats_bar = tk.Frame(self.test_frame, bg="#F5F5F7")
        stats_bar.pack(fill="x", pady=(0, 20))

        timer_display_text = f"Time Remaining: {self.time_left}s" if self.mode_var.get() == "time" else "Time Elapsed: 0s"
        self.timer_label = tk.Label(stats_bar, text=timer_display_text, font=("Helvetica", 12, "bold"), bg="#F5F5F7",
                                    fg="#1D1D1F")
        self.timer_label.pack(side="left")

        self.status_label = tk.Label(stats_bar, text="Typing...", font=("Helvetica", 12), bg="#F5F5F7", fg="#0071E3")
        self.status_label.pack(side="right", padx=10)

        # Read-only text screen showing sample paragraphs to replicate
        self.text_display = tk.Text(self.test_frame, font=("Helvetica", 15), wrap="word", height=6, bg="white",
                                    fg="#1D1D1F", relief="flat", padx=15, pady=15)
        self.text_display.insert("1.0", self.target_string)

        # Explicitly using background and foreground properties to avoid Tkinter bitmap crashes
        self.text_display.tag_config("correct", background="#E2F6EA", foreground="#34C759")
        self.text_display.tag_config("incorrect", background="#FEE7E6", foreground="#FF3B30")
        self.text_display.tag_config("active", background="#E8F0FE", underline=True)

        self.text_display.config(state="disabled")
        self.text_display.pack(fill="x", pady=(0, 20))

        # Highlight the very first word as ready to type
        self.highlight_target_word(0, "active")

        # Interactive writing input area for user keyboard entries
        self.input_entry = tk.Text(self.test_frame, font=("Helvetica", 15), wrap="word", height=4, bg="white",
                                   fg="#1D1D1F", relief="flat", padx=15, pady=15, insertbackground="#0071E3")
        self.input_entry.pack(fill="x", pady=(0, 10))
        self.input_entry.focus()

        # Connect event listeners for live input character changes and space bar strikes
        self.input_entry.bind("<<Modified>>", self.handle_live_typing)
        self.input_entry.bind("<space>", self.handle_space_press)

    def highlight_target_word(self, word_index, tag_name):
        """Finds a word position index inside the text field and applies a color style tag."""
        if word_index >= len(self.target_words_list):
            return

        self.text_display.config(state="normal")

        # Remove old active cursor highlight lines safely
        if tag_name != "active":
            self.text_display.tag_remove("active", "1.0", "end")

        # Calculate character indexing coordinates for text tagging arrays
        start_char_pos = sum(len(w) + 1 for w in self.target_words_list[:word_index])
        end_char_pos = start_char_pos + len(self.target_words_list[word_index])

        start_index_str = f"1.0 + {start_char_pos} chars"
        end_index_str = f"1.0 + {end_char_pos} chars"

        self.text_display.tag_add(tag_name, start_index_str, end_index_str)
        self.text_display.config(state="disabled")

    def handle_live_typing(self, event):
        if not self.input_entry.edit_modified():
            return

        if not self.timer_started:
            self.timer_started = True
            self.run_timer_loop()

        # Verify page layout mode completion status
        user_input = self.input_entry.get("1.0", "end-1c")
        if self.mode_var.get() == "page" and user_input.strip() == self.target_string.strip():
            self.end_test_session()

        self.input_entry.edit_modified(False)

    def handle_space_press(self, event):
        """Triggered immediately when the user presses space, validating the finished word."""
        if not self.timer_started:
            return

        # Fetch the full text currently inside the writing box
        full_typed_text = self.input_entry.get("1.0", "end-1c")
        typed_words = full_typed_text.split()

        # Safety check to see if there is a word ready to parse
        if not typed_words or self.current_word_index >= len(self.target_words_list):
            return

        # Isolate the latest single word typed by the user
        latest_typed_word = typed_words[-1]
        goal_word = self.target_words_list[self.current_word_index]

        # Apply immediate colour highlight feedback based on a direct string match
        if latest_typed_word == goal_word:
            self.highlight_target_word(self.current_word_index, "correct")
        else:
            self.highlight_target_word(self.current_word_index, "incorrect")

        # Shift progress over by 1 word and mark the next one as active
        self.current_word_index += 1
        if self.current_word_index < len(self.target_words_list):
            self.highlight_target_word(self.current_word_index, "active")
        else:
            self.end_test_session()

    def run_timer_loop(self):
        if not self.timer_started:
            return

        if self.mode_var.get() == "time":
            if self.time_left > 0:
                self.time_left -= 1
                self.elapsed_seconds += 1
                self.timer_label.config(text=f"Time Remaining: {self.time_left}s")
                self.root.after(1000, self.run_timer_loop)
            else:
                self.end_test_session()
        else:
            self.elapsed_seconds += 1
            self.timer_label.config(text=f"Time Elapsed: {self.elapsed_seconds}s")
            self.root.after(1000, self.run_timer_loop)

    def end_test_session(self):
        self.timer_started = False

        # Clear the underline marker from the remaining text
        self.text_display.config(state="normal")
        self.text_display.tag_remove("active", "1.0", "end")
        self.text_display.config(state="disabled")

        # Remove the input writing text box from view
        self.input_entry.pack_forget()
        self.status_label.config(text="Test Complete!", fg="#34C759")

        # Parse final inputs to calculate scorecards
        user_final_text = self.input_entry.get("1.0", "end-1c")
        user_words = user_final_text.split()

        correct_words_count = 0
        incorrect_words_count = 0

        # Loop through typed words to tally final metrics
        for index in range(len(user_words)):
            if index >= len(self.target_words_list):
                break
            if user_words[index] == self.target_words_list[index]:
                correct_words_count += 1
            else:
                incorrect_words_count += 1

        # Fallback tracking for skipped words if timer cuts off mid-session
        if len(user_words) < self.current_word_index:
            incorrect_words_count = self.current_word_index - correct_words_count

        total_chars_typed = len(user_final_text)
        minutes_passed = max(self.elapsed_seconds, 1) / 60
        gross_wpm = int((total_chars_typed / 5) / minutes_passed)

        total_words_attempted = correct_words_count + incorrect_words_count
        final_accuracy = int((correct_words_count / total_words_attempted) * 100) if total_words_attempted > 0 else 100

        # Create a visual metric dashboard layout panel below the highlighted text
        self.results_dashboard = tk.Frame(self.test_frame, bg="#F5F5F7")
        self.results_dashboard.pack(fill="x", pady=10)

        metrics_box = tk.Frame(self.results_dashboard, bg="white", relief="flat", padx=25, pady=25)
        metrics_box.pack(fill="x", pady=10)

        speed_label = tk.Label(metrics_box, text=f"Typing Speed: {gross_wpm} WPM", font=("Helvetica", 14, "bold"),
                               bg="white", fg="#1D1D1F")
        speed_label.pack(anchor="w", pady=6)

        accuracy_label = tk.Label(metrics_box, text=f"Accuracy Rate: {final_accuracy}%", font=("Helvetica", 14, "bold"),
                                  bg="white", fg="#1D1D1F")
        accuracy_label.pack(anchor="w", pady=6)

        errors_label = tk.Label(metrics_box, text=f"Total Mistakes: {incorrect_words_count}",
                                font=("Helvetica", 14, "bold"), bg="white", fg="#FF3B30")
        errors_label.pack(anchor="w", pady=6)

        restart_button = tk.Button(self.results_dashboard, text="Try Again", font=("Helvetica", 12, "bold"),
                                   bg="#0071E3", fg="white", activebackground="#005BB5", activeforeground="white",
                                   relief="flat", padx=20, pady=8, command=self.reset_and_try_again)
        restart_button.pack(pady=20)

    def reset_and_try_again(self):
        # Destroy the temporary dashboard layout panels
        self.results_dashboard.destroy()
        self.test_frame.destroy()

        # Bring back original landing configuration page
        self.setup_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    window = tk.Tk()
    app = TypingTestApp(window)
    window.mainloop()
