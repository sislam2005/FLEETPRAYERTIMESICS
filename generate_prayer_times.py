import requests
import json
from ics import Calendar, Event
from datetime import datetime, timedelta
import os
from git import Repo

# Fleet, UK Coordinates
LAT = 51.285
LON = -0.833
TIMEZONE = "Europe/London"
YEAR = datetime.now().year

# Backup Moonsighting API URL
BACKUP_API_URL = f"https://moonsighting.ahmedbukhamsin.sa/time_json.php?year={YEAR}&tz={TIMEZONE}&lat={LAT}&lon={LON}&method=0&both=false&time=0"

# GitHub repository details
GITHUB_REPO_PATH = "/path/to/your/local/repo"  # Your local repository path where the ICS file will be saved
GITHUB_TOKEN = "your_github_token"  # Personal Access Token for GitHub
GITHUB_REPO_URL = "https://github.com/yourusername/yourrepo.git"

# User-Agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_prayer_times():
    """Fetch prayer times from the backup Moonsighting API"""
    try:
        response = requests.get(BACKUP_API_URL, headers=headers)
        response.raise_for_status()

        # Try to parse the response as JSON
        data = response.json()

        # Check for the correct structure in the response
        if "times" not in data:
            print("⚠️ Unexpected API response:", data)
            return None

        return data["times"]  # List of prayer times for each day

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching prayer times: {e}")
        return None

def generate_ics(prayer_times):
    """Generate ICS calendar from prayer times"""
    cal = Calendar()

    for day_entry in prayer_times:
        day = day_entry["day"]
        date_str = f"{YEAR}-{day.split()[0]}-{day.split()[1]}"

        times = day_entry["times"]
        for prayer, time in times.items():
            if time.strip():  # Ensure the time string is not empty
                # Create a datetime object and format it in ISO 8601
                prayer_time = f"{date_str} {time.strip()}"
                try:
                    event_time = datetime.strptime(prayer_time, "%Y-%b-%d %H:%M").isoformat()
                except ValueError:
                    print(f"⚠️ Invalid time format: {prayer_time}")
                    continue

                event = Event()
                event.name = f"{prayer} Prayer"
                event.begin = f"{event_time}+00:00"  # Add timezone offset
                event.duration = timedelta(minutes=15)  # 15-min event
                cal.events.add(event)

    # Save to ICS file
    file_name = f"prayer_times_{YEAR}.ics"
    with open(file_name, "w") as f:
        f.writelines(cal)

    print(f"✅ ICS file generated: {file_name}")
    return file_name

def push_to_github(file_path):
    """Push ICS file to GitHub"""
    try:
        repo = Repo(GITHUB_REPO_PATH)
        repo.git.add(file_path)  # Add ICS file to staging
        repo.git.commit("-m", f"Add prayer times for {YEAR}")  # Commit the file
        repo.git.push()  # Push changes to GitHub
        print(f"✅ ICS file pushed to GitHub successfully!")
    except Exception as e:
        print(f"❌ Error pushing to GitHub: {e}")

def main():
    prayer_times = get_prayer_times()
    if prayer_times:
        file_name = generate_ics(prayer_times)
        push_to_github(file_name)
    else:
        print("❌ Could not fetch prayer times.")

if __name__ == "__main__":
    main()
