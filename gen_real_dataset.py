from config.dataset_hyperparam import  \
    get_dataset_name, \
    get_all_hyperparam_dicts, \
    parse_dataset_name, \
    dataset_root_dir, \
    exectutable_dir

from os.path import join, exists
import os
import shutil


from objdump_to_memory_dump_with_call_instruction_indexed import MemoryDump


def write_dataset(
        dataset_root_dir,
        memory_bytes,
        idx_set,
        class_name,
        sample_name_prefix,
        validation_set_size_in_percentage,
        window_radius,
        set_name,
):
    validation_set_end = int(validation_set_size_in_percentage*len(idx_set))

    idx_list = list(idx_set)
    now_idx_set = idx_list[:validation_set_end]
    count = 0
    class_dir = join(dataset_root_dir, "ML_format", "validation_set", class_name)
    os.makedirs(class_dir, exist_ok=True)
    for idx in now_idx_set:
        sample = bytes(memory_bytes[idx - window_radius:idx + window_radius])
        with open(join(class_dir, sample_name_prefix + str(count) + '.hxv'), 'wb') as f:
            f.write(sample)
        count += 1
    os.makedirs(join(dataset_root_dir, 'meta_info', 'validation_set'), exist_ok=True)
    with open(join(dataset_root_dir, 'meta_info', 'validation_set', set_name), 'w') as f:
        for idx in now_idx_set:
            f.write(str(idx))
            f.write(' ')

    now_idx_set = idx_list[validation_set_end:]
    count = 0
    class_dir = join(dataset_root_dir, "ML_format", "traintest_set", class_name)
    os.makedirs(class_dir, exist_ok=True)
    for idx in now_idx_set:
        sample = bytes(memory_bytes[idx - window_radius:idx + window_radius])
        with open(join(class_dir, sample_name_prefix + str(count) + '.hxv'), 'wb') as f:
            f.write(sample)
        count += 1
    os.makedirs(join(dataset_root_dir, 'meta_info', 'traintest_set'), exist_ok=True)
    with open(join(dataset_root_dir, 'meta_info', 'traintest_set', set_name), 'w') as f:
        for idx in now_idx_set:
            f.write(str(idx))
            f.write(' ')

    memory_bytes_file = join(dataset_root_dir, 'meta_info', 'memory_bytes')
    if not exists(memory_bytes_file):
        with open(memory_bytes_file, 'wb') as f:
            f.write(bytes(memory_bytes))




def gen_real_dataset(hyperparam_dict, dataset_dir, exectutable_dir, force=False):
    assert hyperparam_dict["window_size_in_bytes_to_gen"]%2 == 0

    import random
    from binascii import hexlify

    random.seed(hyperparam_dict["rand_seed_used_in_all_dataset_generation"])
    print("Gonna generate real dataset with config", hyperparam_dict, "at", dataset_dir)

    if exists(dataset_dir):
        if force:
            shutil.rmtree(dataset_dir)
        else:
            print(dataset_dir+" already exists so I will skip generating it!")
            return

    md = MemoryDump(join(exectutable_dir, hyperparam_dict["executable_used"]))
    print(f"{hyperparam_dict['executable_used']} info:")
    print("len(memory_bytes)", len(md.memory_bytes))
    print("len(retaddr_index)", len(md.retaddr_index))
    print("len(symbol_index)", len(md.symbol_index))


    size_of_retaddr_index = min(hyperparam_dict["max_number_of_samples_per_class"], len(md.retaddr_index))
    picked_ret_addr_index_set = set(random.sample(md.retaddr_index, k=size_of_retaddr_index))

    size_of_symbol_index = min(size_of_retaddr_index//2, len(md.symbol_index))
    size_of_non_symbo_non_retaddr_index = min(hyperparam_dict["max_number_of_samples_per_class"]-size_of_symbol_index, len(md.memory_bytes)-size_of_symbol_index)
    picked_symbol_index_set = set(random.sample(md.symbol_index, k=size_of_symbol_index))

    picked_non_symbo_non_retaddr_index_set = set()
    while len(picked_non_symbo_non_retaddr_index_set) < size_of_non_symbo_non_retaddr_index:
        now_idx = random.randint(0, len(md.memory_bytes)-1)
        if now_idx not in picked_ret_addr_index_set \
            and now_idx not in picked_symbol_index_set:
            picked_non_symbo_non_retaddr_index_set.add(now_idx)

    print(len(picked_ret_addr_index_set), picked_ret_addr_index_set)
    print(len(picked_symbol_index_set), picked_symbol_index_set)
    print(len(picked_non_symbo_non_retaddr_index_set), picked_non_symbo_non_retaddr_index_set)


    window_radius = hyperparam_dict["window_size_in_bytes_to_gen"]//2


    write_dataset(
        dataset_root_dir=dataset_dir,
        memory_bytes=md.memory_bytes,
        idx_set=picked_ret_addr_index_set,
        class_name="ret addr",
        sample_name_prefix="picked_ret_addr_index_set ",
        validation_set_size_in_percentage=hyperparam_dict['validation_set_size_in_percentage'],
        window_radius=window_radius,
        set_name='picked_ret_addr_index_set'
    )

    write_dataset(
        dataset_root_dir=dataset_dir,
        memory_bytes=md.memory_bytes,
        idx_set=picked_symbol_index_set,
        class_name="not ret addr",
        sample_name_prefix="picked_symbol_index_set ",
        validation_set_size_in_percentage=hyperparam_dict['validation_set_size_in_percentage'],
        window_radius=window_radius,
        set_name='picked_symbol_index_set'
    )

    write_dataset(
        dataset_root_dir=dataset_dir,
        memory_bytes=md.memory_bytes,
        idx_set=picked_non_symbo_non_retaddr_index_set,
        class_name="not ret addr",
        sample_name_prefix="picked_non_symbo_non_retaddr_index_set ",
        validation_set_size_in_percentage=hyperparam_dict['validation_set_size_in_percentage'],
        window_radius=window_radius,
        set_name='picked_non_symbo_non_retaddr_index_set'
    )

if __name__ == "__main__":
    for d in get_all_hyperparam_dicts():
        dataset_name = get_dataset_name(d)
        dataset_dir = join(dataset_root_dir, "real", dataset_name)
        gen_real_dataset(d, dataset_dir, exectutable_dir, force=True)
