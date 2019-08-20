CREATE TABLE IF NOT EXISTS UsersResponses (
    Id BIGINT AUTO_INCREMENT PRIMARY KEY,
    QuestionId VARCHAR(50),
    PhotoOrder INT,
    PhotoFlickrId VARCHAR(50),
    StoryletId VARCHAR(50),
    StoryId VARCHAR(50))