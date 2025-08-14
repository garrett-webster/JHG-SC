import copy
import math
from Client.combinedLayout.Node import Node
from Client.combinedLayout.Arrow import Arrow
from Client.combinedLayout.Circle import Circle
class SC_Allocations_Grapher:

    def __init__(self, self_id):
        self.rad = 5
        self.nodes = []
        self.self_id = self_id
        self.arrows = []
        self.node_to_index_dict = {} # this holds the adjusted number accounting for indexes
        self.node_to_number_dict = {}  # holds the actual original index number (for output purposes)

    def create_graph(self, new_vector):
        self.create_node_to_index_dict(new_vector) # figure out where We stand specifically.
        self.create_nodes(new_vector)
        self.nodes.append(Node(0, 0, "PLAYER", "Player " + str(self.self_id+1), False))  # add your own tag # only at the end or it might mess with the arrows.
        new_nodes = [node.to_json() for node in self.nodes] # I understand this but still come on why must I do this
        return new_nodes
        # ok now that we have these, we need to graph them somehow. we will need to just pass these nodes into the
        # existing SC canvas, so lets figure out the best way to do that.

    def create_node_to_index_dict(self, new_vector):
        self.node_to_index_dict = {}
        self.node_to_number_dict = {}
        index_to_add = 0
        for i in range(len(new_vector)):
            if i != self.self_id:
                self.node_to_index_dict[i] = index_to_add
                index_to_add += 1
                self.node_to_number_dict[i] = i # this isn't helpful I don't think

        return self.node_to_index_dict

    def create_nodes(self, new_vector):
        new_nodes = new_vector
        dispalcement = 2 * math.pi / (len(new_nodes)-1)  # find the angular spacing between them, but we are going to be missing one.

        for node in self.node_to_index_dict:
            curr_idx = self.node_to_index_dict[node]
            new_x = math.cos(dispalcement * curr_idx) * self.rad
            new_y = math.sin(dispalcement * curr_idx) * self.rad
            self.nodes.append(Node(new_x, new_y, "PLAYER", "Player " + str(self.node_to_number_dict[node] + 1), False))

    def create_arrows(self, new_vector):
        pass # so the arrows are categorized by 3 things - strength, color and angle. the angle is determined by
        # the angle between the central node and the node they are pointing two, which can be expressed as a funciton of their ID
        # the color is determined by positive or negative
        # and the strength is categorized by the magnitude fo the vector. SO
        if self.arrows: # if there is anything there
            for arrow in self.arrows:  # cycle through
                arrow.remove() # get rid of everything
        self.arrows = [] # go ahead and reset it at the top level as well, makes my life easier.
        for node in self.node_to_index_dict: # cycle through all the relavent nodes.
            start = (0, 0)  # this assumption GREATLY simplifies a lot of the math. also make sure to reset this every time.
            curr_idx = self.node_to_index_dict[node] # get the actual location of the node.
            end = self.nodes[curr_idx].get_x(), self.nodes[curr_idx].get_y() # just get the end position.
            new_magnitude = new_vector[node] # i think? this should work?
            color = "Green"

            if new_magnitude < 0:
                color = "Red"
                start, end = end, start # swaps the values for me
            new_magnitude = abs(new_magnitude) # there is no reason to use that value there, it just feels right ig.
            new_arrow = Arrow(start, end, color=color, line_thickness=new_magnitude / self.rad) # don't worry about it, should be fine.
            self.arrows.append(new_arrow)

        self.add_circle(new_vector[self.self_id])
        return self.arrows


    def add_circle(self, new_magnitude):
        if new_magnitude < 0:
            color = "Red"
            radius = -0.5 + (new_magnitude / (self.rad*2))  # start there?
        elif new_magnitude > 0:
            color = "Green"
            radius = 0.5 + (new_magnitude / (self.rad*2))  # start there?
        else:
            color = "Black" # just to give us a place to start.
            radius = 0.5


        new_circle = Circle((0, 0), radius, line_thickness=new_magnitude / self.rad, color=color)
        self.arrows.append(new_circle)
