from neo4j_interface.Neo4jDAO import Neo4jDAO

import json
import requests
import sys

# Step 2 imports
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Step 3 imports
import spacy
import classy_classification

# Functions for step 3: turning selected tuples to command
import random

# Gathering template <start> <number> <item to find> to make a <to make> from <location> <protected by?>
# Exploration template <start> <location> <optional: purpose>
# Combat template <start> <number> <enemy> <location> <item to retrieve>
gathering_start_words = ['Find', 'Gather', 'Collect', 'Retrieve', 'Get me', 'Bring back', 'Obtain', 'Get']
exploration_start_words = ['Go to', 'Visit', 'Go see', 'Travel to', 'Journey to', ' Explore']
combat_start_words = ['Fight', 'Slay', 'Kill', 'Defeat', 'Vanquish', 'Eliminate']
possible_relationships = ['located_in', 'has', 'protected_by'] # expand on this based on KG



# Imports for language model and processing quest
from transformers import pipeline

data = {
    "exploration": ["Where should I go for an adventure?",
               "Any recommendations of places to visit?",
               "I am new here and looking for somewhere to stay the night.",
               "What are some famous locations in this area?",
               "I love traveling to foreign countries!",
               "I hope I can visit that city someday."],
    "combat": ["Do you need help cleaning things up around here?",
                "I'm just itching to fight some bad guys!",
                "Anybody causing you trouble recently?",
               "Looks like you have a pest problem on your hand.",
               "Anything that needs killing around here?",
               "It looks like the giant spiders are causing a problem in the town."],
    "gathering": ["Do you need me to get something?",
                  "Is there something I can get you?",
                  "Anything you are missing?",
                  "Looks like you need some supplies.",
                  "I should get you some iron to make a sword",
                  "What else do you need me to get?"]
}

nlp = spacy.load('en_core_web_lg')
nlp.add_pipe("text_categorizer", 
    config={
        "data": data,
        "model": "spacy"
    }
)

# Class for storing nodes with properties and information with them.
class Neo_Node:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties

    def set_name(self, name):
        self.name = name

    def set_properties(self, properties):
        self.properties = properties

    def get_name(self):
        return self.name
        
    def get_properties(self):
        return self.properties


