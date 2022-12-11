import tkinter as tk
from tkinter import ttk
from arango import ArangoClient
import hashlib

def findRelation():
    character1 = character_selection.get()
    character2 = character2_selection.get()
    # print(character1)
    # print(character2)
    for character in characterCollection.all():
        if character['name'] == character1:
            id1 = character['_id']
            # print(id1)
        if character['name'] == character2:
            id2 = character['_id']
    result = sys_db.graph('test').traverse(
    start_vertex=id1,
    direction='outbound',
    strategy='bfs',
    edge_uniqueness='global',
    vertex_uniqueness='global',
)
    #print(result)
    found = False
    for elem in result['vertices']:
        if elem['_id'] == id2:
            found = True
            break
    
    if not(found):
        label.config(text="No relation found")
        label.config(fg='red')
    else:
        label.config(text="Relation found")
        label.config(fg='green')

    cursor = sys_db.aql.execute(f"FOR v, e IN OUTBOUND SHORTEST_PATH '{id1}' TO '{id2}' GRAPH 'test' RETURN [v.name, e.relation]")
    if (len(frames) > 0):
        frames[0].destroy()
        frames.clear()
    frame = tk.Frame(master=window, relief=tk.RAISED, borderwidth=1)
    i = 0
    for elem  in cursor:
        if (i == 0):
            i+=1
            continue
        for j in range(2):
            frameGrid = tk.Frame(
            master=frame,
            relief=tk.FLAT,
            borderwidth=2
            )
            frameGrid.grid(row=i, column=j)
            if (j == 0):
                labelGrid = tk.Label(master=frameGrid, text=elem[0])
            else:
                labelGrid = tk.Label(master=frameGrid, text=elem[1])
            #labelGrid = tk.Label(master=frameGrid, text=f"Row No. {x}\nColumn No. {y}")
            labelGrid.pack()
            #print(i)
        i+=1

    frame.pack()
    frames.append(frame)




# when the button is clicked, the number is added to the variable id and the status is displayed as a label
def confirm():
    # get the id from the selected character
    character_name = character_selection.get()

    for character in characterCollection.all():
        if character['name'] == character_name:
            id = character['_key']

    character_status = characterCollection[id]['status']
    if character_status:
        label.config(text="royal")
        label.config(fg='green')
    else :
        label.config(text="not royal")
        label.config(fg='red')
    # update the label
    label.update()


# create a tkinter window
window = tk.Tk()
window.title('Family Tree')
window.geometry('500x800')

#data entry for connection
tk.Label(window, text='User').pack()
user = tk.Entry(window)
user.pack()

tk.Label(window, text='Password').pack()
password = tk.Entry(window, show='*')
password.pack()

tk.Label(window, text='Database').pack()
database = tk.Entry(window)
database.pack()

connect = tk.Button(window, text='Connect')
connect.pack()

def connectToDB():
    user_d = user.get()
    password_d = password.get()
    database_d = database.get()
    global client
    global sys_db
    client = ArangoClient(hosts='http://localhost:8529')
    sys_db = client.db(database_d, username=user_d, password=password_d)

    if sys_db.has_collection('character'):
        global characterCollection
        characterCollection = sys_db.collection('character')
    else:
        print("character Collection does not exist")
        quit()
    if sys_db.has_collection('character'):
        global linkCollection
        linkCollection = sys_db.collection('link')
    else:
        print("link Collection does not exist")
        quit()


    #get all the characters
    characters = characterCollection.all()



    #create a list of all the characters names
    global character_names
    character_names = []

    for character in characters:
        #print(character)
        character_names.append(character['name'])

    separator = ttk.Separator(window, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)

    # create a combobox with all the characters names
    global character_selection
    character_selection = ttk.Combobox(window, values=character_names)
    character_selection.pack()

    # add a confirmation button
    confirm_button = tk.Button(window, text='Is royal?')
    confirm_button.pack()


    # add a button to look for consanguinity
    consanguinity_button = tk.Button(window, text='check inbreeding')
    consanguinity_button.pack()

    # create a combobox with all the characters names
    global character2_selection
    character2_selection = ttk.Combobox(window, values=character_names)
    character2_selection.pack()

    # add a button to look for shortest path
    shortest_path_button = tk.Button(window, text='Find blood relation')
    shortest_path_button.pack()

    # add a label to display the status
    global label
    label = tk.Label(window, text="Please select a character")
    label.pack()
    confirm_button.config(command=confirm)
    
    consanguinity_button.config(command=check_consanguinity)
    
    shortest_path_button.config(command=findRelation)

    #code for the insert 
    
    separator = ttk.Separator(window, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)

    #data entry for connection
    tk.Label(window, text='New character').pack()
    global new_character
    new_character = tk.Entry(window)
    new_character.pack()

    global royal
    royal = tk.IntVar()

    c1 = tk.Checkbutton(window, text='Royalty',variable=royal, onvalue=True, offvalue=False)
    c1.pack()



    tk.Label(window, text='relation').pack()
    global relation_selection
    relation_selection = ttk.Combobox(window, values=["parents", "parentOf", "marriedEngaged", "siblings"])
    relation_selection.pack()


    tk.Label(window, text='to').pack()
    global character3_selection
    character3_selection = ttk.Combobox(window, values=character_names)
    character3_selection.pack()

    insert_button = tk.Button(window, text='Insert')
    insert_button.pack()
    insert_button.config(command=insert)

    separator = ttk.Separator(window, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)

connect.config(command=connectToDB)

frames = []

def check_consanguinity():
    character1 = character_selection.get()
    for character in characterCollection.all():
        if character['name'] == character1:
            id = character['_id']
    graph = sys_db.graph('test')
    parents = []
    for elem in graph.edges('link',id)['edges']:
        if elem['relation'] == 'parents' and elem['_from'] == id:
            parents.append(elem['_to'])

    relations = []
    if len(parents) >= 2:
        edges = graph.edges('link',parents[-2])['edges']
        for elem in edges:
            if elem['_to'] == parents[-1]:
                relations.append(elem['relation'])
    print(relations)
    if len(relations) == 0 or len(parents)<2:
        label.config(text="Not enough data")
        label.config(fg='red')
    elif 'siblings' in relations and 'marriedEngaged' not in relations:
        label.config(text="inbred + bastard")
        label.config(fg='green')
    elif 'siblings' in relations and 'marriedEngaged' in relations:
        label.config(text="inbred")
        label.config(fg='green')
    elif 'marriedEngaged' not in relations:
        label.config(text="Bastard")
        label.config(fg='green')
    else:
        label.config(text="non inbred child born in wedlock")
        label.config(fg='red')
    

def insert():
    character1 = new_character.get()
    relation = relation_selection.get()
    character2 = character3_selection.get()
    id1 = abs(hash(character1)) % (10 ** 8)
    print(id1)

    id1 = int(hashlib.sha256(character1.encode('utf-8')).hexdigest(), 16) % 10**8
    if character1 not in character_names:
        print({"_key": id1, "name": character1, "status": royal})
        characterCollection.insert({"_key": str(id1), "name": character1, "status": royal.get()})
        character_names.append(character1)
    else:
        print("character already exists")

    for character in characterCollection.all():
        if character['name'] == character2:
            id2 = character['_id']
    key = int(hashlib.sha256((character1+character2+relation).encode('utf-8')).hexdigest(), 16) % 10**8
    for elem in linkCollection.all():
        if elem['_key'] == str(key):
            print("link already exists")
            return
    linkCollection.insert({"_key": str(key), "_from": "character/"+str(id1), "_to": id2, "relation": relation})
    print("inserted link")


# display the window
window.mainloop()


