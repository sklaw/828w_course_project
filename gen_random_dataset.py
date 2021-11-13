from config.dataset_hyperparam import  \
    get_dataset_name, \
    get_all_hyperparam_dicts, \
    parse_dataset_name, \
    dataset_root_dir

from os.path import join, exists
import os
import shutil


def gen_random_dataset(hyperparam_dict, dataset_dir, force=False):
    assert hyperparam_dict["window_size_in_bytes_to_gen"]%2 == 0

    import random
    from binascii import hexlify

    random.seed(hyperparam_dict["rand_seed_used_in_all_dataset_generation"])
    print("Gonna generate random dataset with config", hyperparam_dict, "at", dataset_dir)

    if exists(dataset_dir):
        if force:
            shutil.rmtree(dataset_dir)
        else:
            print(dataset_dir+" already exists so I will skip generating it!")
            return

    for label in ["ret addr", "not ret addr"]:
        class_dir = join(dataset_dir, label)
        os.makedirs(class_dir)
        for i in range(hyperparam_dict["max_number_of_samples_per_class"]):
            n_bytes = hyperparam_dict["window_size_in_bytes_to_gen"]
            sample = random.getrandbits(8*n_bytes).to_bytes(n_bytes, "big")
            #print(hexlify(sample))
            with open(join(class_dir, str(i)+'.hxv'), 'wb') as f:
                f.write(sample)


if __name__ == "__main__":
    for d in get_all_hyperparam_dicts():
        d["executable_used"] = "fake" + d["executable_used"]
        dataset_name = get_dataset_name(d)
        dataset_dir = join(dataset_root_dir, "random", dataset_name)
        gen_random_dataset(d, dataset_dir, force=True)
