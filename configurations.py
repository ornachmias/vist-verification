# post_hits script parameters
aws_access_key_id = "XXX"
aws_secret_access_key = "XXX"
api_url = "XXX"

# HTTP application parameters
root_data = "./data"
samples = 150
number_of_questions = 5
show_original_description = True
get_user_description = False

# HTTPS parameters
certificate_path = ""
private_key_path = ""

# Submit limitation
max_story_submit = 3
story_ids = None
use_obvious_stories = True

# Obvious sequences image Ids
test_sequence = {
    "id": "test",
    "image_ids": ["00000000001", "00000000002", "00000000003", "00000000004", "00000000005"],
    "story": "I started from a clean table and added two cards. After I saw that went "
             "well I continued stacking more cards."
}

obvious_sequences = [
    {
        "id": "obvious1",
        "image_ids": ["00000000006", "00000000007", "00000000008", "00000000009", "00000000010"],
        "story": "The man woke up. He first brushed his teeth, then got his shirt on, drank some juice, "
        "and put on his jacket before leaving."
    },
    {
        "id": "obvious2",
        "image_ids": ["00000000011", "00000000012", "00000000013", "00000000014", "00000000015"],
        "story": "The man took out a pill. The pill made him happy. The pill "
                 "caused him to see himself as a puppet. In his new form, he went dancing."
    },
    {
        "id": "obvious3",
        "image_ids": ["00000000016", "00000000017", "00000000018", "00000000019", "00000000020"],
        "story": "A girl was standing in line to buy a train ticket. She bought the ticket and went to the dock. "
                 "On the dock she waited until the train arrived."
    }
]

invalid_assignment_id = "ASSIGNMENT_ID_NOT_AVAILABLE"
