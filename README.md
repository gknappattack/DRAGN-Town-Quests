# DRAGN-Town-Quests

Code for Brigham Young University's DRAGN Lab (https://dragn.ai/#navigation) submission for the CHI 2023 conference on Computer and Human Interaction (https://chi2023.acm.org). 


## Project Overview 

DRAGN-Town is a user focused quest generation engine for a fantasy Role-Playing game setting. Using a user defined knowledge graph that is implemented using Neo4j Aura (https://neo4j.com/cloud/platform/aura-graph-database/) and a GPT-2 langauge model fine tuned for quest generation from a 
World of Warcraft dataset, DRAGN-Town will generate quests in response to user input.

This repository, DRAGN-Town-Quests, is a Python console application for performing a user study of the effectiveness of the quest generation in comparison to other methods. The user study was a core component of the CHI submission and showed that our engine generated quests that felt more personalized than the other tested methods (n-grams and random selection).

## Usage 

The following command can be used to run the engine:

```
python main.py
```

Inside of main.py, when the function receive_input() is called on line 632, a True or False logging parameter is passed in. This is defaulted to false, but can be set to true manually in the code. The logging function is used for user testing of the engine, and records user responses and generated quests to the response_logs folder. 

If logging is True, before accepting user input, the engine will ask for the test proctor's name and the test subject's name to be entered in the command line.

```
Test Moderator, please type your name: Gregory
Type the name of the participant: Trevor
```

These inputs are used to create a log file to write output to. This was used for evaluation of our engine in comparison to other generation methods that was added to our paper submission.

If logging is set to False, these 2 steps are skipped and no log file will be created.

After this step, the user is asked how many quests they would like to generate. The console will loop the number of times that the user specifies.

```
How many prompts will be done: 3 ## The user will receive 3 generate quests before the engine exits.
```

Finally, the user will be asked to type something to receive a quest. Once the user types a string, the quest engine will run and return a generated quest and title based on their input. At the same time, quests using alternative generation methods, specifically, n-gram and random selection from a dataset, are returned to the user.

The quests are presented in a random order and the user answers a few questions to express which quest is preferred. If logging is True, all of the responses are saved and the generation method for each quest is clearly recorded and marked.

```
Sample Quest #1
Type something to get a quest for you!: I want to kill a dragon.

Option 0: 
	Quest: Retrieve Archmage Vargoth's Staff from Ekkorash the Inquisitor and bring it to Ravandwyr in Area 52 . To bring Ekkorash out of hiding , sprinkle the Conjuring Powder on the brazier in the center of the ruins . 
	Title: The Archmage's Staff
	Dialogue: Allow me to introduce myself , Mechanic . I am Ravandwyr , apprentice to the Archmage Vargoth . My master is . . . indisposed , shall we say . I am here on a matter of great importance . The Arklon Ruins southeast of the city are a hotbed of Burning Legion activity . Their purpose in the ruins concerns neither me nor my master , but their leader , Ekkorash , possesses the archmage's staff . This conjuring powder will allow you to draw the demon out of hiding . Sprinkle it on the brazier at the center of the ruins . 


Option 1: 
	Quest: Create the Titan Activation Device ..
	Title:  But the last time out - - Alright , only rule is stay in the inn .
	Dialogue:  Fight the waves of the harbor . Only wither and decay remains in his wake . Unfortunately , this elixir calls for a rare ore that ' s spurring the harpies to be more peaceful ; Murky is .


Option 2: 
	Quest: Kill The Great Dragon of Arelind located in Arelind to obtain Gold stolen by The Great Dragon of Arelind
	Title: The Great Dragon of Arelind
	Dialogue: For those of us trying to escape into Dragonblight , you must find and slay the great dragon , Arelind . It is an honor to stand beside your ancient friend . 

Which quest is most satisfying to you?: 2

Which quest was most responsive to your input?: 2

What was your experience with each quest?: I really like that.....
```

This process repeats until the indicated number of quests has been generated. The program then exits and can be run again for the next user.

## Future Work

DRAGN-Town works with a pre-made, author-created knowledge graph which controls what exists in the world. This limits the ability for the engine to match things that the user seeks that are not "existing" currently in the world. For example, if the user says "I want to mine iron" but iron does not exist in the knowledge graph, the engine will have a difficult time creating a relevant quest from the graph.

A solution to this is using a conversation with the user to help fill the knowledge graph. This will ensure that both the player has control over the world they are building and give the engine an ever growing knowledge bank to generate interesting and applicable questions. We plan to apply a combination of chatbot mechanics to handle user conversation and input parsing (Named-Entity Recognition, semantic role parsing, constituency parsing, etc.) to identify new entities and relationships to add to the knowledge graph and update the graph.

Updates and other projects from DRAGN-Lab can be viewed on the DRAGN-Lab website: https://dragn.ai/#navigation.

## Attributions

DRAGN-Town-Quests code was written by Gregory Knapp (repository owner) and Trevor Ashby (https://github.com/TrevorAshby) with supervision and advice from Dr. Nancy Fulda (https://github.com/NancyFulda).

