# Neo4J for knowledge graphs
#from client_Node import client_Node
class client_Edge():

    def __init__(self, n1, relType, n2):
        self.n1 = n1
        self.relType = relType
        self.n2 = n2

    def getNode1(self):
        return self.n1

    def getNode2(self):
        return self.n2

    def getRel(self):
        return self.relType

    def __str__(self):
        s = "Node 1\n" + str(self.n1) + "\n" + self.relType + "\n" + "Node 2\n" + str(self.n2)
        return s