### TODO: Port all of this functionality to separate classes to keep main clean.
class QuestEngine:
    
    # Init function, open connection to Neo4J database
    def __init__(self):
        self.dao = Neo4jDAO(uri="neo4j+s://ecdeb551.databases.neo4j.io", user="neo4j", pwd="N4Qwx1-8GrA_Ik-LgwxwldF8TdUj_6rtWpKBKAtTxds")
        # Visit https://huggingface.co/models?sort=downloads&search=Dizzykong
        self.generator = pipeline('text-generation', model='Dizzykong/gpt2-medium-commands', tokenizer='Dizzykong/gpt2-medium-commands')

    # Functions for step 1: extracting and processing information from kg

    def verbalize_tuple(self, tuple_in):
        string = tuple_in[0].get_name() + " " + tuple_in[1] + " " + tuple_in[2].get_name()
        return string 


    def verbalize_tuple_2(self, tuple_in):
        string = tuple_in[0].get_properties()['name'] + " " + tuple_in[1] + " " + tuple_in[2].get_properties()['name']
        return string

    def extract_tuples(self, record):
        tup_vals = []

        for i, val in enumerate(record):
            if i == 1:
                relationship_type = val.type
                relationship_type = relationship_type.replace('_', " ")

                tup_vals.append(relationship_type)
            else:
                node_name = None
                for name in val.labels:
                    node_name = name

                node_properties = dict(val.items())
                node = Neo_Node(node_name, node_properties)

                tup_vals.append(node)
        
        return tuple(val for val in tup_vals)


    def extract_facts(self, res):
        all_facts = []

        for record in res:
            new_tup = self.extract_tuples(record)
            all_facts.append(new_tup)

        return all_facts


    def facts_to_strings(self, facts):
        fact_str = []

        for fact in facts:
            fact_str.append(self.verbalize_tuple_2(fact))

        return fact_str


    # Functions for step 2: similarity metrics between input and kg

    def cosine_similarity(self, user_string, facts_list):  

        cosine_scores = []
        X = user_string.lower()

        print("User string: ", X)

        for fact in facts_list:
            Y = fact.lower()

            print("Compared with: ", Y)
            X_list = word_tokenize(X)
            Y_list = word_tokenize(Y)

            sw = stopwords.words('english')
            l1 = []; l2 = []

            X_set = {w for w in X_list if not w in sw}
            Y_set = {w for w in Y_list if not w in sw}

            rvector = X_set.union(Y_set)

            for w in rvector:
                if w in X_set: 
                    l1.append(1) # create a vector
                else: 
                    l1.append(0)
                if w in Y_set: 
                    l2.append(1)
                else: 
                    l2.append(0)
            c = 0


            # cosine formula 
            for i in range(len(rvector)):
                c+= l1[i]*l2[i]

            cosine = c / float((sum(l1)*sum(l2))**0.5)

            cosine_scores.append(cosine)

        print(cosine_scores)
        print("Best match: ", facts_list[cosine_scores.index(max(cosine_scores))])

        return facts_list[cosine_scores.index(max(cosine_scores))], cosine_scores.index(max(cosine_scores))


    ### Functions for step 3
    def get_quest_type(self, user_input):
        doc = nlp(user_input)
        result_dict = doc._.cats
        classified_quest_type = max(result_dict, key=result_dict.get)

        return classified_quest_type 

    def find_connections(self, match_tuple):
        query_str = "match (n)-[r]->(m) return n,r,m"
        res = self.dao.query(query_str)

        # Get turn neo4j result into fact tuples in a list
        all_tuples = self.extract_facts(res)

        # Save and return all relevant information in string
        all_relevant_information = []
        all_relevant_information.append(self.verbalize_tuple_2(match_tuple))

        possible_tuples = []

        
        for tup in all_tuples:
            self.verbalize_tuple_2(tup)

            # iterate over each node
            for node in tup:

                # Skip relationship strings
                if type(node) == str:
                    continue

                # Find all outgoing connections from main quest node.
                if match_tuple[2].get_properties()['name'] == node.get_properties()['name']:
                    possible_tuples.append(tup)

        print("\nAll possible matches")
        for tup in possible_tuples:
            print(self.verbalize_tuple_2(tup))

        return possible_tuples
    
    def create_command(self, tuple_nodes, additional_tuples, classification="combat"):

        # Set up variables
        command_str = ""
        command_vals = []
        number_of = None

        # Get start based on classification
        if classification == 'gathering':
            start = random.choice(gathering_start_words)
            command_vals.append(start)

            # Get quest target to get number property
            quest_target = tuple_nodes[2]
            target_props = quest_target.get_properties()

            # TODO: Randomly generate number between 1 and number of for quest reqs
            if 'number_of' in target_props:
                number_of = target_props['number_of']

                number_of = random.randint(1, number_of // 3)

            # Append number to string
            if number_of is not None and number_of > 1:
                command_vals.append(str(number_of))

            # Append quest target value
            command_vals.append(quest_target.get_properties()['name'])

            loc_str = ""
            protect_str_str = ""

            # TODO: Simplify and make code more efficient
            for tup in additional_tuples:
                print(self.verbalize_tuple_2(tup))
                if tup[1] ==  'located in':
                    loc_str = 'located in ' + tup[2].get_properties()['name']
                elif tup[1] == 'protected by':
                    num = 0

                    # Get number of if there is property
                    if 'number_of' in tup[2].get_properties():
                        num = tup[2].get_properties()['number_of']
                        num = random.randint(1,num)

                    if num > 0:
                        if num == 1:
                            protect_str = 'which is protected by a ' + tup[2].get_properties()['name']
                        else:
                            protect_str = 'which is protected by ' + str(num) + " " + tup[2].get_properties()['name'] + "s"
                    else:
                        protect_str = 'which is protected by some ' + tup[2].get_properties()['name'] + "s"

            command_vals.extend(loc_str.split(' '))
            command_vals.extend(protect_str.split(' '))

        ## TODO: Implement exploration quests B)
        elif classification == 'exploration':
            start = random.choice(exploration_start_words)

        else: # Combat quests 
            # Get start word
            start = random.choice(combat_start_words)
            command_vals.append(start)

            # Get quest target to get number property
            quest_target = tuple_nodes[2]
            target_props = quest_target.get_properties()

            # TODO: Randomly generate number between 1 and number of for quest reqs
            if 'number_of' in target_props:
                number_of = target_props['number_of']
                number_of = random.randint(1, number_of)

            # Append number to string
            if number_of is not None and number_of > 1:
                command_vals.append(str(number_of))

            # Append quest target value
            command_vals.append(quest_target.get_properties()['name'])

            loc_str = ""
            has_str = ""

            # TODO: Simplify and make code more efficient
            for tup in additional_tuples:
                print(self.verbalize_tuple_2(tup))
                if tup[1] ==  'located in':
                    loc_str = 'located in ' + tup[2].get_properties()['name']
                elif tup[1] == 'has':
                    has_str = 'to obtain ' + str(tup[2].get_properties()['number_of']) + " " + tup[2].get_properties()['name']

            
            command_vals.extend(loc_str.split(' '))
            command_vals.extend(has_str.split(' '))

        command_str = " ".join(command_vals)
        print("Command out: ", command_str)

        return command_str


    # Core functionality. Takes in user input string and returns the final quest.
    def verbalize_command(self, user_input):
        print("User said: ", user_input)

        # Step 1: Query database for all information tuples marked for quests
        query_str = "match (n)-[r]->(m) where r.quest = true return n,r,m"
        res = self.dao.query(query_str)

        print(res)

        # Get turn neo4j result into fact tuples in a list
        facts = self.extract_facts(res)

        print("Facts found: ", facts)

        fact_strings = self.facts_to_strings(facts)
        print("Facts to strings: ", fact_strings)


        # Step 2: Get best match from similarity metric of best tuple to build command around
        # TODO: Maybe use multiple metrics to choose the best match?

        best_match, index = self.cosine_similarity(user_input, fact_strings)
        print("Best matching tuple: ", best_match)
        print("Index in list: ", facts[index])

        # Step 3: Turn tuples into command
        additional_information = self.find_connections(facts[index])
        print("Additional Tuples: ", additional_information)

        #Step 3a: Get quest classification
        quest_type = self.get_quest_type(user_input)
        print("Quest classified as: ", quest_type)

        # Get command string
        command = self.create_command(facts[index], additional_information, quest_type)

        print("Final command: ", command)

        return command # Command to return out

    def receive_input(self):
        print("Welcome to DRAGNTown Quest Generation Test\n")

        while True:
            user_in = input("Type something to get a quest for you!\n")
            
            # Handle quit ooption
            if user_in == "--quit" or user_in == "quit" or user_in == "q":
                self.dao.close()
                sys.exit("Closing server test. Thank you!")
            else: # Process input like normal 

                ## TODO: Needs error processing for bad inputs. What is bad input?

                ## Get quest command from KG
                quest_command = self.verbalize_command(user_in)

                # Generate quest output for user using language model
                prompt = quest_command + "<div>"
                sequences = self.generator(prompt, max_length=200, num_return_sequences=1)
                final_quest = sequences[0]['generated_text'].split("<eos>")[0]



                

                ## Return final quest to user
                print("FINAL QUEST: ", final_quest)

## TODO: Have the user select which NPC to talk to.
if __name__ == "__main__":
    console = QuestEngine()
    console.receive_input()