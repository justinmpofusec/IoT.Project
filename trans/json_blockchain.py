import hashlib
import json
import datetime as date
import os


class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0, block_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = block_hash or self.calculate_hash()

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

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }


class Blockchain:
    def __init__(self, difficulty=3, filename="blockchain.json"):
        self.difficulty = difficulty
        self.filename = filename
        self.chain = []

        if os.path.exists(self.filename):
            self.load_chain()
        else:
            genesis = Block(0, date.datetime.now(), "Genesis Block", "0")
            genesis.mine_block(self.difficulty)
            self.chain = [genesis]
            self.save_chain()

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        block = Block(
            len(self.chain),
            date.datetime.now(),
            data,
            self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.save_chain()

    def save_chain(self):
        with open(self.filename, "w") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4)

    def load_chain(self):
        with open(self.filename, "r") as f:
            chain_data = json.load(f)

        self.chain = []
        for b in chain_data:
            block = Block(
                b["index"],
                b["timestamp"],
                b["data"],
                b["previous_hash"],
                b["nonce"],
                b["hash"]
            )
            self.chain.append(block)

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
    blockchain = Blockchain(difficulty=3, filename="blockchain.json")

    while True:
        print("\n1. Add Block")
        print("2. View Chain")
        print("3. Validate Chain")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            data = input("Enter block data: ")
            blockchain.add_block(data)
            print("Block added and saved to JSON.")

        elif choice == "2":
            for block in blockchain.chain:
                print("\n-----------------------")
                print("Index:", block.index)
                print("Timestamp:", block.timestamp)
                print("Data:", block.data)
                print("Nonce:", block.nonce)
                print("Hash:", block.hash)
                print("Previous Hash:", block.previous_hash)

        elif choice == "3":
            print("Blockchain valid?" , blockchain.is_valid())

        elif choice == "4":
            break

        else:
            print("Invalid option.")