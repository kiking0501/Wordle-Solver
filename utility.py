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
