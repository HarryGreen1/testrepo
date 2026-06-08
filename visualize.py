import json
import matplotlib.pyplot as plt

# --- 1. Ladda in datan ---
try:
    with open("github_data.json", "r", encoding="utf-8") as file:
        commits = json.load(file)
except FileNotFoundError:
    print("Kunde inte hitta github_data.json. Har du kört main.py först?")
    exit()

# --- 2. Bearbeta datan ---
# Vi skapar en ordbok (dictionary) för att räkna commits per person
author_counts = {}

for item in commits:
    # Leta upp författarens namn i JSON-strukturen
    author = item['commit']['author']['name']
    
    # Räkna upp
    if author in author_counts:
        author_counts[author] += 1
    else:
        author_counts[author] = 1

# --- 3. Förbered data för diagrammet ---
authors = list(author_counts.keys())
counts = list(author_counts.values())

# --- 4. Rita diagrammet ---
plt.figure(figsize=(10, 6)) # Bestäm storlek på fönstret
plt.bar(authors, counts, color='#1f77b4') # Skapa stapeldiagram

# Lägg till titlar och text
plt.title("Aktivitet i Sandbox: Commits per utvecklare", fontsize=16)
plt.xlabel("Utvecklare", fontsize=12)
plt.ylabel("Antal Commits", fontsize=12)

# Se till att Y-axeln bara visar hela siffror (man kan inte göra 1.5 commits)
if counts:
    plt.yticks(range(0, max(counts) + 2))

# Visa grafen på skärmen!
print("Öppnar diagrammet...")
plt.show()