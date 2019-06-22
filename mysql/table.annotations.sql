CREATE TABLE IF NOT EXISTS Annotations (
    Id BIGINT AUTO_INCREMENT PRIMARY KEY,
    StoryletId VARCHAR(50),
    PhotoOrder INT,
    PhotoFlickrId VARCHAR(50),
    AlbumId VARCHAR(50),
    StoryId VARCHAR(50),
    OriginalText TEXT,
    Text TEXT)