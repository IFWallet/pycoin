import unittest

from pycoin.ecdsa.secp256k1 import secp256k1_generator
from pycoin.networks.registry import network_for_netcode
from pycoin.solve.utils import build_hash160_lookup


def make_tests_for_netcode(netcode):
    network = network_for_netcode(netcode)

    address_for_script = network.ui.address_for_script
    script_for_p2pkh = network.script_info.script_for_p2pkh
    script_for_p2pk = network.script_info.script_for_p2pk
    script_for_nulldata = network.script_info.script_for_nulldata

    Tx = network.tx
    Key = network.extras.Key

    class AddressForScriptTest(unittest.TestCase):

        def test_script_type_pay_to_address(self):
            for se in range(1, 100):
                key = Key(secret_exponent=se)
                for b in [True, False]:
                    addr = key.address(use_uncompressed=b)
                    sc = script_for_p2pkh(key.hash160(use_uncompressed=b))
                    afs_address = address_for_script(sc)
                    self.assertEqual(afs_address, addr)

        def test_solve_pay_to_address(self):
            for se in range(1, 10):
                key = Key(secret_exponent=se)
                for b in [True, False]:
                    addr = key.address(use_uncompressed=b)
                    script = script_for_p2pkh(key.hash160(use_uncompressed=b))
                    afs_address = address_for_script(script)
                    self.assertEqual(afs_address, addr)
                    hl = build_hash160_lookup([se], [secp256k1_generator])
                    tx = Tx(1, [], [Tx.TxOut(100, script)])
                    tx.sign(hash160_lookup=hl)
                    afs_address = address_for_script(tx.txs_out[0].puzzle_script())
                    self.assertEqual(afs_address, addr)

        def test_script_type_pay_to_public_pair(self):
            for se in range(1, 100):
                key = Key(secret_exponent=se)
                for b in [True, False]:
                    addr = key.address(use_uncompressed=b)
                    sc = script_for_p2pk(key.sec(use_uncompressed=b))
                    afs_address = address_for_script(sc)
                    self.assertEqual(afs_address, addr)

        def test_solve_pay_to_public_pair(self):
            for se in range(1, 10):
                key = Key(secret_exponent=se)
                for b in [True, False]:
                    addr = key.address(use_uncompressed=b)
                    script = script_for_p2pk(key.sec(use_uncompressed=b))
                    afs_address = address_for_script(script)
                    self.assertEqual(afs_address, addr)
                    hl = build_hash160_lookup([se], [secp256k1_generator])
                    tx = Tx(1, [], [Tx.TxOut(100, script)])
                    tx.sign(hash160_lookup=hl)
                    afs_address = address_for_script(tx.txs_out[0].puzzle_script())
                    self.assertEqual(afs_address, addr)

        def test_weird_tx(self):
            # this is from tx 12a8d1d62d12307eac6e62f2f14d7e826604e53c320a154593845aa7c8e59fbf
            afs_address = address_for_script(b'Q')
            self.assertNotEqual(afs_address, None)
            self.assertEqual(afs_address, "???")

        def test_issue_225(self):
            script = script_for_nulldata(b"foobar")
            tx_out = Tx.TxOut(1, script)
            address = address_for_script(tx_out.puzzle_script())
            self.assertEqual(address, "(nulldata 666f6f626172)")

    return AddressForScriptTest


for netcode in ["BTC", "LTC", "BCH"]:
    exec("%sTests = make_tests_for_netcode('%s')" % (netcode, netcode))


if __name__ == "__main__":
    unittest.main()
