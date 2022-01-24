import os


def _bucket_count(li):
    """
        utility function:
            get bucket counts given a list

        Return:
            {x: count} for each x in the list
    """
    bucket = {}
    for x in li:
        if x not in bucket:
            bucket[x] = 0
        bucket[x] += 1
    return bucket


def _get_output_path(output_dir, output_name, suffix):
    """
        utility function:
            get output path
    """
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_path = os.path.join(
        output_dir,
        "{}_{}".format(output_name, suffix)
    )
    return output_path


def _txt2dict(path):
    import collections.abc

    def merge_dict(d1, d2):
        for k, v in d2.items():
            if isinstance(v, collections.abc.Mapping):
                d1[k] = merge_dict(d1.get(k, {}), v)
            else:
                d1[k] = v
        return d1

    def create_nested_dict(data):
        if len(data) > 1:
            head, tail = data[0], data[1:]
            return {head: create_nested_dict(tail)}
        else:
            return {data[0]: {}}
    d = {}
    with open(path) as f:
        for line in f.readlines():
            splits = line.strip().split("\t")
            splits_d = create_nested_dict(splits)
            merge_dict(d, splits_d)
    return d


if __name__ == "__main__":
    import json
    for name in ("HeuristicWordlePlayer", "smallMaxInformationGainWordlePlayer"):
        d = _txt2dict("output/traces_{}.txt".format(name))
        with open("output/traces_{}.json".format(name), "w") as f:
            json.dump(d, f)
            print("{} saved.".format(f.name))
