import random
from utility import _get_output_path


class BaseWordlePlayer():
    """
        A base class for playing Worldle
            k: length of each word
            m: length of the guess list
            n: length of the Wordle list
    """

    def __init__(self, wordle, guess_list=None):
        """
            Initialize
                wordle: an Wordle object
                guess_list: (list of str)
                    the list of words to guess from, default None
        """
        self.wordle = wordle
        if guess_list is not None:
            self.guess_list = [w for w in guess_list if len(w) == self.wordle.k]
        else:
            self.guess_list = self.wordle.words.copy()
        if not self.guess_list:
            raise ValueError(
                "<guess_list> does not contain {}-letter words!".format(self.wordle.k))

    def compute_score(self, word):
        """
            Return:
                the score of the word
        """
        return -1

    def give_guess(self, guess_words, candidates=None, fixed_guess=None, verbose=True):
        """
           A simple way to provide a guess word:
                either through the user input or the word is generated randomly

            Parameters:
                guess_words: (list of str)
                    the default list of words for guessing
                (optional) candidates:
                    the candidate words that satisfy the target conditions
                (optional) fixed_guess:
                    if supplied, use this as the output guess

            Return:
                the word of guess and its score

            Runtime: O(k) or O(m+k)
        """
        if fixed_guess is not None:
            return fixed_guess, self.compute_score(fixed_guess)

        if verbose:
            while (1):
                guess = input(
                    "## Input Your Own Guess? (<{}-letter word>/empty):\n".format(self.wordle.k))
                if guess in self.wordle.words:
                    return guess, self.compute_score(guess)
                elif not guess:
                    break
                print("(invalid guess: not in the Wordle list)")
        guess = random.choice(guess_words)
        return guess, self.compute_score(guess)

    def get_response(self, guess, target):
        """
            Return:
                a response string for a guess with resect to a target
        """
        return self.wordle.response_to_guess(guess, target)

    def adjust_candidates(self, guess, response, candidates):
        """
            Get updated candidates that satisfy the target conditions
                based on the response from a guess

            Return:
                a list of new candidates of words

            Runtime: O(nk), depends on a shrinking n
        """
        new_candidates = []
        for candidate in candidates:
            attempt = self.get_response(guess, candidate)
            if attempt == response:
                new_candidates.append(candidate)

        return new_candidates

    @staticmethod
    def should_pick_from(words):
        """
            Determine whether one should pick a word as a guess from the input words
            Return a boolean
        """
        return True

    def play(self, target=None, first_guess=None, verbose=False):
        """
            Solve a Wordle game by:

            Step 1. provide a guess word among either the guess list or the available candidates
            Step 2. get a response to the guess word
                if the target is given, the response is automatically generated
                else the response is manually input by the user
            Step 3. if not correct yet,
                adjust the candidate words with respect to the response
                and repeat the above
            Parameters:
                first_guess: (str)
                    if supplied, uses it as the first guess
                verbose: (boolean)
                    set to True to print the intermediate guess words step-by-step

            Output:
                the number of total guesses

            Runtime:
                O(m+n) + num_guess * O(give_guess + get_response + adjust_candidates)

        """
        if verbose:
            print("\nTARGET: ", "UNKNOWN" if target is None else target)

        guess_words = set(self.guess_list)
        candidates = self.wordle.words.copy()

        num_guess = 0
        while (len(candidates) >= 1):
            num_guess += 1

            # Step 1: Guess
            guess, score = self.give_guess(
                guess_words=candidates if self.should_pick_from(candidates) else guess_words,
                candidates=candidates,
                fixed_guess=first_guess if num_guess == 1 else None,
                verbose=verbose)
            if verbose:
                print("# Guesses: {}, # Availalbe Candidates: {}, Picked Guess: {} (Score: {:.2f})".format(
                    num_guess, len(candidates), guess, score))

            # Step 2: Get a response
            if target is None:
                response = None
                while not self.wordle.validate_response(response):
                    response = input(
                        "Type the response...\n{}\n".format(self.wordle.get_response_description())
                    )
            else:
                response = self.get_response(guess, target)
                if verbose:
                    print("# Responses: {}".format(response))

            # Step 3: Check correctness and adjust
            if not self.wordle.is_correct_response(response):
                if verbose and target:
                    input("(... click Enter to proceed ...)\n")
                candidates = self.adjust_candidates(guess, response, candidates)
                guess_words.remove(guess)
            else:
                break

        if len(candidates) == 0:
            print("Failed to guess: no more available candidates!")
            return
        if verbose:
            print("Congrats! Total Guesses: {}".format(num_guess))
        return num_guess

    def print_initial_top_guesses(self, output_dir="output", output_name="top_scores"):
        """
            Save and return a sorted list of computed scores for all guess words

            Return:
                a list of (word, score) ordered by a decreasing score
        """
        top_guesses = sorted(
            [(word, self.compute_score(word)) for word in self.guess_list],
            key=lambda x: (-x[1], x[0]))

        output_path = _get_output_path(output_dir, output_name, type(self).__name__) + ".txt"
        with open(output_path, "w") as f:
            for word, score in top_guesses:
                f.write("\t".join([word, str(score)]) + "\n")
            print("{} saved.".format(f.name))

        return top_guesses
