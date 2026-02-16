from taiiwobot.plugin import Plugin
import math

import lib.cicada.cicada
from lib.cicada.cicada.gematria import Latin, Runes

cicada = lib.cicada.cicada


class Gematria(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.lp = cicada.LiberPrimus()
        self.interface = bot.util.Interface(
            "gp",  # command name
            # plugin description
            "translates runes and latin using the Gematria Primus.",
            [  # Flags: "<short form> <long form> <description> <1=string or 0=bool>"
                # "o output Specifies the location of the output file 1",
            ],
            self.main,  # root function
            subcommands=[  # list of subcommands
                bot.util.Subcommand(
                    "cipher",  # invoked with $template sub <args/flags>
                    "Perform a cipher on a string Args: <string>",  # subcommand description
                    [
                        "i input Format of input: latin, runes, hex, or custom alpha 1",
                        "a atbash Perform atbash 0",
                        "sub substitute Substitute alphabets, colon separated 1",
                        "s shift Shift the alphabet by n 1",
                        "r running_shift Perform a running shift 1",
                        "v vigenere Perform a vigenere cipher 1",
                        "t totient_stream Perform a totient stream cipher 0",
                        "int interrupts Characters to interrupt shifts 1",
                        "skip skip_indices Indices to skip in shifts 1",
                        "d decrypt Decrypt a running shift 0",
                        "o output Format of output: latin, runes, or numbers 1",
                    ],  # subcommand flags
                    self.cipher,  # subcommand function
                ),
                bot.util.Subcommand(
                    "runes",  # invoked with $template sub <args/flags>
                    "Perform a cipher on a string Args: <string>",  # subcommand description
                    [
                        "a atbash Perform atbash 0",
                        "sub substitute Substitute alphabets, colon separated 1",
                        "s shift Shift the alphabet by n 1",
                        "r running_shift Perform a running shift 1",
                        "v vigenere Perform a vigenere cipher 1",
                        "t totient_stream Perform a totient stream cipher 0",
                        "int interrupts Characters to interrupt shifts 1",
                        "skip skip_indices Indices to skip in shifts 1",
                        "d decrypt Decrypt a running shift 0",
                        "o output Format of output: latin, runes, or numbers 1",
                    ],  # subcommand flags
                    self.runes,  # subcommand function
                ),
                bot.util.Subcommand(
                    "sum",  # invoked with $template sub <args/flags>
                    "Returns the gematria sum for a string: <string>",  # subcommand description
                    [
                        "r runic Supply input in runes instead of latin 0",
                    ],  # subcommand flags
                    self.sum,  # subcommand function
                ),
                bot.util.Subcommand(
                    "sum_index",  # invoked with $template sub <args/flags>
                    "Returns the sum of indexes for a string: <string>",  # subcommand description
                    [
                        "r runic Supply input in runes instead of latin 0",
                    ],  # subcommand flags
                    self.sum_index,  # subcommand function
                ),
                bot.util.Subcommand(
                    "image",  # invoked with $template sub <args/flags>
                    "Shows the gematria primus image",  # subcommand description
                    [],  # subcommand flags
                    self.image,  # subcommand function
                ),
            ],
        ).listen()  # sets the on message callbacks and parses messages

    def main(self, message, *args):  # include your root flags here
        self.interface.help(message.target, self)

    def image(self, message, *args):
        self.bot.msg(
            message.target,
            "https://opensource.cicada.gq/images/gematria.jpg",
            follows=message,
        )

    def cipher(self, message, *args, input=None, atbash=False, substitute=None,
               shift=None, running_shift=None, vigenere=None, totient_stream=None,
               interrupts=None, skip_indices=None, decrypt=False, output=""):
        string = " ".join(args)
        if input is None:
            if string[0] in Latin("").alpha:
                input = "latin"
            elif string[0] in Runes("").alpha:
                input = "runes"
            elif string[0] in cicada.gematria.Hex("").alpha:
                input = "hex"
            else:
                input = "latin"
        print(input)
        input_type = input.lower()
        if input_type == "latin":
            input = Latin(string)
        elif input_type in ["runic", "runes"]:
            input = Runes(string)
        elif input_type == "hex":
            input = cicada.Hex(string)
        else:
            input = cicada.Cipher(string, input)

        if atbash:
            input = input.atbash()
        if substitute:
            alpha1, alpha2 = substitute.split(":")
            input = input.sub(alpha1, alpha2)
        if shift:
            input = input.shift(int(shift))

        interrupts = interrupts.split(",") if interrupts else ""
        skip_indices = skip_indices.split(",") if skip_indices else []

        if running_shift:
            try:
                running_shift = [int(i) for i in running_shift.split(",")]
            except TypeError:
                self.bot.msg(message.target, "Running shift must be a list of integers",
                             follows=message)

            input = input.running_shift(
                running_shift, interrupts, skip_indices, decrypt)
        if vigenere:
            input = input.vigenere(vigenere, interrupts, decrypt)
        if totient_stream:
            input = input.totient_stream(interrupts, skip_indices)

        if output.lower() == "latin" and input_type == "latin":
            output = input.text
        elif output.lower() == "latin":
            output = input.to_latin().text
        elif output.lower() in ["runic", "runes"]:
            output = input.to_runes().text
        elif output.lower() == "numbers":
            output = " ".join([str(c) for c in input.to_numbers()])
        elif output.lower() == "index":
            output = " ".join([str(c) for c in input.to_index()])
        else:
            full_input = input.text
            chunk = ""
            for word in full_input.split(" "):
                if len(chunk) + len(word) < 30:
                    chunk += word + " "
                else:
                    input.text = chunk
                    output += self.format_output(input_type, input)
                    chunk = ""
            input.text = chunk
            output += self.format_output(input_type, input)
            input.text = full_input
            output += self.format_summary(input)

        self.bot.msg(message.target, self.bot.server.code_block(
            output), follows=message)
    
    def format_output(self, input_type, input):
        # latin_text = input.to_latin().text if input_type != "latin" else input.text
        runes_text = input.to_runes().text if input_type != "runes" else input.text

        # Word sums, prime check, and palindrome check
        word_sums = input.gematria_sum_words()  # List of tuples (sum, is_prime, is_palindrome)

        # Simplified output building
        output = ""
        
        # Word sums
        for i, sum in enumerate(word_sums):
            p = "p" if self.is_prime(sum) else ""
            e = "e" if p == "p" and self.is_prime(int(str(sum)[::-1])) else ""
            tag = f"{sum}({p}{e})" if p else f"{sum}"
            # center the output by the length of the word
            word_length = (len(runes_text.split(" ")[i]) * 3) + (1 if i == 0 else 2)
            output += "|" + f"{tag}".center(word_length)
        output += "|"
            
        output = output.strip() + "\n"

        # Latin text, runes, numbers, and indices
        # output += f"{latin_text}\n"
        output += "".join([Runes(c).to_latin().text.rjust(3) for c in runes_text]) + "\n"
        output += "".join([r.rjust(3) for r in runes_text]) + "\n"
        output += "".join([f"{str(c if c != 0 else ' ').rjust(3)}" for c in input.to_numbers()]) + "\n"
        output += "".join([f"{str(c).rjust(3)}" for c in Runes(runes_text).to_index()]) + "\n"
        output += "\n"

        return output
    
    def format_summary(self, input):
        total_sum = input.gematria_sum()
        # entropy = round(input.entropy(), 3)
        # ioc = round(input.index_of_coincidence(), 3)
        rune_count = len(input.to_runes().text.replace(" ", ""))
        # Total sum, and rune count
        return f"| Total Sum: {total_sum} | Rune Count: {rune_count} | Prime sum: {self.is_prime(total_sum)} | Emirp sum: {self.is_prime(int(str(total_sum)[::-1]))} |\n"

    def runes(self, message, *args, **kwargs):
        self.cipher(message, *args, input="runes", **kwargs)

    def latin(self, message, *args, numeric=False, atbash=False):
        string = " ".join(args)
        input = Runes(string)

        if atbash:
            alpha = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
            latin = Runes(input.substitute(alpha, alpha[::-1])).to_latin().text
        else:
            latin = input.to_latin().text
        self.bot.msg(message.target, self.bot.server.code_block(
            latin), follows=message)

    def is_prime(self, n):
        return n not in [0, 1] and all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1))

    def sum(self, message, *args, runes=False):
        if runes:
            input = Runes(" ".join(args))
        else:
            input = Latin(" ".join(args))
        n = input.gematria_sum()
        self.bot.msg(message.target, f"Sum of {input.text}: {n}", follows=message)
        if self.is_prime(n):
            self.bot.msg(message.target, "It's also prime!", follows=message)
            m = int(str(n)[::-1])
            if self.is_prime(m) and m != n:
                self.bot.msg(message.target, "!emirp osla s'tI",
                             follows=message)

    def sum_index(self, message, *args, runes=False):
        if runes:
            input = Runes("".join(args))
        else:
            input = Runes(Latin(" ".join(args)).to_runes().text.replace(" ", ""))
        n = sum(input.to_index())
        self.bot.msg(message.target, n, follows=message)
        if self.is_prime(n):
            self.bot.msg(message.target, "It's also prime!", follows=message)
            m = int(str(n)[::-1])
            if self.is_prime(m) and m != n:
                self.bot.msg(message.target, "!emirp osla s'tI",
                             follows=message)
