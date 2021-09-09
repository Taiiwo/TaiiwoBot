from taiiwobot.plugin import Plugin
import requests
import dwh_hashkit
import io

class Check(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "check",
            "Various tools for checking inputs for valid affiliation with 3301",
            [],
            self.hash,
            subcommands=[
                bot.util.Interface(
                    "hash", "Hashes text or webpage at URL and compares it to the deep web hash", [
                        "u url URL to check 1",
                        "v verbose Return the hash products 0"
                    ], self.hash,
                ),
                #bot.util.Interface(
                #    "pgp", "verifies PGP signature for affiliation with 3301", [], self.pgp,
                #),
                #bot.util.Interface(
                #    "outguess", "Reveals if an image has outguess data", [], self.outguess,
                #),
            ],
        ).listen()
        self.dwh = [
            "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4",
            "24f0db614f9ffe58dedc062c68ff8689c29091c77651d699fdef4c1210a8f66ea9e991c17c6d0a47b6110d25bdc1f46354c2065cb6e9cec01554de9ff2888c76",
            "24f0db614f9ffe58de002c62ec13aa6d2432f70dd8f318553f256678720c1042cdcf3307f2c16280d20f2927db60906bb2486ad83a618604303600d7d2ace674",
            "30ac3b4b4ae78110c3ed50018f0bd349eb3d3c2b25ede66160e8f1221bf9e8b8729b0b7f4ddea8d3ebd4e0c2d8b2315b8bcdba6d62eacc2d521130b8645dda77"
        ]
        self.algorithms = ["SHA512", "Blake2b", "Streebog", "SHA3", "FNV-0", "FNV-1", "FNV-1a", "Grøstl", "MD6", "JH", "Blake512", "LSH", "Skein", "Keccak3", "CubeHash", "Whirlpool-0", "Whirlpool-T", "Whirlpool"]

    def hash(self, message, *args, url=False, verbose=False):
        texts = []
        if url:
            texts.append(url)
            r = requests.get(url, stream=True)
            texts.append(r.text)
            for h in r.history:
                texts.append(h.text)
        else:
            texts.append(" ".join(args))
            if texts[0] != texts[0].lower():
                texts.append(texts[0].lower())
            if texts[0] != texts[0].upper():
                texts.append(texts[0].upper())
        i = 0
        found = False
        log = ""
        for text in texts:
            hashes = dwh_hashkit.hash(text)
            if verbose:
                log += "For text: %s \n" % (
                        text[0:100] + "..." if len(text) > 100 else text
                    ) + "\n".join(["[%s] - %s" % (a, h)
                        for a, h in zip(
                            self.algorithms,
                            [h.hex() for h in hashes]
                        )
                    ]) + "\n\n"
                #self.bot.msg(message.target, self.bot.server.code_block(str(hashes)))
            for hash in hashes:
                if hash.hex() in self.dwh:
                    self.bot.msg(message.target, "Deep web hash(%s) found using algorithm %s method %s %s" % (
                        self.dwh.index(hash.hex()),
                        self.algorithms[hashes.index(hash)],
                        "URL" if url else "text",
                        i
                    ))
                    found = True
            i += 1
        if verbose:
            with io.StringIO() as f:
                f.write(log)
                f.seek(0)
                self.bot.msg(message.target, " ", files=[("output.txt", f),])
        if not found:
            self.bot.msg(message.target, "Unlucky")
