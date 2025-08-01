import threading
from tkinter import (
    Tk,
    Label,
    Entry,
    Button,
    StringVar,
    messagebox,
    Toplevel,
    filedialog,
)

import crawler
from pause import PauseController


def run_crawler(start_date: str, end_date: str, ies: list[str], download_dir: str, controller: PauseController):
    args = [
        '--start-date', start_date,
        '--end-date', end_date,
        '--download-dir', download_dir,
        '--ies',
    ] + ies
    crawler.set_pause_controller(controller)
    crawler.main(args)


class App:
    def __init__(self, root: Tk):
        self.root = root
        root.title("NF WebCrawler")
        root.geometry("360x250")

        self.controller = PauseController()
        root.bind('<Motion>', self.controller.on_motion)

        self.month = StringVar()
        self.year = StringVar()
        self.ies = StringVar()
        self.download_dir = StringVar(value="downloads")

        crawler.set_prompt_callback(self.show_prompt)

        Label(root, text="M\u00eas (MM):").pack()
        Entry(root, textvariable=self.month).pack()
        Label(root, text="Ano (YYYY):").pack()
        Entry(root, textvariable=self.year).pack()
        Label(root, text="IE list (space separated):").pack()
        Entry(root, textvariable=self.ies).pack()
        Label(root, text="Download directory:").pack()
        dir_frame = Entry(root, textvariable=self.download_dir)
        dir_frame.pack()
        Button(root, text="Browse", command=self.browse_dir).pack(pady=2)
        Button(root, text="Start", command=self.start).pack(pady=8)

    def browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.download_dir.get())
        if path:
            self.download_dir.set(path)

    def show_prompt(self, text: str):
        """Display a modal dialog asking the user to continue."""
        event = threading.Event()

        def _show():
            win = Toplevel(self.root)
            win.title("NF WebCrawler")
            Label(win, text=text, wraplength=320).pack(padx=10, pady=10)
            Button(win, text="Continuar", command=lambda: (event.set(), win.destroy())).pack(pady=5)
            win.transient(self.root)
            win.grab_set()

        self.root.after(0, _show)
        event.wait()

    def start(self):
        ies_list = [v for v in self.ies.get().split() if v]
        month = self.month.get().zfill(2)
        year = self.year.get()
        if not (month and year and ies_list):
            messagebox.showerror("Missing Data", "Please fill all fields.")
            return
        start_date = f"01/{month}/{year}"
        end_date = f"31/{month}/{year}"
        thread = threading.Thread(
            target=run_crawler,
            args=(
                start_date,
                end_date,
                ies_list,
                self.download_dir.get(),
                self.controller,
            ),
            daemon=True,
        )
        thread.start()


def main():
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
