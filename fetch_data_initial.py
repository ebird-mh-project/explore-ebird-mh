import subprocess

months_2025 = [
    "January_2025","February_2025","March_2025","April_2025",
    "May_2025","June_2025","July_2025","August_2025",
    "September_2025","October_2025","November_2025","December_2025"
]

extra = ["January_2026", "February_2026"]

all_months = months_2025 + extra

for m in all_months:
    print(f"Running fetch for {m}")
    subprocess.run(["python", "fetch_data.py", m])
