from flask import Flask, request, jsonify
from block import Block, Blockchain

app = Flask(__name__)
blockchain = Blockchain()


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({"length": len(chain_data), "chain": chain_data})


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

    response = {
        "message": "New Block Forged",
        "index": block.index,
        "transactions": block.transactions,
        "proof-of-work": block.data["hash"],
        "previous_hash": block.data["prev_hash"],
    }

    return jsonify(response), 200


app.run(debug=True, port=5010)
