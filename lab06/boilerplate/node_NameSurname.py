import random
import sched
import socket
import time
from threading import Thread
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
        self.sched = sched.scheduler()
        # Start election timer for this node
        self.reset_election_timer()
        print(f"Node started! State: {self.state}. Term: {self.term}")

    def is_leader(self):
        """Returns True if this node is the elected cluster leader and False otherwise"""
        return self.state == NodeState.LEADER

    def reset_election_timer(self):
        """Resets election timer for this (follower or candidate) node and returns it to the follower state"""
        self.sched.cancel(self.election_timer)
        self.election_timer = self.sched.enter(random.uniform(*ELECTION_TIMEOUT), 1, self.hold_election)
        self.state = NodeState.FOLLOWER

    def hold_election(self):
        """Called when this follower node is done waiting for a message from a leader (election timeout)
            The node increments term number, becomes a candidate and votes for itself.
            Then call request_vote over RPC for all other online nodes and collects their votes.
            If the node gets the majority of votes, it becomes a leader and starts the heartbeat timer
            If the node loses the election, it returns to the follower state and resets election timer.
        """
        self.term += 1
        self.state = NodeState.CANDIDATE
        self.votes = {self.node_id: True}
        print(f"New election term {self.term}. State: {self.state}")
        for node in CLUSTER:
            if node == self.node_id:
                continue
            try:
                server = ServerProxy(f"http://localhost:{PORT + node}")
                granted = server.request_vote(self.term, self.node_id)
                if granted:
                    self.votes[node] = True
            except socket.error:
                pass
        if sum(self.votes.values()) > len(CLUSTER) // 2:
            self.state = NodeState.LEADER
            self.reset_heartbeat_timer()
        else:
            self.reset_election_timer()

    def request_vote(self, term, candidate_id):
        """Called remotely when a node requests voting from other nodes.
            Updates the term number if the received one is greater than `self.term`
            A node rejects the vote request if it's a leader or it already voted in this term.
            Returns True and update `self.votes` if the vote is granted to the requester candidate and False otherwise.
        """
        print(f"Got a vote request from {candidate_id} (term={term})")
        if term > self.term:
            # if received term is greater than our current term, update our term and go back to follower state
            self.term = term
            self.state = NodeState.FOLLOWER
        if self.state == NodeState.LEADER:
            # we cannot vote if we're already a leader
            return False
        if term == self.term and candidate_id in self.votes:
            # we cannot vote twice in the same term for the same candidate
            return False
        # vote for the candidate and update our vote record
        self.votes[candidate_id] = term
        return True


    def append_entries(self):
        """
        Called by leader every HEARTBEAT_INTERVAL, sends a heartbeat message over RPC to all online followers.
        Accumulates ACKs from followers for a pending log entry (if any)
        If the majority of followers ACKed the entry, the entry is committed to the log and is no longer pending
        """
        if self.state != NodeState.LEADER:
            return

        # send a heartbeat message over RPC to all online followers
        for node_id in CLUSTER:
            if node_id == self.node_id:
                continue
            try:
                proxy = ServerProxy(f"http://localhost:{PORT+node_id}")
                ack = proxy.heartbeat(self.pending_entry)
                if ack:
                    self.votes[node_id] = True
            except (socket.timeout, ConnectionRefusedError):
                pass

        # accumulate ACKs from followers for a pending log entry (if any)
        if self.pending_entry:
            ack_count = sum(self.votes.values())
            if ack_count > len(CLUSTER) // 2:
                self.log.append(self.pending_entry)
                self.pending_entry = ''


    def heartbeat(self, leader_entry):  
        """Called remotely from the leader to inform followers that it's alive and supply any pending log entry
            Followers would commit an entry if it was pending before, but is no longer now.
            Returns True to ACK the heartbeat and False on any problems.
        """
        print(f"Heartbeat received from leader (entry='{leader_entry}')")
        if self.state != NodeState.FOLLOWER:
            return False

        if self.term < leader_entry['term']:
            self.term = leader_entry['term']
            self.reset_election_timer()

        if self.pending_entry == leader_entry['log']:
            self.pending_entry = ''
            self.log.append(leader_entry['log'])

        return True


    def leader_receive_log(self, log):
        """Called remotely from the client. Executed only by the leader upon receiving a new log entry
        Returns True after the entry is committed to the leader log and False on any problems
        """
        print(f"Leader received log '{log}' from client")
        self.log.append(log)
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