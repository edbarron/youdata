from datetime import datetime, timedelta
from collections import Counter
import re

LATAM_SPANISH_STOPWORDS = set([
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
    "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más",
    "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde",
    "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni",
    "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes",
    "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto",
    "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco",
    "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis",
    "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "ustedes", "vosotros",
    "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya",
    "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra",
    "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras",
    "esos", "esas", "estoy", "estás", "está", "estamos", "están", "andan",
    "andan", "anda", "andamos", "andás", "andan", "así", "es", "entonces", "pues"
])

def extract_keywords_from_titles_over_views(videos, view_threshold=3000, min_freq=2):
    """
    Extracts trending keywords from video titles, filtering out stopwords and
    ignoring words that appear less than `min_freq` times.
    Returns all keywords sorted by frequency descending.
    """
    words_all = []

    for v in videos:
        try:
            views = int(v[2])  # index 2 = views según tu esquema
        except (TypeError, ValueError):
            continue

        if views > view_threshold:
            title = (v[1] or "").lower()  # index 1 = name (título)
            tokens = re.findall(r"\b[a-záéíóúñü]+\b", title)
            tokens = [t for t in tokens if t not in LATAM_SPANISH_STOPWORDS]
            words_all.extend(tokens)

    counter = Counter(words_all)
    filtered = [(w, f) for w, f in counter.items() if f >= min_freq]
    return sorted(filtered, key=lambda x: x[1], reverse=True)


def select_time_frame():
    """
    Prompts the user to select a time frame and returns the relevant date(s).
    """
    print("\nSelect the time frame:")
    print("1. By Day (Today, Yesterday, etc.)")
    print("2. By Range (Last 7 days, Last 14 days, Custom Range)")
    print("3. By Month (This Month, Last Month, Custom Month)")
    print("4. By Year (This Year, Last Year, Custom Year)")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("1. Today")
        print("2. Yesterday")
        print("3. Two Days Ago")
        print("4. Three Days Ago")
        print("5. Enter Specific Date")
        sub_choice = input("Select an option: ")

        if sub_choice == "1":
            return [datetime.now().strftime("%Y-%m-%d")]
        elif sub_choice == "2":
            return [(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")]
        elif sub_choice == "3":
            return [(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")]
        elif sub_choice == "4":
            return [(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")]
        elif sub_choice == "5":
            date = input("Enter the specific date (YYYY-MM-DD): ")
            return [date]

    elif choice == "2":
        print("1. Last 7 Days")
        print("2. Last 14 Days")
        print("3. Enter Custom Range")
        sub_choice = input("Select an option: ")

        if sub_choice == "1":
            return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        elif sub_choice == "2":
            return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]
        elif sub_choice == "3":
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]

    elif choice == "3":
        print("1. This Month")
        print("2. Last Month")
        print("3. Enter Custom Month")
        sub_choice = input("Select an option: ")

        if sub_choice == "1":
            today = datetime.now()
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
        elif sub_choice == "2":
            today = datetime.now()
            start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end = today.replace(day=1) - timedelta(days=1)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
        elif sub_choice == "3":
            month = input("Enter the month (YYYY-MM): ")
            start = datetime.strptime(month, "%Y-%m").replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]

    elif choice == "4":
        print("1. This Year")
        print("2. Last Year")
        print("3. Enter Custom Year")
        sub_choice = input("Select an option: ")

        if sub_choice == "1":
            today = datetime.now()
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
        elif sub_choice == "2":
            today = datetime.now()
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(year=today.year - 1, month=12, day=31)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
        elif sub_choice == "3":
            year = input("Enter the year (YYYY): ")
            start = datetime.strptime(year, "%Y").replace(month=1, day=1)
            end = datetime.strptime(year, "%Y").replace(month=12, day=31)
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]

    print("Invalid choice. Please try again.")
    return  []

def generate_table(
    data,
    columns,
    summary=False,
    period_label=None,
    channel_name=None,
    impact_view_threshold=3000,
    top_n_keywords=25
):
    """
    Generates a formatted table for display or reports.
    """
    from tabulate import tabulate

    if summary:
        # --- NUEVA sección: High-Impact Keywords (> X views) ---
        impact_keywords = extract_keywords_from_titles_over_views(
            data, view_threshold=impact_view_threshold, min_freq=2
        )
        impact_line = ", ".join(
            f"{w} (\033[92m{f}\033[0m)" for w, f in impact_keywords[:top_n_keywords]
        )

        print(f"\n\033[93m***REPORT***\033[0m")
        if period_label or channel_name:
            print(f"\033[90mPeriod:\033[0m {period_label or 'N/A'}", end="")
            if channel_name:
                print(f"   \033[90mChannel:\033[0m {channel_name}")
            else:
                print()

        print(f"\n\033[91mTotal videos:\033[0m  {len(data)}")
        # Promedios
        try:
            avg_views = sum(int(row[2]) for row in data if isinstance(row[2], (int, float, str))) / max(len(data), 1)
            print(f"\033[91mAverage Views:\033[0m  {avg_views:.2f}")
        except Exception as e:
            print(f"Error calculating average views: {e}")

        try:
            avg_likes = sum(int(row[3]) for row in data if str(row[3]).isdigit()) / max(len(data), 1)
            print(f"\033[91mAverage Likes:\033[0m  {avg_likes:.2f}")
        except Exception as e:
            print(f"Error calculating average likes: {e}")

        # Línea clave que pediste
        print(f"\n\033[96m🔥 High-Impact Keywords (>{impact_view_threshold} views):\033[0m {impact_line or '—'}")


    # Orden por views desc y render de tabla
    def _safe_views(x):
        try: return int(x[2])
        except: return -1
    data = sorted(data, key=_safe_views, reverse=True)

    table = [tuple(row[i] for i in columns) for row in data]
    print(tabulate(table, headers=["\033[94mDate", "Title", "Views\033[0m"], tablefmt="pretty",stralign="left",))
    input("\nPress Enter to return to the main menu...")
    
def make_period_label(dates):
    if not dates:
        return "—"

    sorted_dates = sorted(set(dates))
    if len(sorted_dates) == 1:
        return sorted_dates[0]

    start_s = sorted_dates[0]
    end_s = sorted_dates[-1]
    s = datetime.strptime(start_s, "%Y-%m-%d")
    e = datetime.strptime(end_s, "%Y-%m-%d")

    # ¿Mes completo?
    first = s.replace(day=1)
    next_month = (first + timedelta(days=32)).replace(day=1)
    last = next_month - timedelta(days=1)
    if s == first and e == last:
        # Usa nombres en inglés por defecto; si quieres español, coloca locale.
        return s.strftime("%B %Y")  # p.ej., "September 2025"

    # ¿Año completo?
    if s.month == 1 and s.day == 1 and e.month == 12 and e.day == 31 and s.year == e.year:
        return str(s.year)

    # Rango genérico
    return f"{start_s} → {end_s}"