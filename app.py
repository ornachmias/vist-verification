import logHandler
from dataLoader import DataLoader


def main():
    logHandler.initialize()
    data_loader = DataLoader(root_path='./data')
    data_loader.download_images()


if __name__ == '__main__':
    main()
