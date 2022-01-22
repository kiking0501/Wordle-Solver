from BaseWordlePlayer import BaseWordlePlayer


class HeuristicWordlePlayer(BaseWordlePlayer):
    """
        Playing Wordle heuristically,
            by picking words that are composed of high-frequency characters
            among the available candidates

        Runtime:
            O(m+n) + num_guess * O(give_guess + get_response + adjust_candidates)
            = O(m+n) + num_guess * O(mk + k + nk)
            = O(k(m+n))

    """

    def __init__(self, wordle, guess_list=None):
        super().__init__(wordle, guess_list)

    def reset(self):
        """
            Reset Character Frequencies
        """
        self.char_freq = self.update_char_freq(self.wordle.words)

    @staticmethod
    def update_char_freq(words):
        """
            Get character frequencies among existing words
                Trick 1:
                    only count unique characters for each word
                Trick 2:
                    ignore characters that already exist for all words

            Return:
                {c: frequencies} for c in each word in words

            Runtime: O(k)
        """
        char_freq = {chr(c): 0 for c in range(ord("a"), ord("z")+1)}
        for w in words:
            for c in set(w):
                char_freq[c] += 1
        for c in char_freq:
            char_freq[c] %= len(words)
        return char_freq

    def compute_score(self, word):
        """
            The score of a word is higher if it is composed of characters with a higher frequency
                among the available candidates

                Trick:
                    compute scores for unique characters only in each word
                    (otherwise results in e.g. "sissy" in the first guess)

            Return:
                the score of the word

            Runtime: O(k)
        """
        return sum([self.char_freq[c] for c in set(word)])

    def give_guess(self, guess_words, candidates, history, fixed_guess=None, verbose=False):
        """
            Provide a guess word that has the maximum score
            (unless specified by the fixed guess)

            Runtime: O(mk)
        """
        if fixed_guess is not None:
            return fixed_guess, self.compute_score(fixed_guess)

        guess, max_score = None, 0.0
        for ind, word in enumerate(guess_words):
            if word not in history:
                score = self.compute_score(word)
                if score >= max_score:
                    guess, max_score = word, score
        return guess, max_score

    def adjust_candidates(self, guess, response, candidates):
        """
            Update character frequencies with the latest available candidates

            Runtime: O(nk), depends on a shrinking n
        """
        new_candidates = super().adjust_candidates(guess, response, candidates)
        if len(new_candidates) >= 1:
            self.char_freq = self.update_char_freq(new_candidates)

        return new_candidates

    @staticmethod
    def should_pick_from(words):
        """
            Should pick from the words if they have the same character sets
            (would be scored indifferently)

            Runtime: O(k)
        """
        c_set = set(words[0])
        for w in words[1:]:
            if set(w) != c_set:
                return False
        return True
