import random
from utility import _bucket_count


class Wordle():
    """
        A Wordle object
            specifies a list of n words with k-letters (as the target pool)
            and the characters used in the response-to-guess output string

    """
    def __init__(self, k, words, rformat=["0", "1", "2"]):
        self.k = k
        self.words = [x for x in words if len(x) == k]
        if not self.words:
            raise ValueError("input words do not contain {}-letter words!".format(k))
        self.rformat = rformat
        if len(rformat) != 3 and any([len(x) > 1 for x in rformat]):
            raise ValueError("wrong response format: must be a list of three single characters")

    def generate_target(self):
        """
            uniformly generate a choice from words
        """
        return random.choice(self.words)

    def response_to_guess(self, guess, target):
        """
            Generate a response for each letter of the guess with respect to the target,
                specified by rformat as follows:

                rformat[0] (default "0") : wrong letter
                rformat[1] (default "1") : correct letter but wrong position
                rformat[2] (default "2") : correct letter and correct position

            If the same letter appears in a guess more than needed,
                the additional appearances would be marked as "0"

            Example input:
                guess = "robot", target = "coach", rformat = ["0","1","2"] (default)

            Example output:
                 response = "02000"

            Runtime: O(k)
        """
        if len(guess) != len(target):
            raise ValueError(
                "size of the guess({}) does not equal to the size of the target({})".format(
                    len(guess), len(target)))

        target_dict = _bucket_count(target)

        k = len(guess)
        response = [self.rformat[0] for _ in range(k)]
        for i, (g, t) in enumerate(zip(guess, target)):
            if g == t:
                response[i] = self.rformat[2]
                target_dict[g] -= 1

        for i, (g, t) in enumerate(zip(guess, target)):
            if g != t:
                if g in target_dict and target_dict[g] > 0:
                    response[i] = self.rformat[1]
                    target_dict[g] -= 1

        return "".join(response)

    def get_response_description(self):
        """
            Return a string that specifies the response format
        """
        return '\n'.join([
            'A {}-character response with the format:'.format(self.k),
            '- "{}": wrong letter'.format(self.rformat[0]),
            '- "{}": correct letter but wrong position'.format(self.rformat[1]),
            '- "{}": correct letter and correct position'.format(self.rformat[2])
        ])

    def is_correct_response(self, response):
        """
            Return a boolean to tell if the response represents an exact match
        """
        return response == (self.rformat[2] * self.k)

    def validate_response(self, response):
        """
            Validate whether the response is in the correct format
        """
        return (response and
                len(response) == self.k and
                set(response).issubset(self.rformat))

    def encode_response(self, response):
        """
            Encode each response as an interger
        """
        response_score = {r: idx for idx, r in enumerate(self.rformat)}
        code = 0
        for i, r in enumerate(response):
            code += (response_score[r] * 3 ** i)
        return code
