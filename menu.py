import threading
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox

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

        Label(root, text="Start date (DD/MM/YYYY):").pack()
        Entry(root, textvariable=self.start_date).pack()
        Label(root, text="End date (DD/MM/YYYY):").pack()
        Entry(root, textvariable=self.end_date).pack()
        Label(root, text="IE list (space separated):").pack()
        Entry(root, textvariable=self.ies).pack()
        Label(root, text="Download directory:").pack()
        Entry(root, textvariable=self.download_dir).pack()
        Button(root, text="Start", command=self.start).pack(pady=8)

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
