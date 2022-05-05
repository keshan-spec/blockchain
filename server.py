from flask import Flask, request, jsonify
from block import Block, Blockchain
import requests, json

app = Flask(__name__)
blockchain = Blockchain()
peers = set()


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify(
        {"length": len(chain_data), "chain": chain_data, "peers": list(peers)}
    )


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing values", 400

    index = blockchain.add_new_transaction(values)
    response = {"message": f"Transaction will be added to Block {index}"}
    return jsonify(response), 201


@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockchain.last_block
    # last_proof = last_block.data["hash"]
    # proof = blockchain.proof_of_work(last_proof)
    # blockchain.add_new_transaction(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    # )

    # previous_hash = blockchain.hash(last_block)
    block = blockchain.mine()
    if not block:
        return jsonify("No transactions to mine"), 400
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            announce_new_block(block)
            
        response = {
            "message": "New Block Forged",
            "index": block.index,
            "transactions": block.transactions,
            "proof-of-work": block.data["hash"],
            "previous_hash": block.data["prev_hash"],
        }

        return jsonify(response), 200


@app.route("/node/register", methods=["POST"])
def register_node():
    values = request.get_json()
    node = values.get("node")

    if node is None:
        return jsonify("Error: Please supply a valid node"), 400

    peers.add(node)
    return jsonify(
        {
            "message": "New nodes have been added",
            "total_nodes": list(peers),
        }
    )


# endpoint to query unconfirmed transactions
@app.route("/pending_tx")
def get_pending_tx():
    return jsonify(blockchain.unconfirmed_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        print("{}chain".format(node))
        response = requests.get("{}chain".format(node))
        length = response.json()["length"]
        chain = response.json()["chain"]
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {"Content-Type": "application/json"}
        requests.post(
            url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers
        )


app.run(debug=True, port=5010)
