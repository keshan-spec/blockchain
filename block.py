import hashlib, time, json


class Block:
    def __init__(
        self,
        index,
        transactions,
        prev_hash,
        nonce=0,
        timestamp=time.time(),
        hash=None,
    ):
        self.index = index
        self.timestamp = timestamp
        self.hash = hash if hash else self.calculate_hash()
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.nonce = nonce

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    @property
    def data(self):
        return self.__dict__


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        # load the blockchain from json file
        try:
            with open("blockchain.json", "r") as f:
                for block in json.load(f):
                    self.chain.append(Block(**block))
                # self.chain = json.load(f)
                print(f"Blockchain loaded from file: {self.chain}")
        except FileNotFoundError:
            self.create_genesis_block()
            pass

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        # block.nonce = difficulty
        computed_hash = block.calculate_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.calculate_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.prev_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (
            block_hash.startswith("0" * Blockchain.difficulty)
            and block_hash == block.calculate_hash()
        )

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        print(f"New transaction added to pool: {transaction}")
        # len of uncons_transactions is index of new block
        # return len(self.unconfirmed_transactions)
        return self.last_block.index + 1

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            prev_hash=last_block.hash,
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        # add blocks to json file
        with open("blockchain.json", "w") as f:
            # serialize the blocks to json
            f.write(json.dumps([block.__dict__ for block in self.chain]))
            # json.dump(self.__dict__, f, indent=4, sort_keys=True)

        return new_block
