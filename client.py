import xmlrpc.client
import datetime
import sys

def display_menu():
    print("\n==== Notebook RPC Client ====")
    print("1. Add a note")
    print("2. Get notes for a topic")
    print("3. Search Wikipedia and add info to a topic")
    print("4. Exit")
    return input("Choose an option (1-4): ")

def add_note(proxy):
    topic = input("Enter topic: ")
    text = input("Enter note text: ")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        result = proxy.add_note(topic, text, timestamp)
        if result:
            print("Note added successfully!")
        else:
            print("Failed to add note.")
    except Exception as e:
        print(f"Error: {e}")

def get_notes(proxy):
    topic = input("Enter topic to retrieve: ")
    
    try:
        notes = proxy.get_notes(topic)
        
        if notes:
            print(f"\nNotes for topic '{topic}':")
            for i, note in enumerate(notes, 1):
                print(f"{i}. [{note['timestamp']}] {note['text']}")
        else:
            print(f"No notes found for topic '{topic}'.")
    except Exception as e:
        print(f"Error: {e}")

def search_wikipedia(proxy):
    topic = input("Enter existing topic to add Wikipedia info to: ")
    search_term = input("Enter search term for Wikipedia (leave blank to use topic name): ")
    
    if not search_term:
        search_term = topic
    
    try:
        result = proxy.add_wikipedia_info(topic, search_term)
        
        if "success" in result:
            print("Wikipedia information added successfully!")
            print(f"Title: {result['wiki_info']['title']}")
            print(f"Link: {result['wiki_info']['link']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Connect to the server
    try:
        proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
        print("Connected to server.")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            add_note(proxy)
        elif choice == "2":
            get_notes(proxy)
        elif choice == "3":
            search_wikipedia(proxy)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()