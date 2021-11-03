from config.dataset_hyperparam import  \
    get_dataset_name, \
    get_all_hyperparam_dicts, \
    parse_dataset_name



if __name__ == "__main__":
    for d in get_all_hyperparam_dicts():
        print('---')
        print(d)
        print(get_dataset_name(d))
        print(parse_dataset_name(get_dataset_name(d)))