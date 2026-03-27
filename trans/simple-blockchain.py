# block.py
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Block:
    index: int
    timestamp: datetime
    data: Any
    previous_hash: str
    hash: str = ""

    def __post_init__(self) -> None:
        # Calculate the block hash after initialization
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Compute SHA-256 hash from block contents.
        """
        hash_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(hash_string.encode("utf-8")).hexdigest()



class Blockchain:
    def __init__(self) -> None:
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block(0, datetime.now(), "Genesis Block", "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Any) -> Block:
        """
        Create a new block with 'data' and append it to the chain.
        """
        latest = self.get_latest_block()
        new_block = Block(
            index=latest.index + 1,
            timestamp=datetime.now(),
            data=data,
            previous_hash=latest.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_valid(self) -> bool:
        """
        Validate blockchain integrity by checking each block hash
        and previous-hash linkage.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Verify current block hash matches recalculated hash
            if current.hash != current.calculate_hash():
                return False

            # Verify linkage
            if current.previous_hash != previous.hash:
                return False

        return True


def main() -> None:
    bc = Blockchain()

    # Add blocks (as in your document)
    bc.add_block("Transaction Data 1")
    bc.add_block("Transaction Data 2")
    bc.add_block("Transaction Data 3")
    bc.add_block("Transaction Data 4")

    # Print chain
    for block in bc.chain:
        print(f"Block #{block.index}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Data: {block.data}")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")
        print()

    print("Blockchain valid?", bc.is_valid())


if __name__ == "__main__":
    main()
