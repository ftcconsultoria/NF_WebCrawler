import threading
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Toplevel

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
        root.geometry("360x220")

        self.controller = PauseController()
        root.bind('<Motion>', self.controller.on_motion)

        self.start_date = StringVar()
        self.end_date = StringVar()
        self.ies = StringVar()
        self.download_dir = StringVar(value="downloads")

        crawler.set_prompt_callback(self.show_prompt)

        Label(root, text="Start date (DD/MM/YYYY):").pack()
        Entry(root, textvariable=self.start_date).pack()
        Label(root, text="End date (DD/MM/YYYY):").pack()
        Entry(root, textvariable=self.end_date).pack()
        Label(root, text="IE list (space separated):").pack()
        Entry(root, textvariable=self.ies).pack()
        Label(root, text="Download directory:").pack()
        Entry(root, textvariable=self.download_dir).pack()
        Button(root, text="Start", command=self.start).pack(pady=8)

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
        if not (self.start_date.get() and self.end_date.get() and ies_list):
            messagebox.showerror("Missing Data", "Please fill all fields.")
            return
        thread = threading.Thread(
            target=run_crawler,
            args=(
                self.start_date.get(),
                self.end_date.get(),
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
