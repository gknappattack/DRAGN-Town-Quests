class client_Node():

    def __init__(self, node_type, props):
        self.node_type = node_type
        self.props = props

    def getType(self):
        return self.node_type

    def getProps(self):
        return self.props

    def __str__(self):
        s = "Types: " + str(self.node_type) + "\n" + "Props: " + str(self.props)
        return s