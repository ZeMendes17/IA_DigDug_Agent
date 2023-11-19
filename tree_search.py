# Module: tree_search
#
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2019,
#  Inteligência Artificial, 2014-2019

from abc import ABC, abstractmethod


# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):
    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return self.domain.satisfies(state, self.goal)


# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self, state, parent, depth=0, cost=0, heuristic=None, action=None):
        self.state = state
        self.parent = parent
        self.depth = depth  # adicionado para calcular a profundidade
        self.cost = cost  # adicionado para calcular o custo
        self.heuristic = heuristic  # 12
        self.action = action  # strips

    def in_parent(self, newState):  # adicionado para evitar ciclos
        if self.parent == None:
            return False
        if self.parent.state == newState:
            return True
        return self.parent.in_parent(newState)

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"

    def __repr__(self):
        return str(self)

    def plan(self):
        return self.parent.plan() + [self.action] if self.parent else []


# Arvores de pesquisa
class SearchTree:
    # construtor
    def __init__(self, problem, strategy="breadth"):
        self.problem = problem
        root = SearchNode(
            problem.initial,
            None,
            heuristic=problem.domain.heuristic(problem.initial, problem.goal),
        )  # 12
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0  # adicionado para calcular o numero de nos nao terminais
        self.highest_cost_nodes = [root]  # 15 tem a root pois e o no com maior custo
        self.total_depth = 0  # 16

    @property  # adicionado para calcular o comprimento da solucao
    def length(self):
        return self.solution.depth

    @property  # adicionado para calcular o numero de nos terminais
    def terminals(self):
        return len(self.open_nodes) + 1

    @property
    def avg_branching(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals

    @property  # ex9
    def cost(self):
        return self.solution.cost

    @property  # strips
    def plan(self):
        return self.solution.plan()

    @property  # 16
    def average_depth(self):
        return self.total_depth / (self.terminals + self.non_terminals)

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self, node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

    # procurar a solucao
    def search(self, limit=None):
        count = 0
        while self.open_nodes != []:
            count += 1
            print(count)
            if count % 1000 == 0: # tá a demorar muito, para encontrar dont know why
                break
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.solution = node
                return self.get_path(node)
            self.non_terminals += (
                1  # adicionado para calcular o numero de nos nao terminais
            )
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state, a)
                if not node.in_parent(newstate):
                    if (
                        limit is None or node.depth < limit
                    ):  # adicionado para limitar a profundidade
                        newnode = SearchNode(
                            newstate,
                            node,
                            node.depth + 1,
                            node.cost + self.problem.domain.cost(node.state, a),  # ex8
                            self.problem.domain.heuristic(
                                newstate, self.problem.goal
                            ),  # 12
                            a,  # strips
                        )  # adicionado para calcular a profundidade
                        if self.highest_cost_nodes[0].cost < newnode.cost:  # 15
                            self.highest_cost_nodes = [newnode]
                        elif self.highest_cost_nodes[0].cost == newnode.cost:
                            self.highest_cost_nodes.append(newnode)

                        self.total_depth += newnode.depth  # 16
                        
                        # print(newnode.state["digdug"])
                        lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self, lnewnodes):
        if self.strategy == "breadth":
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == "depth":
            self.open_nodes[:0] = lnewnodes
            self
        elif self.strategy == "uniform":  # ex10
            self.open_nodes.extend(lnewnodes)  # adicionado os novos nos
            self.open_nodes.sort(key=lambda node: node.cost)  # orderna os nos por custo

        elif self.strategy == "greedy":  # 13
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.heuristic)

        elif self.strategy == "a*":  # 14
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.cost + node.heuristic)
