import hashlib
import datetime as date


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block #{self.index} mined: {self.hash}")


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    def create_genesis_block(self):
        block = Block(0, date.datetime.now(), "Genesis Block", "0")
        block.mine_block(self.difficulty if hasattr(self, "difficulty") else 4)
        return block

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(
            index=len(self.chain),
            timestamp=date.datetime.now(),
            data=data,
            previous_hash=self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

            if not current.hash.startswith("0" * self.difficulty):
                return False

        return True


if __name__ == "__main__":
    blockchain = Blockchain(difficulty=4)

    blockchain.add_block("Transaction Data 1")
    blockchain.add_block("Transaction Data 2")
    blockchain.add_block("Transaction Data 3")

    for block in blockchain.chain:
        print("\n------------------------")
        print("Block #", block.index)
        print("Timestamp:", block.timestamp)
        print("Data:", block.data)
        print("Nonce:", block.nonce)
        print("Hash:", block.hash)
        print("Previous Hash:", block.previous_hash)

    print("\nBlockchain valid?", blockchain.is_valid())