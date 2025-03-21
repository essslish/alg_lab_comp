import struct

from compressor.base import Compressor


class BWTCompressor(Compressor):
    def __init__(self, block_size: int = None):
        self.block_size = block_size

    @staticmethod
    def build_cyclic_sa(block: bytes) -> list[int]:
        n = len(block)
        # Начальные ранги — байтовые значения
        rank = list(block)
        sa = list(range(n))
        tmp = [0] * n
        k = 1

        while k < n:
            sa.sort(key=lambda i: (rank[i], rank[(i + k) % n]))
            tmp[sa[0]] = 0
            for j in range(1, n):
                prev, curr = sa[j - 1], sa[j]
                prev_key = (rank[prev], rank[(prev + k) % n])
                curr_key = (rank[curr], rank[(curr + k) % n])
                tmp[curr] = tmp[prev] + (curr_key != prev_key)
            rank[:] = tmp[:]
            if rank[sa[-1]] == n - 1:
                break
            k <<= 1

        return sa

    @staticmethod
    def bwt_transform(block: bytes) -> tuple[bytes, int]:
        n = len(block)
        sa = BWTCompressor.build_cyclic_sa(block)
        last_column = bytes(block[(i - 1) % n] for i in sa)
        original_index = sa.index(0)
        return last_column, original_index

    @staticmethod
    def bwt_inverse(transformed: bytes, original_index: int) -> bytes:
        # Unchanged LF‑mapping implementation
        n = len(transformed)
        freq = [0] * 256
        for b in transformed:
            freq[b] += 1

        starts = {}
        tot = 0
        for i in range(256):
            if freq[i]:
                starts[i] = tot
                tot += freq[i]

        occ = [0] * 256
        LF = [0] * n
        for i, b in enumerate(transformed):
            LF[i] = starts[b] + occ[b]
            occ[b] += 1

        res = bytearray(n)
        pos = original_index
        for i in range(n - 1, -1, -1):
            res[i] = transformed[pos]
            pos = LF[pos]
        return bytes(res)

    def compress(self, data: bytes) -> bytes:
        out = bytearray()
        pos = 0
        while pos < len(data):
            block = data[pos:pos + (self.block_size or len(data))]
            transformed, idx = self.bwt_transform(block)
            out += struct.pack(">II", len(block), idx) + transformed
            pos += len(block)
        return bytes(out)

    def decompress(self, data: bytes) -> bytes:
        pos = 0
        out = bytearray()
        while pos < len(data):
            length, idx = struct.unpack(">II", data[pos:pos + 8])
            pos += 8
            transformed = data[pos:pos + length]
            pos += length
            out += self.bwt_inverse(transformed, idx)
        return bytes(out)
