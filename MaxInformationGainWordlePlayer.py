from BaseWordlePlayer import BaseWordlePlayer
from utility import _get_output_path
import numpy as np
import os
from tqdm import tqdm


class MaxInformationGainWordlePlayer(BaseWordlePlayer):
    """
        Playing Wordle based on maximizing information gain

        At each guess, pick the word that generates the maximum Shannon entropy
            from its response distribution (the count of all possible response outcomes
            with respect to the available target words).

        Runtime:
            Precompute: O(mnk)
            Play:
                O(m+n) + num_guess * O(give_guess + get_response + adjust_candidates)
            ~= O(m+n) + num_guess * O(m*3^k + mnk)
            ~= O(m(3^k + nk))
    """

    def __init__(self, wordle, guess_list=None, precompute="small"):
        super().__init__(wordle, guess_list)
        self.WORD_IDX = self.precompute_word_idx()
        self.RESPONSES = self.precompute_response_to_guess(suffix=precompute)
        self.precompute = precompute

    def reset(self):
        """
            Reset Response Distributions
        """
        self.distribution = self.precompute_init_distribution(suffix=self.precompute)

    def precompute_word_idx(self):
        """
            Return maps of {word: idx} from the guess list and the Wordle list
            Runtime: O(k(m+n))
        """
        return {
            "guess": {x: i for i, x in enumerate(self.guess_list)},
            "target": {x: i for i, x in enumerate(self.wordle.words)}
        }

    def precompute_response_to_guess(self, output_dir="output", suffix="small", verbose=True):
        """
            Precompute and cache possible responses for each guess to each target
                (since they will be frequently accessed during score computation)
            Return:
                {idx(guess): idx(target): response} for each guess and each target

            Runtime: O(mnk) for first compute
        """

        output_path = _get_output_path(output_dir, "precompute_responses", suffix) + ".txt"
        responses = {i: {} for i in range(len(self.guess_list))}
        if os.path.exists(output_path):
            with open(output_path) as f:
                for line in f.readlines():
                    guess_idx, target_idx, response_code = line.strip().split("\t")
                    responses[int(guess_idx)][int(target_idx)] = response_code
        else:
            if verbose:
                print("Pre-computing all responses between words...")
                li = tqdm(self.guess_list)
            else:
                li = self.guess_list
            with open(output_path, "w") as f:
                for i, guess in enumerate(li):
                    for j, target in enumerate(self.wordle.words):
                        responses[i][j] = self.wordle.response_to_guess(guess, target)
                        f.write("\t".join([str(i), str(j), responses[i][j]]) + "\n")
                print("{} saved.".format(f.name))
        return responses

    def precompute_init_distribution(self, output_dir="output", suffix="small", verbose=True):
        """
            Precompute and cache the initial response distribution
                for each guess word with respect to all tareget words

            Return:
                {idx(guess): response: count} for each guess and each response

            Runtime: O(mnk) for first compute
        """
        output_path = _get_output_path(output_dir, "precompute_init_distribution", suffix) + ".txt"
        if os.path.exists(output_path):
            distribution = {i: {} for i in self.RESPONSES}
            with open(output_path) as f:
                for line in f.readlines():
                    i, response, count = line.strip().split("\t")
                    distribution[int(i)][response] = int(count)
        else:
            if verbose:
                print("Pre-computing initial response distribution between words...")
            distribution = self.get_distribution(self.wordle.words)
            with open(output_path, "w") as f:
                for i in self.RESPONSES:
                    for response in distribution[i]:
                        f.write("\t".join([str(i), response, str(distribution[i][response])]) + "\n")
                print("{} saved.".format(f.name))
        return distribution

    def get_distribution(self, words):
        """
            For each word, computes all possible response outcomes
                with respect to different target words
                and store the frequency of each response (distribution)

            Return:
                {idx(word):{response: count}}

            Runtime: O(mnk) with a shrinking n
        """
        distribution = {}
        for i in self.RESPONSES:
            distribution[i] = {}
            for w in words:
                j = self.WORD_IDX["target"][w]
                response = self.RESPONSES[i][j]
                if response not in distribution[i]:
                    distribution[i][response] = 0
                distribution[i][response] += 1
        return distribution

    def compute_score(self, word):
        """
            The score of a word
                is the Shannon entropy of its response distribution

            Runtime: O(3^k)
        """
        word_idx = self.WORD_IDX["guess"][word]
        total = sum(self.distribution[word_idx].values())
        score = 0.0
        for x in self.distribution[word_idx].values():
            px = x*1.0/total
            score += -px * np.log(px)
        return score

    def give_guess(self, guess_words, candidates, history, fixed_guess=None, verbose=False):
        """
            Pick the guess word that has the maximum Shannon entropy
            (unless specified by the fixed guess)

            Runtime: O(m*3^k)
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

    def get_response(self, guess, candidate):
        """
            Get the response using the precomputed map

            Runtime: O(1)
        """
        return self.RESPONSES[self.WORD_IDX["guess"][guess]][self.WORD_IDX["target"][candidate]]

    def adjust_candidates(self, guess, response, candidates):
        """
            Update distributions with the latest available candidates

            Runtime: O(mnk) with a shrinking n
        """
        new_candidates = super().adjust_candidates(guess, response, candidates)
        self.distribution = self.get_distribution(new_candidates)

        return new_candidates

    @staticmethod
    def should_pick_from(words):
        """
            Should pick from the words if there is only one choice

            Runtime: O(1)
        """
        return len(words) == 1

    def print_initial_top_guesses(self, output_dir="output", output_name="top_scores"):
        return super().print_initial_top_guesses(output_dir, output_name + "_" + self.precompute)
