import os
import numpy as np
from utility import _bucket_count, _get_output_path


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


def interactive_play(wordle, player, with_target, first_guess=None):
    print("#" * 50)
    print("### Welcome to the Interactive Mode! ###")
    print("# Wordle Response Format- ", wordle.get_response_description())
    print("#" * 50)

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

    player.play(target=target, first_guess=first_guess, verbose=True)


def get_first_guess_performance(wordle, player, first_guess, verbose=True):
    """
        Use the input first guess word for all possible targets
            and get statistics about the number of guesses
    """
    try:
        from tqdm import tqdm
    except ImportError:
        print("Download tqdm to display progress bar in command line")

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

    if verbose:
        print("#" * 50)
        print("### Checking performance of '{}' as a first guess for all possible targets... ###".format(first_guess))
        print("#" * 50)

    all_guesses = []
    for target in tqdm(wordle.words):
        num_guess, trace = player.play(target=target, first_guess=first_guess, verbose=False)
        all_guesses.append(num_guess)
    msg = _get_stats(all_guesses)
    if verbose:
        print(msg)
    return msg


def check_topK_guesses_performance(
        wordle, player, topK, output_dir="output", output_name="top_guesses_performance"):
    """
        Iterate the top-K first guess word for all possible targets
            and get statistics about the number of guesses for each first guess
    """
    print("#" * 50)
    print("### Getting scores of all words at first guess ... ###")
    top_guesses = player.print_initial_top_guesses()
    print("#" * 50)
    print("### Checking performance of the topK words as a first guess for all possible targets...")
    print("#" * 50)

    obj_name = getattr(player, "precompute", "") + type(player).__name__
    output_path = _get_output_path(output_dir, output_name, obj_name) + ".txt"
    if not os.path.exists(output_path):
        open(output_path, "w").close()
        print("{} created.".format(output_path))

    for top_id in range(topK):
        first_guess, first_score = top_guesses[top_id]
        msg = "({}) Guess: {} (Score: {:.2f}), {}".format(
            top_id, first_guess, first_score, get_first_guess_performance(wordle, player, first_guess), verbose=False)
        print(msg)
        with open(output_path, "a") as f:
            f.write(msg + "\n")


def save_trace(wordle, player, first_guess_list, output_dir="output", output_name="traces"):
    """
        Saving the traces for each possible target and for each first guess in the input list
            each line stores "idx(guess),encode(response)" at each step, tab-separated
            the end of trace is indicated by "idx(target)"
    """
    try:
        from tqdm import tqdm
    except ImportError:
        print("Download tqdm to display progress bar in command line")

    obj_name = getattr(player, "precompute", "") + type(player).__name__
    output_path = _get_output_path(output_dir, output_name, obj_name) + ".txt"
    if not os.path.exists(output_path):
        open(output_path, "w").close()
        print("{} created.".format(output_path))

    word_idx = {word: idx for idx, word in enumerate(player.guess_list)}
    for first_guess in first_guess_list:
        print("first guess: ", first_guess)
        for target in tqdm(wordle.words):
            num_guess, trace = player.play(target=target, first_guess=first_guess, verbose=False)
            msg = "\t".join([
                "{},{}".format(word_idx[guess], wordle.encode_response(response))
                for guess, response in trace[:-1]] + [str(word_idx[target])])
            with open(output_path, "a") as f:
                f.write(msg + "\n")


if __name__ == "__main__":
    from Wordle import Wordle
    from HeuristicWordlePlayer import HeuristicWordlePlayer
    from MaxInformationGainWordlePlayer import MaxInformationGainWordlePlayer
    import argparse

    # solver
    parser = argparse.ArgumentParser(
        description='Wordle Solvers in Python!')

    parser.add_argument(
        "--solver", choices=["heuristic", "small-mig", "large-mig"], default="heuristic",
        help="Specify the solver to use (heuristic/small-mig/large-mig)")
    parser.add_argument(
        "--first_guess", default="raise",
        help="Specify a fixed word for the solver to use in the first guess, default 'raise'")

    subparsers = parser.add_subparsers(help="usages: interactive/analysis", dest='mode')

    # interactive
    parser_i = subparsers.add_parser("interactive", help="Play Interactively")
    parser_i.add_argument(
        "--with_target", action="store_true",
        help="If specified, set a target word for the solver to guess")

    # analysis
    parser_a = subparsers.add_parser("analysis", help="Analyse First Guess Performance")

    parser_a.add_argument(
        "--topK", default=None,
        help="Check the performance of the top-K words with the highest internal solver score")
    parser_a.add_argument(
        "--save_trace", nargs="+", default=None)

    args = parser.parse_args()

    ####################################################
    words_size = "small"
    wordle = Wordle(5, get_words(words_size))

    if args.solver == "heuristic":
        print("\n[Loading the Heuristic Player ({} word list)]\n".format(words_size))
        player = HeuristicWordlePlayer(wordle, guess_list=get_words(words_size))

    elif args.solver == "small-mig":
        print("\n[Loading the Max Information Gain Player]\n")
        player = MaxInformationGainWordlePlayer(wordle, guess_list=get_words("small"), precompute="small")

    elif args.solver == "large-mig":
        print("\n[Loading the Max Information Gain Player (large word list)]\n")
        player = MaxInformationGainWordlePlayer(wordle, guess_list=get_words("large"), precompute="large")

    if args.mode == "interactive":
        interactive_play(wordle, player, with_target=args.with_target, first_guess=args.first_guess)

    elif args.mode == "analysis":
        if args.topK:
            check_topK_guesses_performance(wordle, player, topK=int(args.topK))
        elif args.save_trace:
            save_trace(wordle, player, first_guess_list=args.save_trace)
        elif args.first_guess:
            get_first_guess_performance(wordle, player, first_guess=args.first_guess)
