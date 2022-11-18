from neo4j import GraphDatabase
from neo4j_interface.DAOInterface import DAOInterface
import re


# For info on Cypher Query Language, see
# https://neo4j.com/developer/cypher/intro-cypher/

# Make sure to pip install neo4j


class Neo4jDAO(DAOInterface):
    def __init__(self, uri, user, pwd):
        super().__init__()
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def createNode(self, objType, dictArgs):
        # figure out a good way to replace the strings in the dictionary
        the_str = f"merge (x:{objType} {dictArgs})"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def createEdge(self, objTypeN1, argsN1, objTypeN2, argsN2, relType):
        the_str = f"match (x:{objTypeN1} {argsN1}) match (y:{objTypeN2} {argsN2}) merge (x)-[:{relType}]->(y)"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def getNode(self, objType, dictArgs):
        the_str = f"match (x:{objType} {dictArgs}) return x"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        res = self.query(the_str)
        matches = []
        for x in res:
            n_type = [a for a in x[0].labels]
            n_props = [a for a in x[0].items()]
            node = client_Node(n_type, n_props)
            matches.append(node)
        return matches

    # Note from Chaz: I'm leaving this in, but it should be treated as deprecated
    def getConnections(self, objType, dictArgs):
        the_str = f"match (x:{objType} {dictArgs})--(y) return x, y"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def getConnectionsWithRel(self, objType, dictArgs):
        the_str = f"match (x:{objType} {dictArgs})-[r]-(y) return x, r, y"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        res = self.query(the_str)
        connections = []
        for x in res:
            n1_type = [a for a in x[0].labels]
            n1_props = [a for a in x[0].items()]
            n1 = client_Node(n1_type, n1_props)
            # print("Node ", n1.getType(), "\n", n1.getProps())
            rel_type = x[1].type
            n2_type = [a for a in x[2].labels]
            n2_props = [a for a in x[2].items()]
            n2 = client_Node(n2_type, n2_props)
            edge = client_Edge(n1, rel_type, n2)
            # print(edge)
            connections.append(edge)
        return connections

    def deleteNode(self, objType, dictArgs):
        the_str = f"match (x:{objType} {dictArgs}) detach delete x"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def deleteEdge(self, objTypeN1, argsN1, objTypeN2, argsN2, relType):
        the_str = f"match (x:{objTypeN1} {argsN1})-[r:{relType}]-(y:{objTypeN2} {argsN2}) delete r"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def updateNode(self, objType, dictArgs, update_name, update_data):
        the_str = f"match (x:{objType} {dictArgs}) set x.{update_name} = {update_data} return x"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)

    def updateEdge(self, objTypeN1, argsN1, objTypeN2, argsN2, relType, update_name, update_data):
        the_str = f"match (x:{objTypeN1} {argsN1})-[r:{relType}]-(y:{objTypeN2} {argsN2}) set r.{update_name} = {update_data} return r"
        the_str = re.sub("'(\w+)':", r"\1:", the_str)
        return self.query(the_str)


if __name__ == "__main__":
    pass
