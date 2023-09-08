# reviews.py
class Review:
    def __init__(self, content, author, timestamp):
        try:
            if not content:
                raise ValueError("Review content cannot be empty")
            if not author:
                raise ValueError("Review author cannot be empty")
            if not timestamp:
                raise ValueError("Review timestamp cannot be empty")

            self.content = content
            self.author = author
            self.timestamp = timestamp
        except ValueError as e:
            # Handle the validation error here, such as logging it or raising a custom exception
            # For this simple example, we'll just print the error
            print(f"Error creating a review: {e}")
