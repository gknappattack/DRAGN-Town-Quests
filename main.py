# ONLY NEEDED ON SETUP 
#import nltk
#nltk.download('stopwords')
#nltk.download('punkt')

from neo4j_interface.Neo4jDAO import Neo4jDAO
from ngram import NgramModel

import json
import requests
import sys
from datetime import datetime

# Step 2 imports
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Step 3 imports
import spacy
import classy_classification
import re

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
from transformers.utils import logging

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


def create_ngram_model(n, path):
    m = NgramModel(n)
    with open(path, 'r') as f:
        text = f.read()
        text = text.split('.')
        for sentence in text:
            # add back the fullstop
            sentence += '.'
            m.update(sentence)
    return m

# Class for storing nodes with properties and information with them.
class Neo_Node:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.type = None

    def set_name(self, name):
        self.name = name

    def set_type(self, type):
        self.type = type

    def set_properties(self, properties):
        self.properties = properties

    def get_name(self):
        return self.name
        
    def get_properties(self):
        return self.properties
    
    def get_type(self):
        return self.type


### TODO: Port all of this functionality to separate classes to keep main clean.
class QuestEngine:
    
    # Init function, open connection to Neo4J database
    def __init__(self):
        self.dao = Neo4jDAO(uri="neo4j+s://ecdeb551.databases.neo4j.io", user="neo4j", pwd="N4Qwx1-8GrA_Ik-LgwxwldF8TdUj_6rtWpKBKAtTxds")
        # Visit https://huggingface.co/models?sort=downloads&search=Dizzykong
        self.generator = pipeline('text-generation', model='Dizzykong/gpt2-medium-commands', tokenizer='Dizzykong/gpt2-medium-commands')

    # Functions for step 1: extracting and processing information from kg


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

        #print("User string: ", X)

        for fact in facts_list:
            Y = fact.lower()

            #print("Compared with: ", Y)
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

        #print("Best match: ", facts_list[cosine_scores.index(max(cosine_scores))])

        if max(cosine_scores) == 0:
            rand_idx = random.randrange(len(cosine_scores))

            return facts_list[rand_idx], rand_idx, cosine_scores


        return facts_list[cosine_scores.index(max(cosine_scores))], cosine_scores.index(max(cosine_scores)), cosine_scores


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

        '''
        print("\nAll possible matches")
        for tup in possible_tuples:
            print(self.verbalize_tuple_2(tup))
        '''

        return possible_tuples
    
    def create_command(self, tuple_nodes, additional_tuples, classification="combat"):

        # Set up variables
        command_str = ""
        command_vals = []
        number_of = None

        loc_str = ""
        protect_str = ""
        object_str = ""

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

                #number_of = random.randint(1, number_of // 3) ####### WAS BREAKING THINGS

            # Append number to string
            if number_of is not None and number_of > 1:
                command_vals.append(str(number_of))

            # Append quest target value
            command_vals.append(quest_target.get_properties()['name'])

            for tup in additional_tuples:
                #print(self.verbalize_tuple_2(tup))
                if tup[2].get_name() ==  'Location':
                    loc_str = 'located in ' + tup[2].get_properties()['name']
                elif tup[2].get_name() == 'Enemy':
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
                elif tup[2].get_name() == 'Object':
                    object_str = "to create " + tup[2].get_properties()['name']


            command_vals.extend(loc_str.split(' '))
            command_vals.extend(protect_str.split(' '))
            command_vals.extend(object_str.split(' '))

        ## TODO: Implement exploration quests B)
        elif classification == 'exploration':
            start = random.choice(exploration_start_words)
            command_vals.append(start)

            # Get quest target to get number property
            quest_target = tuple_nodes[2]
            command_vals.append(quest_target.get_properties()['name'])

            has_str = ""

            # TODO: Simplify and make code more efficient
            for tup in additional_tuples:
                #print(self.verbalize_tuple_2(tup))

                if tup[2].get_name() ==  'Location':       
                    loc_str = 'located in ' + tup[2].get_properties()['name']
                elif tup[2].get_name() == 'Object':
                    has_str = 'and bring back ' + str(tup[2].get_properties()['number_of']) + " " + tup[2].get_properties()['name']
                elif tup[0].get_name() == 'Object':
                    has_str = 'and bring back ' +str(tup[0].get_properties()['name']) + " "  + tup[1] + " " + tup[2].get_properties()['name']

            
            command_vals.extend(loc_str.split(' '))
            command_vals.extend(has_str.split(' '))

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
                #print(self.verbalize_tuple_2(tup))

                if tup[2].get_name() ==  'Location':       
                    loc_str = 'located in ' + tup[2].get_properties()['name']
                elif tup[2].get_name() == 'Object':
                    has_str = 'to obtain ' + str(tup[2].get_properties()['number_of']) + " " + tup[2].get_properties()['name']
                elif tup[0].get_name() == 'Object':
                    has_str = 'to obtain ' +str(tup[0].get_properties()['name']) + " "  + tup[1] + " " + tup[2].get_properties()['name']

            
            command_vals.extend(loc_str.split(' '))
            command_vals.extend(has_str.split(' '))

        command_str = " ".join(command_vals)

        return command_str


    # Core functionality. Takes in user input string and returns the final quest.
    def verbalize_command(self, user_input, log):
        #print("User said: ", user_input)

        # Step 1: Query database for all information tuples marked for quests
        query_str = "match (n)-[r]->(m) where r.quest = true return n,r,m"
        res = self.dao.query(query_str)

        # Get turn neo4j result into fact tuples in a list
        facts = self.extract_facts(res)

        fact_strings = self.facts_to_strings(facts)
        #print("Facts to strings: ", fact_strings)


        # Step 2: Get best match from similarity metric of best tuple to build command around
        # TODO: Maybe use multiple metrics to choose the best match?

        best_match, index, cosine = self.cosine_similarity(user_input, fact_strings)
        #print("Best matching tuple: ", best_match)

        # Step 3: Turn tuples into command
        additional_information = self.find_connections(facts[index])
        #print("Additional Tuples: ", additional_information)

        #Step 3a: Get quest classification
        quest_type = self.get_quest_type(user_input)
        #print("Quest classified as: ", quest_type)

        # Get command string
        command = self.create_command(facts[index], additional_information, quest_type)

        #print("Final command: ", command)

        if log is not None:
            nl = '\n'
            log.write(f"{nl}User said: {user_input}")
            log.write(f"{nl}Fact strings: {fact_strings}")
            log.write(f"{nl}Cosine Similarity Scores: {cosine}")
            log.write(f"{nl}Best matching tuples: {best_match}")
            log.write(f"{nl}Additional Tuples: {additional_information}")
            log.write(f"{nl}Quest classified as: {quest_type}")
            log.write(f"{nl}Final command out: {command}")


        return command # Command to return out

    def choose_random_wow_qtd(self):
        # CHOOSE A RANDOM WOW QUEST
        wow_lines = open('./wow_v2_cleaned.tsv', 'r').readlines()
        rand_quest_idx = random.randint(0, len(wow_lines)-1)
        wow_quest = wow_lines[rand_quest_idx].split('\t')
        wow_quest[0]= re.sub('([.,!?()])', r' \1 ', wow_quest[0])
        wow_quest[0] = re.sub('\s{2,}', ' ', wow_quest[0])
        wow_quest[1]= re.sub('([.,!?()])', r' \1 ', wow_quest[1])
        wow_quest[1] = re.sub('\s{2,}', ' ', wow_quest[1])
        wow_quest[2]= re.sub('([.,!?()])', r' \1 ', wow_quest[2])
        wow_quest[2] = re.sub('\s{2,}', ' ', wow_quest[2])

        #wow_quest_final = "\n\tQuest: {}\n\tTitle: {}\n\tDialogue: {}".format(wow_quest[0], wow_quest[1], wow_quest[2])
        wow_quest_final = "Quest: {}|Title: {}|Dialogue: {}".format(wow_quest[0], wow_quest[1], wow_quest[2])
        return wow_quest_final

    def generate_gpt2_qtd(self, quest_command):
        # Generate quest output for user using language model
        prompt = quest_command + "<div>"
        sequences = self.generator(prompt, max_length=200, num_return_sequences=1)
        final_quest = sequences[0]['generated_text'].split("<eos>")[0]

        final_quest = re.sub('([.,!?()])', r' \1 ', final_quest)
        final_quest = re.sub('\s{2,}', ' ', final_quest)

        split_final_quest = final_quest.split('<div>')

        #final_quest = "\n\tQuest: {}\n\tTitle: {}\n\tDialogue: {}".format(split_final_quest[0], split_final_quest[1], split_final_quest[2])
        final_quest = "Quest: {}|Title: {}|Dialogue: {}".format(split_final_quest[0], split_final_quest[1], split_final_quest[2])
        final_quest = re.sub('George', 'Player', final_quest)
        return final_quest

    def generate_ngram_qtd(self, user_in, m):
        # Generate and save n-gram quest
        # Grab a random quest prompt for n-gram model
        ngram_prompt_options = ["explore", "gather", "attack", "defend", "search", "destroy", "mine", "hunt", "help", "craft", "create", "build"]
        input_trigger = False
        trigger_word = None
        for word in user_in.split(' '):
            if word.lower() in ngram_prompt_options:
                input_trigger = True
                trigger_word = word
        if input_trigger == True:
            ngram_input = trigger_word
        else:
            ngram_input = ngram_prompt_options[random.randint(0,len(ngram_prompt_options)-1)]
        n_gram_quest = m.generate_text(60, ngram_input[0].upper() + ngram_input[1:])
        
        ngram_quest = ""
        ngram_title = ""
        ngram_dialogue = ""
        ngram_parser_mode = 0
        for idx in range(len(n_gram_quest)):
            # append to quest
            if ngram_parser_mode == 0:
                ngram_quest += n_gram_quest[idx]
                if n_gram_quest[idx] == ".":
                    ngram_parser_mode += 1
                    ngram_quest += '.'
            # append to title
            elif ngram_parser_mode == 1:
                ngram_title += n_gram_quest[idx]
                if n_gram_quest[idx] == "." and len(ngram_title) > 4:
                    ngram_parser_mode += 1
                    #ngram_title += '.'
            # append to dialogue
            else:
                ngram_dialogue += n_gram_quest[idx]

        #n_gram_quest2 = "\n\tQuest: {}\n\tTitle: {}\n\tDialogue: {} .".format(ngram_quest, ngram_title, ngram_dialogue)
        n_gram_quest2 = "Quest: {}|Title: {}|Dialogue: {} .".format(ngram_quest, ngram_title, ngram_dialogue)
        n_gram_quest2 = re.sub('George', 'Player', n_gram_quest2)

        return n_gram_quest2
    

    def receive_input_API(self, user_in, logging=False):
        if logging: 
            ## Get inputs for logging file
            file_name = ''

            #mod_name = input("Test Moderator, please type your name: ")
            #user_name = input("Type the name of the participant: ")

            date = datetime.now()
            curr_date_time = date.strftime("%d_%b_%Y_(%H_%M_%S_%f)")

            #file_name = 'DRAGN-Town-Quests/response_logs/' + mod_name + "_" + user_name + "_" + curr_date_time + ".txt"

            log = open(file_name, "w")
            log.write("")
        else:
            log = None

        # initialize n-gram model
        m = create_ngram_model(4, './wow_v2_cleaned.tsv')
        random.seed(datetime.now())

        #quests = []

        ## GPT-2
        quest_command = self.verbalize_command(user_in, log)
        final_quest = self.generate_gpt2_qtd(quest_command)
        #quests.append(final_quest)

        # N-GRAM
        n_gram_quest2 = self.generate_ngram_qtd(user_in, m)
        #quests.append(n_gram_quest2)

        # WOW
        wow_quest_final = self.choose_random_wow_qtd()
        #quests.append(wow_quest_final)

        # Present both options to the user in a randomized order
        #idx_list = [quests.index(q) for q in quests]
        #random.shuffle(idx_list)
        gp = final_quest.split('|')
        ng = n_gram_quest2.split('|')
        wow = wow_quest_final.split('|')

        key = {"p1":"gp2", "p2":"ngram", "p3":"wow"}

        res = {
            #"from":json_data["name"],
            #"said":json_data["data"]
            # gpt2
            "p1": {"quest":gp[0], "title":gp[1], "dialogue":gp[2]},
            # ngram
            "p2": {"quest":ng[0], "title":ng[1], "dialogue":ng[2]},
            # wow
            "p3": {"quest":wow[0], "title":wow[1], "dialogue":wow[2]},
            "key": key
        }

        #print('finalquest: ', final_quest)
        #print('gp: ', gp)

        # Close dao and file
        self.dao.close()

        if log is not None:
            log.close()

        #sys.exit()
        return res


    def receive_input(self, logging=True):

        if logging: 
            ## Get inputs for logging file
            file_name = ''

            mod_name = input("Test Moderator, please type your name: ")
            user_name = input("Type the name of the participant: ")

            date = datetime.now()
            curr_date_time = date.strftime("%d_%b_%Y_(%H_%M_%S_%f)")

            file_name = './response_logs/' + mod_name + "_" + user_name + "_" + curr_date_time + ".txt"

            log = open(file_name, "w")
            log.write("")
        else:
            log = None

        print("\nWelcome to DRAGNTown Quest Generation Test\n")
        num_quest = int(input("How many prompts will be done: "))

        complete_quests = 0


        # initialize n-gram model
        m = create_ngram_model(4, './wow_v2_cleaned.tsv')
        random.seed(datetime.now())


        while complete_quests < num_quest:
            user_in = input("\nType something to get a quest for you!\n")
            
            # Handle quit option
            if user_in == "--quit" or user_in == "quit" or user_in == "q":
                self.dao.close()
                sys.exit("Closing server test. Thank you!")
            else: # Process input like normal 
                nl = '\n'
                print(f"{nl}Sample Quest #{complete_quests+1}")

                if logging:
                    log.write(f"Sample Quest #{complete_quests+1}")

                quests = []

                ## GPT-2
                quest_command = self.verbalize_command(user_in, log)
                final_quest = self.generate_gpt2_qtd(quest_command)
                quests.append(final_quest)

                ## N-GRAM
                n_gram_quest2 = self.generate_ngram_qtd(user_in, m)
                quests.append(n_gram_quest2)

                ## WOW
                wow_quest_final = self.choose_random_wow_qtd()
                quests.append(wow_quest_final)

                # Present both options to the user in a randomized order
                idx_list = [quests.index(q) for q in quests]
                random.shuffle(idx_list)

                for i, index in enumerate(idx_list):
                    out_string = f"{nl}Option {i}: {quests[index]}"
                    print(out_string)

                    if logging: 
                        log.write(f"{nl}{out_string}")
                        log.write(f"{nl}Generation method: {index} (0 = DRAGN-Town, 1 = N-Gram, 2 = WoW){nl}")

                user_selected = input("\nWhich quest is most satisfying to you? ")
                
                if logging:
                    log.write("\nWhich quest is most satisfying to you?\n")
                    log.write(f'User selected option #{user_selected}')
                    log.write("\n")

                user_selected = input("\nWhich quest was most responsive to your input? ")
                
                if logging:
                    log.write("\nWhich quest was most responsive to your input?\n")
                    log.write(f'User selected option #{user_selected}')
                    log.write("\n")

                user_thoughts = input("\nWhat was your experience with each quest? What did you like/dislike about each one? Please respond in a short paragraph.\n")

                if logging:
                    log.write("\nWhat was your experience with each quest?\n")
                    log.write(f'User responded: {user_thoughts}')
                    log.write("\n")

                print("============================")

                if logging:
                    log.write("\n===========================\n")
                
                complete_quests += 1


        print("\n\nThank you for participating in this survey!!")

        # Close dao and file
        self.dao.close()

        if log is not None:
            log.close()

        sys.exit()




## TODO: NPC selection? (SCOPED OUT FOR NOW)
if __name__ == "__main__":
    logging.set_verbosity_error()

    console = QuestEngine()
    console.receive_input(True) # Toggle logging on and off.




## TODO List
#
# 4. clean up templates, expand on them. IF THERES TIME: randomly select location node - put into an array of location strings, randomly choose one?
# 6. Add more examples to the 0-shot classification to improve performance.
#
#
