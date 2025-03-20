from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import os
import datetime
import requests
import threading

# XML file path
XML_FILE = "notebook.xml"

# Create XML file if it doesn't exist
def initialize_xml():
    if not os.path.exists(XML_FILE):
        root = ET.Element("notebook")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE)
        print(f"Created new XML file: {XML_FILE}")
    else:
        print(f"Using existing XML file: {XML_FILE}")

# XML file lock for thread safety
xml_lock = threading.Lock()

# Function to add a note to the XML database
def add_note(topic, text, timestamp=None):
    with xml_lock:
        if not timestamp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Parse the XML file
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            # Check if topic exists
            topic_element = None
            for elem in root.findall("topic"):
                if elem.get("name") == topic:
                    topic_element = elem
                    break
            
            # If topic doesn't exist, create it
            if topic_element is None:
                topic_element = ET.SubElement(root, "topic", name=topic)
            
            # Add the note to the topic
            note = ET.SubElement(topic_element, "note")
            note.set("timestamp", timestamp)
            note.text = text
            
            # Save the changes
            tree.write(XML_FILE)
            print(f"Added note to topic '{topic}'")
            return f"Note added successfully to topic '{topic}'"
        except Exception as e:
            print(f"Error adding note: {e}")
            return f"Error adding note: {e}"

# Function to get notes for a specific topic
def get_notes(topic):
    with xml_lock:
        try:
            # Parse the XML file
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            # Find the topic
            for topic_element in root.findall("topic"):
                if topic_element.get("name") == topic:
                    notes = []
                    for note in topic_element.findall("note"):
                        notes.append({
                            "timestamp": note.get("timestamp"),
                            "text": note.text
                        })
                    print(f"Retrieved {len(notes)} notes for topic '{topic}'")
                    return notes
            
            print(f"No notes found for topic '{topic}'")
            return []  # Return empty list if topic not found
        except Exception as e:
            print(f"Error getting notes: {e}")
            return []

# Function to search Wikipedia for a topic
def search_wikipedia(topic):
    try:
        print(f"Searching Wikipedia for: {topic}")
        # Use the Wikipedia API to search for the topic
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Extract the relevant information
        if len(data) >= 4 and len(data[1]) > 0:
            title = data[1][0]
            link = data[3][0]
            
            # Get a summary of the article
            summary_params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
            }
            
            summary_response = requests.get(url, params=summary_params)
            summary_data = summary_response.json()
            
            # Extract the page ID and summary
            page_id = next(iter(summary_data["query"]["pages"]))
            if "extract" in summary_data["query"]["pages"][page_id]:
                summary = summary_data["query"]["pages"][page_id]["extract"]
                # Limit summary to first paragraph
                summary = summary.split("\n")[0]
            else:
                summary = "No summary available."
            
            print(f"Found Wikipedia article: {title}")
            return {
                "title": title,
                "link": link,
                "summary": summary
            }
        else:
            print(f"No Wikipedia results found for '{topic}'")
            return {"error": "No results found"}
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return {"error": f"Error: {str(e)}"}

# Function to add Wikipedia information to a topic
def add_wikipedia_info(topic, search_term=None):
    if not search_term:
        search_term = topic
    
    wiki_info = search_wikipedia(search_term)
    
    if "error" in wiki_info:
        return wiki_info
    
    # Format the note text
    note_text = f"Wikipedia: {wiki_info['title']}\nLink: {wiki_info['link']}\nSummary: {wiki_info['summary']}"
    
    # Add the note to the topic
    result = add_note(topic, note_text)
    
    return {"success": True, "wiki_info": wiki_info, "message": result}

def main():
    # Initialize the XML file
    initialize_xml()
    
    # Create the server
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Server started on port 8000...")
    
    # Register functions
    server.register_function(add_note, "add_note")
    server.register_function(get_notes, "get_notes")
    server.register_function(search_wikipedia, "search_wikipedia")
    server.register_function(add_wikipedia_info, "add_wikipedia_info")
    
    # Register introspection functions (IMPORTANT ADDITION)
    server.register_introspection_functions()
    
    # List available methods
    print("Available methods:")
    for method in server.system_listMethods():
        print(f"- {method}")
    
    # Start the server
    try:
        print("Server running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")

if __name__ == "__main__":
    main()