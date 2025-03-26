import sqlite3, csv, json, os

class Converter:
    def __init__(self, db_path, chunk_size=1000):
        self.db_path = db_path
        self.chunk_size = chunk_size

    def convert(self, table_name, output_format, output_folder, progress_callback=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = [c[1] for c in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        output_file = os.path.join(output_folder, f"{table_name}.{output_format}")
        if output_format == "txt":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\t".join(cols) + "\n")
                fetched = 0
                while True:
                    rows = cursor.fetchmany(self.chunk_size)
                    if not rows:
                        break
                    for r in rows:
                        f.write("\t".join(str(x) for x in r) + "\n")
                    fetched += len(rows)
                    if progress_callback:
                        progress_callback(int((fetched / total_rows) * 100))
        elif output_format == "csv":
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                fetched = 0
                while True:
                    rows = cursor.fetchmany(self.chunk_size)
                    if not rows:
                        break
                    writer.writerows(rows)
                    fetched += len(rows)
                    if progress_callback:
                        progress_callback(int((fetched / total_rows) * 100))
        elif output_format == "json":
            data = []
            fetched = 0
            while True:
                rows = cursor.fetchmany(self.chunk_size)
                if not rows:
                    break
                for r in rows:
                    data.append(dict(zip(cols, r)))
                fetched += len(rows)
                if progress_callback:
                    progress_callback(int((fetched / total_rows) * 100))
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif output_format == "html":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("<html><head><meta charset='utf-8'><title>")
                f.write(table_name)
                f.write("</title></head><body><table border='1'><tr>")
                for c in cols:
                    f.write(f"<th>{c}</th>")
                f.write("</tr>")
                fetched = 0
                while True:
                    rows = cursor.fetchmany(self.chunk_size)
                    if not rows:
                        break
                    for r in rows:
                        f.write("<tr>")
                        for x in r:
                            f.write(f"<td>{x}</td>")
                        f.write("</tr>")
                    fetched += len(rows)
                    if progress_callback:
                        progress_callback(int((fetched / total_rows) * 100))
                f.write("</table></body></html>")
        conn.close()

    def get_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        return tables
