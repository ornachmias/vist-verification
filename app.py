import logHandler
from dataLoader import DataLoader
from databaseAccess import DatabaseAccess
from vistDataset import VistDataset


def main():
    logHandler.initialize()
    data_loader = DataLoader(root_path="./data")
    data_loader.initialize()
    vist_dataset = VistDataset(root_path="./data")
    vist_dataset.initialize()
    database_access = DatabaseAccess()
    database_access.initialize(vist_dataset)


if __name__ == '__main__':
    main()
