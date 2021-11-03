hyperparam_space = {
    "window_size_in_bytes_to_gen": [32, 64],
    "rand_seed_used_in_all_dataset_generation": 1234,
    "executable_used": ["A.dll", "B.exe"],
    "max_number_of_samples_per_class": [1, 2]
}

dataset_root_dir = "/Volumes/ssd4work/828w_project_dataset"

def get_dataset_name(hyperparam_dict):
    s = f"{hyperparam_dict['window_size_in_bytes_to_gen']}" \
        f"_{hyperparam_dict['rand_seed_used_in_all_dataset_generation']}" \
        f"_{hyperparam_dict['executable_used']}" \
        f"_{hyperparam_dict['max_number_of_samples_per_class']}"

    return s

def parse_dataset_name(s):
    d = {}
    d['window_size_in_bytes_to_gen'], \
    d['rand_seed_used_in_all_dataset_generation'], \
    d['executable_used'], \
    d['max_number_of_samples_per_class'] \
        = s.split('_')

    return d

def get_all_hyperparam_dicts():
    from itertools import product
    prod_ks = []
    prod_vs = []

    base_dict = {}
    for k, v in hyperparam_space.items():
        if type(v) is list:
            prod_ks.append(k)
            prod_vs.append(v)
        else:
            base_dict[k] = v

    dicts = []
    for vs in product(*prod_vs):
        now_dict = base_dict.copy()
        for idx in range(len(prod_ks)):
            now_dict[prod_ks[idx]] = vs[idx]
        dicts.append(now_dict)

    return dicts


if __name__ == "__main__":
    for d in get_all_hyperparam_dicts():
        print('---')
        print(d)
        print(get_dataset_name(d))
        print(parse_dataset_name(get_dataset_name(d)))

