class Dataset:
    def __init__(self, hyperparam_dict):
        self.hyperparam_dict = hyperparam_dict
        pass

    def gen(self, path_to_put_dataset_folder):
        raise Exception("not implemented")


class RandDataset(Dataset):
    pass

    def gen(self, path_to_put_dataset_folder):
        import random
        pass