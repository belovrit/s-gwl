import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import os.path
import networkx as nx
import pickle

G1 = nx.read_edgelist("/Users/alexwang/Documents/UCLA 2019 Fall/Wasserstein Research/GraphMatching/model/s-gwl/data/aids_toy1.edgelist")
G2 = nx.read_edgelist("/Users/alexwang/Documents/UCLA 2019 Fall/Wasserstein Research/GraphMatching/model/s-gwl/data/aids_toy2.edgelist")

data = {}

# degree1 =
probs1 = [x[1] for x in G1.degree]
probs1 = np.array(probs1 / np.sum(probs1)).reshape((len(probs1), 1))

# degree2 =
probs2 = [x[1] for x in G2.degree]
probs2 = np.array(probs2 / np.sum(probs2)).reshape((len(probs2), 1))
probs = [probs1, probs2]


adj1 = nx.adjacency_matrix(G1)
adj2 = nx.adjacency_matrix(G2)


data['costs'] = [adj1, adj2]

data['probs'] = probs


idx2nodes1 = dict(zip(range(len(G1.nodes)), sorted(G1.nodes)))
idx2nodes2 = dict(zip(range(len(G2.nodes)), sorted(G2.nodes)))
idx2nodes = [idx2nodes1, idx2nodes2]
data['idx2nodes'] = idx2nodes


import methods.EvaluationMeasure as Eval
import methods.GromovWassersteinGraphToolkit as GwGt
import pickle
import time
import warnings


warnings.filterwarnings("ignore")

database = data

num_iter = 2000
ot_dict = {'loss_type': 'L2',  # the key hyperparameters of GW distance
           'ot_method': 'proximal',
           'beta': 0.025,
           'outer_iteration': num_iter,
           # outer, inner iteration, error bound of optimal transport
           'iter_bound': 1e-30,
           'inner_iteration': 2,
           'sk_bound': 1e-30,
           'node_prior': 1e3,
           'max_iter': 4,  # iteration and error bound for calcuating barycenter
           'cost_bound': 1e-26,
           'update_p': False,  # optional updates of source distribution
           'lr': 0,
           'alpha': 0}

for i in range(1):
    cost_s = database['costs'][0]
    cost_t = database['costs'][i+1]
    p_s = database['probs'][0]
    p_t = database['probs'][i+1]
    idx2node_s = database['idx2nodes'][0]
    idx2node_t = database['idx2nodes'][i+1]
    num_nodes = min([len(idx2node_s), len(idx2node_t)])

    time_s = time.time()
    ot_dict['outer_iteration'] = num_iter
    pairs_idx, pairs_name, pairs_confidence, soft_X = GwGt.recursive_direct_graph_matching(
        0.5 * (cost_s + cost_s.T), 0.5 * (cost_t + cost_t.T), p_s, p_t, idx2node_s, idx2node_t, ot_dict,
        weights=None, predefine_barycenter=False, cluster_num=2,
        partition_level=3, max_node_num=0)
    runtime = time.time() - time_s
    nc = Eval.calculate_node_correctness(pairs_name, num_correspondence=num_nodes)
    print(pairs_idx)
    print(pairs_name)
    print('soft_X', soft_X)

    print('method: s-gwl, duration {:.4f}s, nc {:.4f}.'.format(runtime, nc))
    with open('results/sgwl_ppi_syn_{}.pkl'.format(i + 1), 'wb') as f:
        pickle.dump([nc, runtime], f)




