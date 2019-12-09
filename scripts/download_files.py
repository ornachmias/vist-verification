from google_drive_downloader import GoogleDriveDownloader as gdd

file_id = "0ByQS_kT8kViSWmtRa1lMcG1EaHc"
dest_path = "./val_images.tar.gz"

print("Starting download file_id={} to dest_path={}".format(file_id, dest_path))
gdd.download_file_from_google_drive(file_id=file_id, dest_path=dest_path, unzip=False, showsize=True)
print("Finished download file_id={} to dest_path={}".format(file_id, dest_path))

file_id = "0ByQS_kT8kViSTHJ0cGxSVW1SRFk"
dest_path = "./test_images.tar.gz"

print("Starting download file_id={} to dest_path={}".format(file_id, dest_path))
gdd.download_file_from_google_drive(file_id=file_id, dest_path=dest_path, unzip=False, showsize=True)
print("Finished download file_id={} to dest_path={}".format(file_id, dest_path))