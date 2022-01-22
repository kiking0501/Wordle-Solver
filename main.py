import numpy as np
from utility import _bucket_count, _get_output_path
from Wordle import Wordle
from BaseWordlePlayer import BaseWordlePlayer
from HeuristicWordlePlayer import HeuristicWordlePlayer
from MaxInformationGainWordlePlayer import MaxInformationGainWordlePlayer


def get_words(size="small"):
    """
        small word list: 2315
        extra word list: 12972
    """
    if size not in ("small", "large"):
        raise ValueError("choose from size 'small' / 'large")

    words = []
    with open("data/small.txt") as f:
        for line in f.readlines():
            word = line.strip()
            words.append(word)

    if size == "small":
        return words
    elif size == "large":
        word_set = set(words)
        with open("data/large.txt") as f:
            for line in f.readlines():
                extra_word = line.strip()
                if extra_word not in word_set:
                    words.append(extra_word)
        return words


def interactive_play(wordle, player, with_target):
    target = None

    if with_target:
        while target is None:
            input_target = input(
                "## Input Your Own Target? (<{}-letter word>/empty):\n".format(wordle.k))
            if input_target:
                if input_target in wordle.words:
                    target = input_target
            else:
                print("#### Generating Target... ####")
                target = wordle.generate_target()

    player.play(target, verbose=True)


def check_top_guesses_performance(
        wordle, player, topK, output_dir="output", output_name="top_guesses_performance"):

    from tqdm import tqdm

    def _get_stats(all_guesses):
        """
            Print message for the statistics of a list of guesses
        """

        guess_dict = _bucket_count(all_guesses)
        msg = "Mean: {:.3f}, Min: {}, Max: {}".format(
            np.mean(all_guesses), min(guess_dict), max(guess_dict))
        msg += ", Count of Guesses:"
        for i in range(min(guess_dict), max(guess_dict) + 1):
            msg += " [{}] {}".format(i, guess_dict.get(i, 0))
        return msg

    top_guesses = player.print_initial_top_guesses()

    print("\n## Start Running...")
    topK = 10
    prints = []
    for top_id in range(topK):
        first_guess, first_score = top_guesses[top_id]
        all_guesses = []

        for target in tqdm(wordle.words):
            num_guess = player.play(target=target, first_guess=first_guess, verbose=False)
            all_guesses.append(num_guess)

        msg = "({}) Guess: {} (Score: {:.2f}), {}".format(
            top_id, first_guess, first_score, _get_stats(all_guesses))
        print(msg)
        prints.append(msg)

    obj_name = getattr(player, "precompute", "") + type(player).__name__
    output_path = _get_output_path(output_dir, output_name, obj_name) + ".txt"
    with open(output_path, "w") as f:
        f.writelines("\n".join(prints))
        print("{} saved.".format(f.name))


if __name__ == "__main__":

    INTERACTIVE = True
    WITH_TARGET = True
    TOPK = 10

    wordle = Wordle(5, get_words("small"))
    # player = BaseWordlePlayer(wordle, guess_list=get_words("small"))
    player = HeuristicWordlePlayer(wordle, guess_list=get_words("small"))
    # player = MaxInformationGainWordlePlayer(wordle, guess_list=get_words("small"), precompute="small")

    if INTERACTIVE:
        interactive_play(wordle, player, with_target=WITH_TARGET)

    else:
        check_top_guesses_performance(wordle, player, topK=TOPK)
