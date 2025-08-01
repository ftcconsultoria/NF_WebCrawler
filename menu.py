import sys
import crawler


def prompt_list(prompt):
    values = input(prompt).strip()
    if not values:
        return []
    return [v for v in values.split() if v]


def main():
    print("NF WebCrawler Interactive Mode")
    while True:
        start_date = input("Start date (DD/MM/YYYY) or 'q' to quit: ").strip()
        if start_date.lower() == 'q':
            break
        end_date = input("End date (DD/MM/YYYY): ").strip()
        ies = prompt_list("IE list (space separated): ")
        download_dir = input("Download directory [downloads]: ").strip() or "downloads"
        action = input("Type 'start' to begin or anything else to re-enter values: ").strip().lower()
        if action == 'start':
            sys.argv = [
                'crawler',
                '--start-date', start_date,
                '--end-date', end_date,
                '--download-dir', download_dir,
                '--ies',
            ] + ies
            crawler.main()
        else:
            print("Re-enter the values or type 'q' to quit.")


if __name__ == '__main__':
    main()
