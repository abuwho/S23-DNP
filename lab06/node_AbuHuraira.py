# Author: Abu Huraira

import random
import sched
import socket
import time
from threading import Thread, Lock
from argparse import ArgumentParser
from enum import Enum
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

PORT = 1234
CLUSTER = [1, 2, 3]
ELECTION_TIMEOUT = (6, 8)
HEARTBEAT_INTERVAL = 5


class NodeState(Enum):
    """Enumerates the three possible node states (follower, candidate, or leader)"""
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


class Node:
    def __init__(self, node_id):
        """Non-blocking procedure to initialize all node parameters and start the first election timer"""
        self.node_id = node_id
        self.state = NodeState.FOLLOWER
        self.term = 0
        self.votes = {}
        self.log = []
        self.pending_entry = ''
        self.sched = sched.scheduler(time.monotonic, time.sleep)
        self.lock = Lock()
        self.election_timer = None
        self.heartbeat_timer = None
        self.start_election_timer()
        self.server = SimpleXMLRPCServer(('0.0.0.0', PORT + node_id), logRequests=False)
        self.server.register_instance(self)

        print(f"Node {self.node_id} started! State: {self.state}. Term: {self.term}")
        Thread(target=self.sched.run, daemon=True).start()

    def start_election_timer(self):
        """Starts a new election timer with a random duration between ELECTION_TIMEOUT"""
        duration = random.uniform(*ELECTION_TIMEOUT)
        self.election_timer = self.sched.enter(duration, 1, self.hold_election)

    def is_leader(self):
        """Returns True if this node is the elected cluster leader and False otherwise"""
        return self.state == NodeState.LEADER

    def reset_election_timer(self):
        """Resets election timer for this (follower or candidate) node and returns it to the follower state"""
        if self.election_timer is not None:
            self.sched.cancel(self.election_timer)
            self.start_election_timer()
        self.state = NodeState.FOLLOWER
        self.votes = {}
        print(f"Node {self.node_id} reset election timer. State: {self.state}. Term: {self.term}")

    def hold_election(self):
        """Called when this follower node is done waiting for a message from a leader (election timeout)
            The node increments term number, becomes a candidate and votes for itself.
            Then call request_vote over RPC for all other online nodes and collects their votes.
            If the node gets the majority of votes, it becomes a leader and starts the hearbeat timer
            If the node loses the election, it returns to the follower state and resets election timer.
        """
        with self.lock:
            self.term += 1
            self.state = NodeState.CANDIDATE
            self.votes = {self.node_id: True}
            print(f"Node {self.node_id} started new election term {self.term}. State: {self.state}")
            self.request_vote()

    def request_vote(self, term, candidate_id):
        """Called remotely when a node requests voting from other nodes.
            Updates the term number if the received one is greater than `self.term`
            A node rejects the vote request if it's a leader or it already voted in this term.
            Returns True and update `self.votes` if the vote is granted to the requester candidate and False otherwise.
        """
        if term > self.term:
            self.term = term
            self.state = NodeState.FOLLOWER
            self.votes = {}

        if self.state == NodeState.LEADER:
            return False

        if self.term == term and self.votes.get(term):
            return False

        # Check if candidate's log is at least as up-to-date as ours
        candidate_log_len = len(candidate_log)
        if candidate_log_len >= len(self.log):
            last_entry_idx = len(self.log) - 1
            if self.log[last_entry_idx][0] == candidate_log[last_entry_idx][0]:
                return False
        else:
            return False

        # Vote for the candidate
        self.votes[term] = candidate_id
        return True
    
    def append_entries(self):
        """Called by leader every HEARTBEAT_INTERVAL, sends a heartbeat message over RPC to all online followers.
            Accumulates ACKs from followers for a pending log entry (if any)
            If the majority of followers ACKed the entry, the entry is committed to the log and is no longer pending
        """
        if self.state != NodeState.LEADER:
            return

        # send heartbeat to all online followers
        for node_id in CLUSTER:
            if node_id == self.node_id:
                continue
            try:
                proxy = ServerProxy(f"http://localhost:{PORT+node_id}/")
                proxy.heartbeat(self.log[-1])
            except socket.error:
                # if follower is down, move to next one
                continue

        # accumulate ACKs from followers for pending entry (if any)
        if self.pending_entry:
            ack_count = 1  # already voted for itself
            for vote in self.votes.values():
                if vote:
                    ack_count += 1
            if ack_count > len(CLUSTER) // 2:
                # entry is committed to the log and no longer pending
                self.log.append(self.pending_entry)
                self.pending_entry = ''
                print(f"Leader {self.node_id} committed new entry to log")
    
    def heartbeat(self, leader_entry):
        """
        Called remotely from the leader to inform followers that it's alive and supply any pending log entry.
        Followers would commit an entry if it was pending before, but is no longer now.
        Returns True to ACK the heartbeat and False on any problems.
        """
        print(f"Heartbeat received from leader (entry='{leader_entry}')")
        
        if self.state != NodeState.FOLLOWER:
            return False
        
        if self.pending_entry == leader_entry:
            self.log.append(leader_entry)
            self.pending_entry = ''
        
        return True
    
    def leader_receive_log(self, log):
        """Called remotely from the client. Executed only by the leader upon receiving a new log entry.
        Returns True after the entry is committed to the leader log and False on any problems.
        """
        print(f"Leader received log '{log}' from client")
        
        # Append the new log entry to the leader's log
        self.log.append(log)
        
        # Replicate the log entry to all followers
        for follower_id in self.follower_ids:
            try:
                # Make RPC call to the follower's `append_entries` method
                follower = self.nodes[follower_id]
                follower.append_entries(self.current_term, self.id, self.commit_index, self.log)
            except:
                # Handle any errors or exceptions during RPC call
                print(f"Failed to replicate log to follower {follower_id}")
                return False
        
        return True


if __name__ == '__main__':
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("node_id", type=int, help="the ID of this node")
    args = parser.parse_args()

    # Create the node instance
    node = Node(args.node_id)

    # Start RPC server and expose the node instance
    server = SimpleXMLRPCServer(('0.0.0.0', PORT), logRequests=False, allow_none=True)
    server.register_instance(node)

    # Run the node scheduler in a separate thread
    def run_scheduler():
        while True:
            node.sched.run(blocking=True)

    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Wait for KeyboardInterrupt and terminate gracefully
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Terminating gracefully.")